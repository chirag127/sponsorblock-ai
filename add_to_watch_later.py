import re
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List

from reques import post_url
from yt_api import info_from_video_id, video_ids_from_main_id

cookies = {
    "PREF": "f4=4000000&tz=Asia.Calcutta",
    "visitor": "1",
    "YSC": "Sx-S8Lckv3M",
    "VISITOR_INFO1_LIVE": "f5eqdpqpUWY",
    "CONSENT": "YES+",
    "SID": "WAj-ySzF48QibsNUPgAKCCzZPQ7FqAzaoR2WqhX3XFrJUOIdKasVOz-XyfdKGmyLiL2Y_w.",
    "__Secure-1PSID": "WAj-ySzF48QibsNUPgAKCCzZPQ7FqAzaoR2WqhX3XFrJUOIdxicy2J5h_enlE6dlaRpiLA.",
    "__Secure-3PSID": "WAj-ySzF48QibsNUPgAKCCzZPQ7FqAzaoR2WqhX3XFrJUOIdmsIjGEW_0smr1ur9AOt7mw.",
    "HSID": "ARW_Cbl87UMmsIBTw",
    "SSID": "A1JOS85Y3sG8BV8VD",
    "APISID": "Lcg0uzKW9A1devVM/Ay_6QrBBfxUFuw4pg",
    "SAPISID": "qnJdVdg1uwyQ1zQe/AijQV12obN_AS6PNy",
    "__Secure-1PAPISID": "qnJdVdg1uwyQ1zQe/AijQV12obN_AS6PNy",
    "__Secure-3PAPISID": "qnJdVdg1uwyQ1zQe/AijQV12obN_AS6PNy",
    "LOGIN_INFO": "AFmmF2swRgIhAJPN8Ww57S1hNUUGxC9MxJWohEJ88JKkdWtpYzxmjCQkAiEAuwW6WQtKyl5_ADkodMq53kp_prCqIklBz-oRRPFIAvU:QUQ3MjNmd2JQSWVHbGUwOE5QdXM0a0xCdkxJMlBwRjZWVEpXb1JydlZkcjM5U3NxUHlnVFAwbkdjbTh1OHExWlV3bnpaWHE3cUo5ZGxHYVA4YnNxSUpteE9NWGVMVXk1djdORjVsSGh2RmZMQmNXWEU2THJOYm5KNi1wV3RWbFdSNnNoY21YVTVxbE05UFoxaGUwcVFFMy1MLVIyR2dBbzVB",
    "SIDCC": "AP8dLtxp45QnB0yVpZDWe2GMx5KnevnqNvmMO-RB5Xg05dATVbFQSCMtDX7BjYCUswj-czdn",
    "__Secure-1PSIDCC": "AP8dLtw6Wg33KMzOnXz1fApCuaGUNrEok3yCltUe4gjxKoqwzyiyDvsycCgWxLko4Uia2MfYBQ",
    "__Secure-3PSIDCC": "AP8dLtytVro97N5npkXXOsRK0-cuLa4Fxuzaus05flcCHWJYpMYyRScX--xqzkq6Y-OYl7O1",
}

