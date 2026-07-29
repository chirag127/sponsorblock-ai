"""This module is used to provide the functionality of the sponsor block api"""

import os
import random
import subprocess

import pandas
import requests
from bs4 import BeautifulSoup

from config import ua
from f import (ALL_SB_ACTION_TYPES, ALL_SB_CAT, SB_HOST, SB_HOST_1,
               WORKING_DIRECTORY, append_to_file, color, end_of_video, execute,
               get_total_segment_time, id_generator,
               print_status_and_text_from_response, random_choice,
               user_ids_from_segment_type,
               wait_for_time_between_1_and_specified_time,
               write_video_id_in_cache)
from reques import ModelResponse, get_url, get_url_with_retry, post_url


def latest_version_of_sponsor_block():
    """get the latest version of the sponsor block"""
    try:
        url = (
            "https://chrome.google.com/webstore/detail/"
            + "sponsorblock-for-youtube/mnjggcdmjocbbbhaepdhchncahnbgone"
        )
        page = get_url_with_retry(url)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup.find("span", attrs={"class": "C-b-p-D-Xe h-C-b-p-D-md"}).text
    except Exception as error:  # pylint: disable=broad-except
        print(error)


try:
    user_agent = latest_version_of_sponsor_block()

    user_agent = f"mnjggcdmjocbbbhaepdhchncahnbgone/v{user_agent}"

except Exception as error:  # pylint: disable=broad-except
    print(error)

    user_agent = None

USER_AGENTS = [user_agent] if user_agent else ua

# sponsorblock.kavin.rocks - 🇩🇪 (main instance)
# sponsorblock.gleesh.net - 🇩🇪
# sb.theairplan.com - 🇺🇸

all_sb_api_hosts = [
    SB_HOST,
    SB_HOST_1,
    "https://sponsorblock.hankmccord.dev" "https://sponsorblock.kavin.rocks",
    "https://sponsorblock.gleesh.net",
    "https://sb.theairplan.com",
    "https://sponsorblock-proxy.lucashmsilva.com/",
]


def public_user_id_from_user_id(user_id):
    """returns the public user id from a private user id"""
    print(user_id)
    info = info_from_user_id(user_id)
    user_id = info["userID"]
    return user_id


def return_url_to_post(
    video_id,
    start_of_segment=0,
    end_of_segment=0,
    category="intro",
    action_type="skip",
    user_id=None,
):
    """returns a url to post a segment to sponsor block server"""
    print(
        f"Making request for video id: {video_id} start {start_of_segment} "
        + f"end {end_of_segment} category: {category} action_type: {action_type}"  # pylint: disable=line-too-long
    )

    if user_id is None:
        user_id = id_generator()

    user_agent = random.choice(USER_AGENTS)

    return (
        "https://sponsor.ajay.app/api/skipSegments?videoID="
        + f"{video_id}&category={category}&startTime={start_of_segment}"
        + f"&endTime={end_of_segment}&userAgent={user_agent}&userID={user_id}&actionType={action_type}"
    )  # pylint: disable=line-too-long


def random_sb_host():
    """returns a random sb host"""
    list_of_5_sb_hosts = [SB_HOST, SB_HOST_1]
    return random_choice(list_of_5_sb_hosts)


def post_vote(uuid, vote_type="d", user_id=None):
    """post a vote for a uuid"""
    print(
        f"Posting vote for uuid: {uuid} with vote type: "
        + f"{vote_type} with user_id: {user_id}"
    )

    if user_id is None:
        user_id = "GH5VE0luuZmGYyBqHkUDcbN26oVeJsQEJkI8"

    print(f"Voting on {uuid}")
    if vote_type == "l":
        type_ = 1
    elif vote_type == "d":
        type_ = 0
    elif vote_type == "u":
        type_ = 20
    else:
        print("Invalid vote type")

    url = (
        f"{SB_HOST}/api/voteOnSponsorTime?"
        + f"UUID={uuid}&userID={user_id}&type={type_}"
    )

    response = post_url(url)
    print_status_and_text_from_response(response)


def uuids_from_sbb(identifier, identifier_type="video"):
    """scraps the uuids from the sponsor block browser url
    and returns them"""
    if identifier_type == "video":
        url = f"https://sb.ltn.fi/video/{identifier}"
    elif identifier_type == "user_name":
        url = f"https://sb.ltn.fi/username/{identifier}"
    elif identifier_type == "user_id":
        url = f"https://sb.ltn.fi/userid/{identifier}"
    elif identifier_type == "uuid":
        url = f"https://sb.ltn.fi/uuid/{identifier}"
    else:
        print(f"Invalid identifier type: {identifier_type}")
        return None

    page = get_url_with_retry(url)
    soup = BeautifulSoup(page.content, "html.parser")
    uuids_r = soup.find_all("textarea", attrs={"class": "form-control", "name": "UUID"})
    return text_from_raw_uuids(uuids_r)