headers = {
    "authority": "www.youtube.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "SAPISIDHASH 1683016565_dc1586095d7930da0be00c60510cb55a75c2d43b",
    "content-type": "application/json",
    # 'cookie': 'PREF=f4=4000000&tz=Asia.Calcutta; visitor=1; YSC=Sx-S8Lckv3M; VISITOR_INFO1_LIVE=f5eqdpqpUWY; CONSENT=YES+; SID=WAj-ySzF48QibsNUPgAKCCzZPQ7FqAzaoR2WqhX3XFrJUOIdKasVOz-XyfdKGmyLiL2Y_w.; __Secure-1PSID=WAj-ySzF48QibsNUPgAKCCzZPQ7FqAzaoR2WqhX3XFrJUOIdxicy2J5h_enlE6dlaRpiLA.; __Secure-3PSID=WAj-ySzF48QibsNUPgAKCCzZPQ7FqAzaoR2WqhX3XFrJUOIdmsIjGEW_0smr1ur9AOt7mw.; HSID=ARW_Cbl87UMmsIBTw; SSID=A1JOS85Y3sG8BV8VD; APISID=Lcg0uzKW9A1devVM/Ay_6QrBBfxUFuw4pg; SAPISID=qnJdVdg1uwyQ1zQe/AijQV12obN_AS6PNy; __Secure-1PAPISID=qnJdVdg1uwyQ1zQe/AijQV12obN_AS6PNy; __Secure-3PAPISID=qnJdVdg1uwyQ1zQe/AijQV12obN_AS6PNy; LOGIN_INFO=AFmmF2swRgIhAJPN8Ww57S1hNUUGxC9MxJWohEJ88JKkdWtpYzxmjCQkAiEAuwW6WQtKyl5_ADkodMq53kp_prCqIklBz-oRRPFIAvU:QUQ3MjNmd2JQSWVHbGUwOE5QdXM0a0xCdkxJMlBwRjZWVEpXb1JydlZkcjM5U3NxUHlnVFAwbkdjbTh1OHExWlV3bnpaWHE3cUo5ZGxHYVA4YnNxSUpteE9NWGVMVXk1djdORjVsSGh2RmZMQmNXWEU2THJOYm5KNi1wV3RWbFdSNnNoY21YVTVxbE05UFoxaGUwcVFFMy1MLVIyR2dBbzVB; SIDCC=AP8dLtxp45QnB0yVpZDWe2GMx5KnevnqNvmMO-RB5Xg05dATVbFQSCMtDX7BjYCUswj-czdn; __Secure-1PSIDCC=AP8dLtw6Wg33KMzOnXz1fApCuaGUNrEok3yCltUe4gjxKoqwzyiyDvsycCgWxLko4Uia2MfYBQ; __Secure-3PSIDCC=AP8dLtytVro97N5npkXXOsRK0-cuLa4Fxuzaus05flcCHWJYpMYyRScX--xqzkq6Y-OYl7O1',
    "dnt": "1",
    "origin": "https://www.youtube.com",
    "referer": "https://www.youtube.com/playlist?list=WL",
    "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"112.0.5615.138"',
    "sec-ch-ua-full-version-list": '"Chromium";v="112.0.5615.138", "Google Chrome";v="112.0.5615.138", "Not:A-Brand";v="99.0.0.0"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"14.0.0"',
    "sec-ch-ua-wow64": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "same-origin",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "x-client-data": "CJW2yQEIprbJAQjBtskBCKmdygEIk4DLAQiUocsBCLGfzQEIhaDNAQi7oc0BCL2izQEI0aLNAQifpM0BCJOlzQEI16bNAQjYps0BCN2mzQEIuKnNAQiRqs0BCKWqzQE=",
    "x-goog-authuser": "1",
    "x-goog-visitor-id": "CgtmNWVxZHBxcFVXWSifksOiBg%3D%3D",
    "x-origin": "https://www.youtube.com",
    "x-youtube-bootstrap-logged-in": "true",
    "x-youtube-client-name": "1",
    "x-youtube-client-version": "2.20230427.04.00",
}

params = {
    "key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    "prettyPrint": "false",
}


def get_action(video_id: str, minimum_views: int = 1000000) -> None:
    """
    Get action for video
    """

    try:
        video_info = info_from_video_id(video_id, cache=True)

        if video_info is None:
            return
        # There are 15 categories of videos on YouTube. They are:

        # 1. Film & Animation
        # 2. Autos & Vehicles
        # 3. Music
        # 4. Pets & Animals
        # 5. Sports
        # 6. Travel & Events
        # 7. Gaming
        # 8. People & Blogs
        # 9. Comedy
        # 10. Entertainment
        # 11. News & Politics
        # 12. How-to & Style
        # 13. Education
        # 14. Science & Technology
        # 15. Nonprofits & Activism

        # Is there anything else you would like to know about YouTube videos?
        # 11. News & Politics
        # 12. How-to & Style
        # 13. Education
        # 14. Science & Technology
        # 15. Nonprofits & Activism
        if video_info["views"] < minimum_views:
            return
        # "uploadDate": "2016-11-13",

        upload_date = datetime.strptime(video_info["uploadDate"], "%Y-%m-%d")

        # check if video is older than 30 days
        if (datetime.now() - upload_date).days > 30:
            return

        # give regular expression for the title of the video to be added to watch later
        # for only english leter and numbers

        # title_regex = r"^[a-zA-Z0-9\s]+$"

        if video_info["category"] in [
            "News & Politics",
            "How-to & Style",
            "Education",
            "Science & Technology",
            "Nonprofits & Activism",
        ] and (
            ("kid" not in video_info["title"].lower())
            and ("rhymes" not in video_info["title"].lower())
            and ("nursery" not in video_info["title"].lower())
            and ("baby" not in video_info["title"].lower())
            and ("children" not in video_info["title"].lower())
            and ("child" not in video_info["title"].lower())
            # match the title of the video with the regular expression so that only english letters and numbers are allowed
            # and (re.match(title_regex, video_info["title"]))
        ):
            # print(f"Skipping {video_id} because it has less than 100k views")
            # continue
            # [{setVideoId: "A7DB66B58B5090E4", action: "ACTION_REMOVE_VIDEO"}]

            # video_id_in_hexadecimal = hex(int(video_id))[2:].upper()

            # print(f"Removing {video_id_in_hexadecimal} from watch later")

            # actions.append(
            #     {
            #         "setVideoId": video_id,
            #         "action": "ACTION_REMOVE_VIDEO",
            #     }
            # )

            # else:
            print(f"Adding {video_id} to watch later")

            return {
                "addedVideoId": video_id,
                "action": "ACTION_ADD_VIDEO",
            }

    except Exception as error:  # pylint: disable=broad-except # noqa: B902
        print(f"Error with {video_id}")
        print(error)
        print(traceback.format_exc())


def add_videos_to_watch_later(video_ids: list, minimum_views=1000) -> None:
    """
    Add videos to watch later playlist

    :param videos: list of video ids
    :return: None
    """

    actions = []
    with ThreadPoolExecutor(max_workers=len(video_ids)) as executor:
        for action in executor.map(get_action, video_ids):
            if action is not None:
                actions.append(action)

    if len(actions) == 0:
        print("No videos to add")
        return

    actions.append(
        (
            {
                "action": "ACTION_REMOVE_WATCHED_VIDEOS",
            }
        )
    )

    json_data = {
        "context": {
            "client": {
                "hl": "en",
                "gl": "IN",
                "remoteHost": "103.68.23.116",
                "deviceMake": "",
                "deviceModel": "",
                "visitorData": "CgtmNWVxZHBxcFVXWSifksOiBg%3D%3D",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36,gzip(gfe)",
                "clientName": "WEB",
                "clientVersion": "2.20230427.04.00",
                "osName": "Windows",
                "osVersion": "10.0",
                "originalUrl": "https://www.youtube.com/",
                "screenPixelDensity": 1,
                "platform": "DESKTOP",
                "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                "configInfo": {
                    "appInstallData": "CJ-Sw6IGEJGprwUQ8qivBRCJ6K4FEOf3rgUQ4tSuBRDks_4SELiLrgUQr5-vBRDM9a4FEL22rgUQpZmvBRDMrv4SEIv5rgUQqrL-EhCgt_4SENf_rgUQ1KGvBRC3ka8FEO6irwUQzN-uBRDbm68FEKLsrgUQmNquBQ%3D%3D",
                },
                "screenDensityFloat": 1.25,
                "timeZone": "Asia/Calcutta",
                "browserName": "Chrome",
                "browserVersion": "112.0.0.0",
                "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "deviceExperimentId": "ChxOekl5T0RRNU9EVXpPREl4T0RJMk5qSTBPQT09EJ-Sw6IGGJ-Sw6IG",
                "screenWidthPoints": 982,
                "screenHeightPoints": 746,
                "utcOffsetMinutes": 330,
                "userInterfaceTheme": "USER_INTERFACE_THEME_LIGHT",
                "connectionType": "CONN_CELLULAR_3G",
                "memoryTotalKbytes": "8000000",
                "mainAppWebInfo": {
                    "graftUrl": "https://www.youtube.com/playlist?list=WL",
                    "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED",
                    "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                    "isWebNativeShareAvailable": True,
                },
            },
            "user": {
                "lockedSafetyMode": False,
            },
            "request": {
                "useSsl": True,
                "internalExperimentFlags": [],
                "consistencyTokenJars": [],
            },
            "adSignalsInfo": {
                "params": [
                    {
                        "key": "dt",
                        "value": "1683015969486",
                    },
                    {
                        "key": "flash",
                        "value": "0",
                    },
                    {
                        "key": "frm",
                        "value": "0",
                    },
                    {
                        "key": "u_tz",
                        "value": "330",
                    },
                    {
                        "key": "u_his",
                        "value": "8",
                    },
                    {
                        "key": "u_h",
                        "value": "864",
                    },
                    {
                        "key": "u_w",
                        "value": "1536",
                    },
                    {
                        "key": "u_ah",
                        "value": "816",
                    },
                    {
                        "key": "u_aw",
                        "value": "1536",
                    },
                    {
                        "key": "u_cd",
                        "value": "24",
                    },
                    {
                        "key": "bc",
                        "value": "31",
                    },
                    {
                        "key": "bih",
                        "value": "729",
                    },
                    {
                        "key": "biw",
                        "value": "966",
                    },
                    {
                        "key": "brdim",
                        "value": "0,0,0,0,1536,0,1536,816,982,746",
                    },
                    {
                        "key": "vis",
                        "value": "1",
                    },
                    {
                        "key": "wgl",
                        "value": "true",
                    },
                    {
                        "key": "ca_type",
                        "value": "image",
                    },
                ],
            },
        },
        "actions": actions,
        "playlistId": "WL",
        "params": "CAFAAQ%3D%3D",
    }

    response = post_url(
        "https://www.youtube.com/youtubei/v1/browse/edit_playlist",
        params=params,
        cookies=cookies,
        headers=headers,
        json=json_data,
        timeout=50,
    )

    if response.status_code == 200:
        print("Successfully added videos to watch later playlist")
    else:
        print("Failed to add videos to watch later playlist")
        print(response.text)