def text_from_raw_uuids(uuids_r):
    """returns a list of uuids from the raw html"""
    uuids = []
    for uuid in uuids_r:
        uuid = uuid.get_text()
        uuids.append(uuid)

    return uuids


def return_video_ids_from_sbb(url):
    """scraps the video ids from the sponsor block browser url and returns them"""
    page = get_url_with_retry(url)
    soup = BeautifulSoup(page.content, "html.parser")
    video_ids_r = soup.find_all(
        "a", attrs={"href": lambda x: x and x.startswith("/video/")}
    )
    return text_from_raw_uuids(video_ids_r)


def segments_stats_for_video_id(
    video_id, sb_host=SB_HOST, segment_type="skip", retry=3
):
    """get the segments for a video id with a given segment type (skip or search)"""

    segment_type = "search" if sb_host in [SB_HOST, SB_HOST_1] else "skip"
    if segment_type == "search":
        response = search_segments_stats_for_video_id(video_id, sb_host)

    elif segment_type == "skip":
        response = skip_segments_stats_for_video_id(video_id, sb_host)
    if response == "error" and retry > 0:
        response = segments_stats_for_video_id(
            video_id, sb_host, segment_type, retry - 1
        )

    return response


def segments_response_from_video_id(
    video_id, sb_host=SB_HOST, segment_type="search", retry=3
):
    """get the segments for a video id with a given segment type (skip or search)"""
    if segment_type == "skip":
        url = url_from_api(f"{sb_host}/api/skipSegments", video_id)
    elif segment_type == "search":
        url = url_from_api(f"{sb_host}/api/searchSegments", video_id)
    response = get_url(url)
    if response.ok or response.status_code == 404:
        return response

    print_status_and_text_from_response(response)
    print(f"Error getting segments for video id {video_id}")
    wait_for_time_between_1_and_specified_time()

    return ModelResponse([], 404)


def skip_segments_stats_for_video_id(video_id, sb_host=SB_HOST):
    """get the skip segments for a video id"""
    print(f"Getting skip segments for video {video_id}")

    categories_found = []
    action_types_found = []
    i = 0
    j = 0

    response = segments_response_from_video_id(video_id, sb_host, "skip")

    if response.ok:
        try:
            for segment in response.json():
                categories_found.append(segment["category"])
                action_types_found.append(segment["actionType"])
                categories_found = list(set(categories_found))
                action_types_found = list(set(action_types_found))
                i += 1
                if segment["category"] == "sponsor":
                    j += 1
        except requests.exceptions.JSONDecodeError as error:
            print(error)
            print(f"Error decoding json for video id {video_id}")
        except Exception as error:
            print(f"Error getting skip segments for video id {video_id}")
            print(error)

    elif response.status_code == 404:
        print(f"No skip segments found for video: {video_id}")
    else:
        print_status_and_text_from_response(response)
        return "error"

    return categories_found, action_types_found, i, j


def search_segments_stats_for_video_id(video_id, sb_host=SB_HOST):
    """get the search segments for a video id"""
    response = segments_response_from_video_id(video_id, sb_host, "search")

    action_types_found = []
    i = 0
    j = 0
    categories_found = []
    if response.ok:
        response_json = response.json()

        segments = response_json["segments"]

        for segment in segments:
            categories_found.append(segment["category"])
            action_types_found.append(segment["actionType"])
            categories_found = list(set(categories_found))
            action_types_found = list(set(action_types_found))
            i += 1
            if segment["category"] == "sponsor":
                j += 1

    elif response.status_code == 404:
        print(f"No skip segments found for video: {video_id}")
    else:
        print_status_and_text_from_response(response)
        return "error"

    return categories_found, action_types_found, i, j


def url_from_api(url, video_id):
    """returns the url with the video id in the api url"""
    url = f"{url}?videoID={video_id}&categories={ALL_SB_CAT}&actionTypes={ALL_SB_ACTION_TYPES}"
    return url