def wl_main():
    """Main function for watch later"""

    def video_ids_from_main_id_all(function_id: str) -> List[str]:
        """Get all video IDs from a given ID"""
        # print("Getting video IDs from main ID")
        return video_ids_from_main_id(function_id)

    def get_list_of_list_of_video_ids(ids: List[str]):
        """Get all video IDs from a given ID"""

        try:
            print(f"max_workers: {20}")
            responses = get_responses(ids)

            print("Got responses")

            print(responses)

            return responses

        except Exception as error:  # pylint: disable=broad-except
            traceback.print_exc()
            print(error)
            print("Error")
            return []

    def get_responses(ids: List[str]):
        """Get all video IDs from a given ID"""
        with ThreadPoolExecutor(max_workers=len(ids)) as executor:
            responses = executor.map(video_ids_from_main_id_all, ids)
        print("Got video IDs")
        return responses

    with open("cw.txt", "r", encoding="utf-8") as file:
        ids = file.readlines()
        ids = [id.strip() for id in ids]
        print(ids)

    ids = get_list_of_list_of_video_ids(ids)

    print("ids are")
    print(ids)
    all_video_ids = []
    for video_ids in ids:
        all_video_ids += video_ids

    # deduplicate video ids
    all_video_ids = list(set(all_video_ids))

    print("all_video_ids are ", all_video_ids)

    # add_videos_to_watch_later(video_ids)

    a = 1000

    if len(all_video_ids) > 100:
        print("length of all_video_ids is ", len(all_video_ids))
        all_video_ids_chunks = []

        for i in range(0, len(all_video_ids), a):
            all_video_ids_chunks.append(all_video_ids[i : i + a])

        print("all_video_ids_chunks are ", all_video_ids_chunks)

        for all_video_ids_chunk in all_video_ids_chunks:
            print("all_video_ids_chunk is ", all_video_ids_chunk)

            try:
                add_videos_to_watch_later(all_video_ids_chunk)

            except Exception as error:  # pylint: disable=broad-except
                traceback.print_exc()

                print(error)

    else:
        add_videos_to_watch_later(all_video_ids)


if __name__ == "__main__":
    for i in range(100):
        wl_main()