def make_request(
    video_id,
    segment_type,
    submit_segments,
    user_ids,
    user_id,
    sb_host=SB_HOST,
    duration=0,
    data_frame_of_uuids_and_user_ids=None,
    retry=True,
    retry_time=2,
):  # sourcery skip: low-code-quality
    """make a post request to submit the segment to sponsor block api"""
    video_duration = end_of_video(duration)

    if user_ids is None and user_id is None:
        user_id = id_generator()
    elif user_id is None:
        user_id = random_choice(user_ids)
        if data_frame_of_uuids_and_user_ids is not None:
            print(f"user_id: {user_id}")
            # public_user_id = public_user_id_from_user_id(user_id)
            # uuids = uuids_from_sbb(public_user_id,"user_id")

    if submit_segments is None:
        submit_segments = []

    user_agent = random_choice(USER_AGENTS)

    data = {
        "videoID": video_id,
        "userID": user_id,
        "userAgent": user_agent,
        "segments": submit_segments,
        "videoDuration": video_duration,
    }

    total_time = get_total_segment_time(submit_segments)

    def check_if_total_time_is_too_high(total_time):
        if total_time > 0.6 * video_duration:
            print(
                f"Total time of segments is {total_time}"
                + f" which is too high for video {video_id}"
            )
            return True
        return False
        # if total_time > 0.6 * video_duration:
        #     print(f"Total time of segments is {total_time} which is too high for video {video_id}")
        #     return True
        # return False

    while check_if_total_time_is_too_high(total_time):
        print("removing a segment")
        submit_segments = submit_segments[:-1]
        total_time = get_total_segment_time(submit_segments)

    if len(submit_segments) == 0:
        print(f"No segments to submit for video {video_id}")
        write_video_id_in_cache(video_id, segment_type)
        return

    url = f"{sb_host}/api/skipSegments"

    response = post_url(url, json=data)

    if response.ok:

        print(
            f"Successfully submitted {len(submit_segments)} segments for video {video_id}"
        )
        print(f"User ID: \n{user_id}\n")
        write_video_id_in_cache(video_id, segment_type)
    else:

        print(f"Failed to submit segments for video {video_id}")
        print_status_and_text_from_response(response)
        print(data)

        if retry is False:
            print("no retry")
            return None

        if response.status_code == 409:

            # if len(submit_segments) == 1:
            print(f"Video {video_id} already submitted")
            write_video_id_in_cache(video_id, segment_type)
            return None
            # for segment in submit_segments:
            #     make_request(
            #         video_id=video_id,
            #         segment_type=segment_type,
            #         submit_segments=[segment],
            #         user_ids=user_ids,
            #         user_id=user_id,
            #         sb_host=sb_host,
            #         duration=duration,
            #         data_frame_of_uuids_and_user_ids=data_frame_of_uuids_and_user_ids,
            #         retry=False,
            #     )

        if response.status_code == 403 and "warning" in response.text:
            # retry with a new user id
            print(f"User ID {user_id} is warned")

            remove_warning_for_a_user_id(user_id)
            print("Retrying with a same user id...")

        elif (
            response.status_code == 403
            or response.status_code == 400
            and "someone is doing a targeted attack" not in response.text
        ):
            write_video_id_in_cache(video_id, segment_type)
            return None
        elif response.status_code == 403:

            # try to make the requests one by one
            for segment in submit_segments:
                make_request(
                    video_id=video_id,
                    segment_type=segment_type,
                    submit_segments=[segment],
                    user_ids=user_ids,
                    user_id=user_id,
                    sb_host=sb_host,
                    duration=duration,
                    data_frame_of_uuids_and_user_ids=data_frame_of_uuids_and_user_ids,
                    retry=False,
                )

            return None

        elif response.status_code == 400:
            print_status_and_text_from_response(response)
            print(f"{user_id} is being targeted")

            if user_ids is None:
                user_ids = user_ids_from_segment_type()

            user_id = None

        else:

            print("retrying...")
            wait_for_time_between_1_and_specified_time()
            sb_host = random_sb_host()

        if retry_time > 0:
            retry_time -= 1
            make_request(
                video_id=video_id,
                segment_type=segment_type,
                submit_segments=submit_segments,
                user_ids=user_ids,
                user_id=user_id,
                sb_host=sb_host,
                duration=duration,
                data_frame_of_uuids_and_user_ids=data_frame_of_uuids_and_user_ids,
                retry=retry,
                retry_time=retry_time,
            )
        else:
            with open(os.path.join(os.path.dirname(__file__), "errors.txt"), "a") as f:
                f.write(f"{video_id}\n")


def remove_warning_for_a_user_id(user_id, warnings="unknown", public_user_id="unknown"):
    """remove the warning for a user id"""
    append_to_file(
        "txt/warnings.txt",
        f"{user_id} has {warnings} warnings with public user id {public_user_id}\n",
    )

    url = "https://sponsor.ajay.app/api/warnUser"

    data = {"userID": user_id, "enabled": False}

    response = post_url(url, json=data)
    print(response.text)

    if response.ok:
        append_to_file(
            "txt/warnings.txt",
            f"""{user_id} has {warnings} warnings with
            public user id {public_user_id}
            and disabled""",
        )
    else:
        print(f"{color.RED}Failed to disable {user_id} {color.END}")
        print(response.text)
        wait_for_time_between_1_and_specified_time()
        remove_warning_for_a_user_id(user_id, warnings, public_user_id)


def post_view(uuid, user_id=None, sb_host=SB_HOST):
    """post a view to sponsor block api"""
    # convert uuid from hex to decimal
    decimal_uuid = int(uuid, 16)

    last_digit = decimal_uuid % 10

    probablity_of_posting_view = last_digit / 10

    if random.random() < probablity_of_posting_view:

        url = f"{SB_HOST}/api/viewedVideoSponsorTime?UUID={uuid}"

        response = post_url(url)

        print_status_and_text_from_response(response)

        if response.ok:
            print(f"Successfully posted view for video {uuid}")
            print(f"User ID: \n{user_id}\n")
        else:
            post_view(uuid, user_id=user_id, sb_host=sb_host)

    else:
        print(
            f"Not posting view for video {uuid} with probability {probablity_of_posting_view}"
        )


def info_from_user_id(user_id):
    """get the info from a user_id"""
    response = get_url(f"{SB_HOST}/api/userInfo?userID={user_id}")

    if response.ok:
        return response.json()
    print_status_and_text_from_response(response)
    print("retrying...")
    wait_for_time_between_1_and_specified_time()
    return info_from_user_id(user_id)


def set_user_name(user_id, user_name=None):
    """set the user name for a user_id"""
    if user_name is None:
        info = info_from_user_id(user_id)
        user_name = info["userID"]

    # url = f"{SB_HOST}/api/setUsername?userID={user_id}"
    url = f"{SB_HOST}/api/setUsername?userID={user_id}&username={user_name}"

    response = post_url(url)
    print_status_and_text_from_response(response)
    if response.ok:
        print(f"Successfully set username for user {user_id} to {user_name}")
    else:
        print(f"Failed to set username for user {user_id} to {user_name}")
        print_status_and_text_from_response(response)
        wait_for_time_between_1_and_specified_time()
        print("retrying...")
        set_user_name(user_id, user_name)


# Convert format of search  segment to the format of the skip segments
def convert_search_segment_to_skip_segment(search_segment):
    """convert the format of the search segment to the format of the skip segment"""
    segments = search_segment["segments"]
    skip_segments = []
    for segment in segments:
        shadow_hidden = segment["shadowHidden"]
        user_id = segment["userID"]
        votes = segment["votes"]
        if (
            shadow_hidden
            and user_id
            == "a41d853c7328a86f8d712f910c4ef77f6c7a9e467f349781b1a7d405c37b681b"
            and votes > -1
        ):
            skip_segment = {
                "segment": [segment["startTime"], segment["endTime"]],
                "UUID": segment["UUID"],
                "category": segment["category"],
                "videoDuration": 60,
                "actionType": segment["actionType"],
                "userID": segment["userID"],
                "locked": segment["locked"],
                "votes": votes,
                "description": "",
            }

            skip_segments.append(skip_segment)
    return skip_segments


def uuid_list_from_data_frame(data_frame, user_id):
    """get the uuid list from a data frame for a userID"""
    return data_frame[data_frame["userID"] == user_id]["UUID"].tolist()


def get_data_frame_of_uuids_and_user_ids():
    """get the data frame of uuids and user_ids for a sponsorTimes"""
    current_directory = os.getcwd()
    os.chdir(WORKING_DIRECTORY)

    if not os.path.exists("sponsorTimes.csv"):
        url_of_datebase = "https://sponsor.ajay.app/database/sponsorTimes.csv"

        execute(["wget", url_of_datebase])

    required_columns = ["userID", "UUID"]

    chunk_size = 1000
    pd_chunks = pandas.read_csv(
        "sponsorTimes.csv",
        low_memory=False,
        chunksize=chunk_size,
        usecols=required_columns,
    )
    data_frame = pandas.concat(pd_chunks)
    try:

        # delete the database
        subprocess.call(["rm", "sponsorTimes.csv"])

        # delete all files which contains sponsorTimes in the filename
        subprocess.call(["find", ".", "-name", "sponsorTimes*", "-delete"])

    except Exception as error:  # pylint: disable=broad-except
        print(error)

    finally:
        os.chdir(current_directory)

    return data_frame


if __name__ == "__main__":
    print(segments_stats_for_video_id("6k2mF7X1WsU"))
