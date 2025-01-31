"""The main file for the auto segmentation."""


import contextlib
import os
import random
import sys
import traceback
from concurrent import futures
from datetime import datetime
from functools import partial

import psutil
from add_to_watch_later import add_videos_to_watch_later

from chapters import get_chapters_with_start_and_end_time
from f import (
    WORKING_DIRECTORY,
    all_channel_ids,
    color,
    end_of_video,
    is_english,
    max_max_workers_for_the_pp,
    merge_segments,
    random_choice,
    return_segment,
    segment_duration_from_start_and_end,
    system_information,
    user_ids_from_segment_type,
    wait_for_time_between_1_and_specified_time,
    write_video_id_in_cache,
    yt_link_with_segments,
    append_to_file,
    get_all_auto_channel_ids,
)
from ftr import get_location
from make_sub_auto import get_words_by_autosub
from model import get_model_tokenizer_classifier
from predict import PredictArguments, SegmentationArguments
from predict import predict as pred
from youtube_transcript_api_words import get_words
from sb_api import make_request, segments_stats_for_video_id
from shared import GeneralArguments
from silence import make_silence_all_segments
from skip_sponsor_api import get_skip_sponsor_api_response
from sync_already_run import sync_already_run
from words import (
    get_words_from_video_info,
    remove_unnecessary_words,
)
from yt_api import (
    info_from_video_id,
    not_already_run_video_ids_from_video_ids_and_category,
    video_ids_from_main_id,
)

full_sponsor_user_ids = user_ids_from_segment_type("full_sponsor")

# Setting the value of the variable all_auto_channel_ids_processing to True.
all_auto_channel_ids_processing = True
# Setting the value of the variable all_auto_channel_ids_processing to False.
all_auto_channel_ids_processing = False

if all_auto_channel_ids_processing:
    all_auto_channel_ids = get_all_auto_channel_ids()

max_workers_for_the_pp = 10000 if all_auto_channel_ids_processing else 4
# max_workers_for_the_pp = 25


def get_user_ids():
    """Get the user ids."""
    function_user_ids = user_ids_from_segment_type()
    function_data_frame_of_uuids_and_user_ids = None  # pylint: disable=invalid-name
    return function_user_ids, function_data_frame_of_uuids_and_user_ids


user_ids, data_frame_of_uuids_and_user_ids = get_user_ids()

MODELS = {
    "Small (293 MB)": {
        "pretrained": "google/t5-v1_1-small",
        "repo_id": "Hugherinit/hi",
        "num_parameters": "77M",
    },
    "Base v1 (850 MB)": {
        "pretrained": "t5-base",
        "repo_id": "Xenova/sponsorblock-base-v1",
        "num_parameters": "220M",
    },
    "Base v1.1 (944 MB)": {
        "pretrained": "google/t5-v1_1-base",
        "repo_id": "Xenova/sponsorblock-base-v1.1",
        "num_parameters": "250M",
    },
}


def print_hf_and_sbb_url(video_id):
    """Print the huggingface url and the sbb url."""
    url = f"https://huggingface.co/spaces/Xenova/sponsorblock-ml?v={video_id}"
    sbb_url = f"https://sb.ltn.fi/video/{video_id}"

    print(f"{color.GREEN}Huggingface url: {color.END}{url}")
    print(f"{color.GREEN}SBB url: {color.END}{sbb_url}")


CLASSIFIER_PATH = "Xenova/sponsorblock-classifier-v2"

TRANSCRIPT_TYPES = {
    "AUTO_MANUAL": {
        "label": "Auto-generated (fallback to manual)",
        "type": "auto",
        "fallback": "manual",
    },
    "MANUAL_AUTO": {
        "label": "Manual (fallback to auto-generated)",
        "type": "manual",
        "fallback": "auto",
    },
}


def predict_function(model, tokenizer, segmentation_args, classifier, video_id, words):
    """Predict the segmentation of a video."""
    return pred(
        video_id,
        model,
        tokenizer,
        segmentation_args,
        words,
        classifier,
    )


def load_predict(model_id):
    """Load the model and tokenizer."""
    model_info = MODELS[model_id]

    predict_args = PredictArguments(model_name_or_path=model_info["repo_id"])
    general_args = GeneralArguments()
    segmentation_args = SegmentationArguments()

    model, tokenizer, classifier = get_model_tokenizer_classifier(
        predict_args, general_args
    )

    return partial(predict_function, model, tokenizer, segmentation_args, classifier)


cwd_first = os.getcwd()

# try:
#     print(f"{color.GREEN}Current directory: {color.END}{os.getcwd()}")
#     print(f"{color.GREEN}Process ID: {color.END}{os.getpid()}")
#     print(
#         f"Memory usage:{psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024} MB"
#     )
#     print(f"{color.GREEN}CPU usage: {color.END}{psutil.cpu_percent()}%")
#     print(f"{color.GREEN}Number of CPUs: {color.END}{psutil.cpu_count()}")
#     print(f"Number of threads: {psutil.Process(os.getpid()).num_threads()}")
#     print(f"{color.GREEN}Number of files: {color.END}{len(os.listdir())}")

#     system_information()

# except Exception as main_exception:  # pylint: disable=broad-except
#     print(f"{color.RED}Exception in main: {color.END}{main_exception}")
#     print(traceback.format_exc())

try:

    os.chdir(WORKING_DIRECTORY)

    print(f"{color.GREEN}Current directory: {color.END}{os.getcwd()}")

except Exception as main_error:  # pylint: disable=broad-except
    print(f"Could not change directory to {WORKING_DIRECTORY}{color.END}{main_error}")
    print(f"{color.RED}Exception in main: {color.END}{main_error}")

finally:

    MODEL_ID = "Small (293 MB)"

    print("loading model")

    make_predictions = load_predict(MODEL_ID)

    os.chdir(cwd_first)


def main(main_id, recognize_speech=False, user_id=None):
    """Main function."""
    video_ids = video_ids_from_main_id(main_id)
    process_video_ids(video_ids, recognize_speech=recognize_speech, user_id=user_id)


def final_video_ids_from_video_ids(video_ids):
    """Return the final video ids."""
    video_ids = not_already_run_video_ids_from_video_ids_and_category(video_ids, "auto")

    if random.random() < 0.9:

        video_ids = not_already_run_video_ids_from_video_ids_and_category(
            video_ids, "recent"
        )

    return video_ids


def process_video_ids(video_ids, recognize_speech=False, user_id=None):
    """Process the video IDs."""
    get_location()

    sync_already_run()

    sync_already_run("recent")

    if video_ids:

        process_video_ids_if_video_ids(video_ids, recognize_speech, user_id)
    else:
        print(f"{color.GREEN}No more videos to process\nExiting...{color.END}")
        return


def making_segments_without_words(video_id, duration, description, title, chapters):

    segments = []

    if not segments and chapters:
        segments.extend(
            return_segment(chapter["start"], chapter["end"], "sponsor", "skip")
            for chapter in chapters
            if "sponsor" in chapter["text"].lower()
        )

    if not segments and (
        "sponsor" in description.lower()
        or "sponsor" in title.lower()
        or "sponsor" in description.lower()
    ):
        segments.append(return_segment(0, 0, "sponsor", "full"))
    if segments:
        make_request(
            video_id=video_id,
            segment_type="without_words",
            submit_segments=segments,
            user_ids=full_sponsor_user_ids,
            user_id=None,
            duration=duration,
            data_frame_of_uuids_and_user_ids=None,
        )

    else:
        write_video_id_in_cache(video_id)


def process_video_ids_if_video_ids(video_ids, recognize_speech, user_id):
    print(f"{len(video_ids)} videos to process")

    print("getting final video IDs")

    video_ids = final_video_ids_from_video_ids(video_ids)

    print(f"{len(video_ids)} videos to process")

    # total_videos_to_process = len(video_ids)

    print("got final video IDs")

    print("making segments")

    size = 1000
    video_ids_chunks = (
        [video_ids[i : i + size] for i in range(0, len(video_ids), size)]
        if len(video_ids) > size
        else [video_ids]
    )

    print(f"{len(video_ids_chunks)} chunks to process")

    for chunk_number, video_ids_chunk in enumerate(video_ids_chunks):
        if chunk_number != 0:
            try:

                sync_already_run()

                sync_already_run("recent")

            except Exception as error:  # pylint: disable=broad-except
                print(f"could_not_sync_already_run with error {error}")

        print(f"{len(video_ids_chunk)} videos to process")

        print("getting final video IDs")

        video_ids = final_video_ids_from_video_ids(video_ids_chunk)

        print(
            f"{len(video_ids)} videos to process after removing ",
            "already run videos from cache",
        )

        print("got final video IDs")

        print("making segments")

        make_segments(video_ids, recognize_speech=recognize_speech, user_id=user_id)

        print("made segments")


def make_segments(video_ids, recognize_speech=False, user_id=None):
    """Make the segments for the videos."""
    print("running using multiprocessing")

    if video_ids:

        try:

            make_segment_with_pp(
                video_ids, recognize_speech=recognize_speech, user_id=user_id
            )

        except Exception as error:  # pylint: disable=broad-except
            print(f"could not make segments with p p with error {error}")
            return
    else:

        print(f"{color.GREEN}No more videos to process\nExiting...{color.END}")
        return


# @timeout(1000, use_signals=False)
def make_segment_with_pp(
    video_ids, return_please=False, recognize_speech=False, user_id=None
):  # pylint: disable=unused-argument
    """Make the segments for the videos with parallel processing."""
    print(f"{len(video_ids)} videos to process with no return_segment")

    with futures.ThreadPoolExecutor(max_workers=max_workers_for_the_pp) as executor:

        the_futures = []
        for i in range(len(video_ids)):

            future = executor.submit(
                make_segment_with_error_catch,
                video_ids[i],
                return_please,
                recognize_speech,
                user_id,
                i,
                len(video_ids),
            )
            the_futures.append(future)
        for _ in futures.as_completed(the_futures):
            pass


def make_segment_with_error_catch(
    video_id,
    return_please=False,
    recognize_speech=False,
    user_id=None,
    number=None,
    total_number=None,
):
    """Make the segments for the videos with error catching."""
    try:
        if number:
            print(f"{number} of {total_number} videos to process")
        print("running on video", video_id)
        make_segment(
            video_id,
            return_please=return_please,
            recognize_speech=recognize_speech,
            user_id=user_id,
        )

        if number:
            print(f"{number} of {total_number} videos processed")

    except Exception as error:  # pylint: disable=broad-except

        traceback.print_exc()

        print(
            f"{color.RED}Error: {error} in {video_id} in function{color.END}",
            f"{color.RED} make_segment_with_error_catch{color.END}",
        )


def make_segment(
    video_id, return_please=False, recognize_speech=False, user_id=None
):  # sourcery skip: low-code-quality
    """make_segment"""

    confidence_threshold = 40
    ts_type_id = "AUTO_MANUAL"
    url = f"https://huggingface.co/spaces/Xenova/sponsorblock-ml?v={video_id}"
    sbb_url = f"https://sb.ltn.fi/video/{video_id}"

    if user_id is None:
        user_id = random_choice(user_ids)

    video_info = info_from_video_id(video_id)

    if not video_info:
        print(
            f"""{color.DARK_PURPLE}Video not found
sbb is at {sbb_url}
hm at {url}{color.END}"""
        )
        write_video_id_in_cache(video_id, "recent")
        return None

    title = video_info["title"]
    upload_date = video_info["uploadDate"]
    split_date = upload_date.split("-")
    year = split_date[0]
    month = split_date[1]
    day = split_date[2]
    channel_name = video_info["uploader"]
    uploader_url = video_info["uploaderUrl"]
    duration = video_info["duration"]
    views = video_info["views"]
    likes = video_info["likes"]
    uploader_subscriber_count = video_info["uploaderSubscriberCount"]
    subtitles = video_info["subtitles"]
    description = video_info["description"]
    uploader_url = video_info["uploaderUrl"]
    channel_id = uploader_url.split("/")[-1]

    title = title.lower()

#     string_to_check_for_english = title + " " + channel_name
#     if not is_english(string_to_check_for_english):
#         print(
#             f"""{color.RED}Not English in {video_id} for the title {title}
# channel name {channel_name}{color.END}"""
#         )
#         write_video_id_in_cache(video_id)
#         return None

    if all_auto_channel_ids_processing is True:
        if (channel_id not in all_channel_ids) and (
            channel_id not in all_auto_channel_ids
        ):
            if uploader_subscriber_count > 100000:

                if subtitles != []:

                    details = (
                        f"{channel_id},{channel_name},"
                        + f"{uploader_subscriber_count},{title},{video_id}"
                    )
                    append_to_file("all_auto_channel_ids.txt", details + "\n")

                    all_auto_channel_ids.append(channel_id)

        return None

    try:
        chapters = video_info["chapters"]

        chapters = get_chapters_with_start_and_end_time(chapters, duration)

    except Exception as error:  # pylint: disable=broad-except
        print("failed to get chapters with error", error)
        chapters = None

    try:

        is_livestream = video_info["livestream"]

        if is_livestream:
            print(f"{color.DARK_PURPLE}Video is a livestream{color.END}")
            write_video_id_in_cache(video_id, "recent")
            return None
    except Exception as error:  # pylint: disable=broad-except
        print("failed to get livestream with error", error)
        is_livestream = None

    if os.getcwd() == "/workspace/Autosb" and uploader_subscriber_count > 100000:

        add_videos_to_watch_later([video_id])

    if channel_id in all_channel_ids:
        uploader_subscriber_count = 1000000

    today = datetime.now()
    upload_date = datetime(int(year), int(month), int(day))

    delta = today - upload_date

    delta_days = delta.days

    if delta_days < 3 and uploader_subscriber_count > 10000:

        print(f"{color.RED}Video is less than 3 days old{color.END}")

        write_video_id_in_cache(video_id, "recent")

        return None

    do_not_process = False

    if (
        "Fresh Drama" in title
        or "iQiyi" in title
        or "YOUKU" in title
        or "Xing Zhaolin" in title
    ):
        do_not_process = True

    elif uploader_subscriber_count < duration / 100:
        print(f"{color.PURPLE}Video is too long and channel is too small{color.END}")

        do_not_process = True

    elif (((views < (duration / 5))) or (views < 100)) and delta.days > 1:

        print(f"{color.PURPLE}Video has too few views {video_id} {views}{color.END}")
        do_not_process = True

    elif (views < (duration / 5)) and views < 10:
        do_not_process = True

    print_most_detail_of_a_video(
        video_id,
        url,
        sbb_url,
        title,
        upload_date,
        year,
        month,
        day,
        channel_name,
        uploader_url,
        duration,
        views,
        likes,
        uploader_subscriber_count,
        subtitles,
    )

    (
        already_made_categories,
        already_made_actions,
        segment_count,
        number_of_sponsor,
    ) = segments_stats_for_video_id(video_id, segment_type="skip")

    if segment_count > 0 and channel_id:

        write_video_id_in_cache(video_id)

        return None

    if do_not_process:

        making_segments_without_words(video_id, duration, description, title, chapters)

        write_video_id_in_cache(video_id)

        return None

    if segment_count > max((duration / 300) * 2, 2):
        write_video_id_in_cache(video_id)

        return None

    if return_please:

        write_video_id_in_cache(video_id)
        return None

    is_recognized = False

    words = None

    if subtitles == []:

        if subtitles == []:

            try:
                making_segments_without_words(
                    video_id, duration, description, title, chapters
                )

            except Exception as error:  # pylint: disable=broad-except
                print(f"failed to make segments without words with error {error}")
        print(f"{color.RED}Video has no subtitles")

        print(f"{color.RED}Video is {delta.days} days old{color.END}")

        if recognize_speech:
            print(
                f"""{color.RED}Video has no subtitles
    {print_hf_and_sbb_url(video_id)}"""
            )
            print(
                f"{color.GREEN}getting words for video {video_id} using sr{color.END}"
            )
            words, is_generated, is_recognized = get_words_by_autosub(
                video_id,
                duration=duration,
                delta_days=delta.days,
                views=views,
                subscriber=uploader_subscriber_count,
                max_workers_for_the_pp=max_workers_for_the_pp,
            )

            print(f"{color.GREEN}got words for video {video_id} using sr{color.END}")

        else:
            print(
                f"""{color.RED}Video has no subtitles
no sr{color.END}"""
            )
            return None

    else:
        if max_workers_for_the_pp > max_max_workers_for_the_pp:
            return None

        try:
            print("getting words for video", video_id)

            words, is_generated = get_words_from_video_info(video_info)

            if words:

                print("got words from piped")

            else:
                words, is_generated = get_words(
                    video_id,
                    transcript_type=TRANSCRIPT_TYPES[ts_type_id]["type"],
                    fallback=TRANSCRIPT_TYPES[ts_type_id]["fallback"],
                )

            if not words and recognize_speech:
                print(f"{color.RED}Video {video_id} has no words{color.END}")

                words, is_generated, is_recognized = get_words_by_autosub(
                    video_id,
                    duration=duration,
                    delta_days=delta.days,
                    views=views,
                    subscriber=uploader_subscriber_count,
                )
                print(f"got words by autosub: {words}")

            elif not words and not recognize_speech:
                print(
                    f"{color.GREEN}Video {video_id} has no words and no sr{color.END}"
                )

                return

            print("got words for video", video_id)

        except Exception as error:  # pylint: disable=broad-except

            print(f"failed to get words for video {video_id} with error {error}")

            print(traceback.format_exc())
            wait_for_time_between_1_and_specified_time(60)
            print(
                f"""{color.RED}Could not load transcript for {video_id}
{print_hf_and_sbb_url(video_id)}{color.END}"""
            )
            if recognize_speech and (random.randint(0, 100) < 5):
                print(f"{color.GREEN}getting words for {video_id} using sr{color.END}")
                words, is_generated, is_recognized = get_words_by_autosub(
                    video_id,
                    duration=duration,
                    delta_days=delta.days,
                    views=views,
                    subscriber=uploader_subscriber_count,
                )

                print(
                    f"{color.GREEN}got words for video {video_id} using sr{color.END}"
                )
            else:
                print("returning")
                return None

    if not words:
        print("words is empty", video_id)
        print(
            f"""{color.BLUE}No words for {video_id}
maybe, the video is too short to segment
{print_hf_and_sbb_url(video_id)}"""
        )

        write_video_id_in_cache(video_id)

        return None

    if words == "vnd":

        print("words is vnd", video_id)
        print(f"{color.RED}the video is not downloadable yet")

        return None

    if words == "nop":
        print("words is nop", video_id)

        return None

    transcript = ""
    for word in words:
        transcript += word["text"] + " "

    words = remove_unnecessary_words(words)

    if not words:

        making_segments_without_words(video_id, duration, description, title, chapters)

        write_video_id_in_cache(video_id)

        return None

    print(f"Running on Video_id {video_id} title {title} channel {channel_name} ")

    all_segments, user_id = make_silence_all_segments(
        video_id,
        url,
        sbb_url,
        title,
        duration,
        views,
        uploader_subscriber_count,
        description,
        words,
        is_generated,
        user_ids,
        user_id,
        is_recognized,
    )

    try:
        print("making pridiction for video", video_id)

        predictions = make_predictions(video_id, words)
    except Exception as erorr:  # pylint: disable=broad-except
        print(f"""{color.RED}Error in predicting for {video_id} with error {erorr}""")
        return

    outro_segments = []
    sponsor_segments = []
    selfpromo_segments = []
    interaction_segments = []

    if subtitles != []:
        try:

            skip_sponsor_segments = get_skip_sponsor_api_response(video_id)

            sponsor_segments.extend(skip_sponsor_segments)

        except Exception as error:  # pylint: disable=broad-except
            print(f"Error in skip_sponsor_api_response: {error}")

    if not predictions:
        print(f"{color.GREEN}No predictions for {video_id}{color.END}")

    else:
        for index, prediction in enumerate(predictions, start=1):
            category_key = prediction["category"]
            confidence = prediction["probability"] * 100
            action_type = "skip"
            main_end_of_segment = prediction["end"]
            main_start_of_segment = prediction["start"]
            text = " ".join(w["text"] for w in prediction["words"])
            if category_key == "sponsor":
                text_color = color.GREEN
            elif category_key == "selfpromo":
                text_color = color.YELLOW
            elif category_key == "interaction":
                text_color = color.PURPLE

            print(
                f"""Video {video_id}
title {title}
channel {channel_name}
segment {index}
start {main_start_of_segment}
end {main_end_of_segment}
text {text}
confidence {confidence} {text_color}
category {category_key}{color.END}"""
            )

            if confidence < confidence_threshold:
                print(
                    f"""{color.RED}Confidence too low! Skipping segment
confidence: {confidence} < {confidence_threshold}%{color.END}"""
                )
                continue

            change_time_limit = 0.1

            print(f"Duration: {duration}")
            segment_duration = segment_duration_from_start_and_end(
                main_start_of_segment, main_end_of_segment
            )

            print(f"Segment duration: {segment_duration}")
            if main_start_of_segment < 5 and main_start_of_segment > -10:
                main_start_of_segment = 0
                print(
                    f"""{color.CYAN}Video_id {video_id}
title {title}
channel {channel_name}
Start time too low! {main_start_of_segment} < 5
Setting to 0{color.END}"""
                )

                main_end_of_segment = main_end_of_segment + change_time_limit

            elif main_end_of_segment > duration - 30:

                print(
                    f"""{color.BLUE}Video_id {video_id}
title {title}
channel {channel_name}
End time too high! {main_end_of_segment} > {duration} - thirty seconds{color.END}"""
                )

                if main_end_of_segment > duration - 5:

                    if (
                        main_end_of_segment < duration - 3
                        and category_key in ["interaction", "selfpromo"]
                    ) and segment_duration < 20:
                        category_key = "outro"

                        print(
                            f"""{color.BLUE}Setting category to outro for
Video_id {video_id}
title {title}
channel {channel_name} {color.END}"""
                        )

                    main_end_of_segment = end_of_video(duration)

                    print(
                        f"""{color.GREEN}Setting end time to {main_end_of_segment}
Video_id {video_id}
title {title}
channel {channel_name}{color.END}"""
                    )

                elif duration > 300:

                    print(
                        f"""Video_id {video_id} title {title} channel {channel_name}
Segment {index}/{len(predictions)}: {category_key}
Confidence {confidence}%
Time span: {main_start_of_segment} - {main_end_of_segment}
Text: {text}{color.END}"""
                    )

                    outro_start = main_end_of_segment - change_time_limit
                    outro_end = end_of_video(duration)

                    outro_segments.append(
                        {
                            "segment": [outro_start, outro_end],
                            "category": "outro",
                        }
                    )
                    print(
                        f"""{color.BLUE}\nSetting outro from {outro_start} - {outro_end}
video {video_id} {color.END}"""
                    )

            else:

                main_start_of_segment = main_start_of_segment - change_time_limit
                main_end_of_segment = main_end_of_segment + change_time_limit

            if main_end_of_segment - main_start_of_segment > 0.5 * duration:

                if category_key in ["sponsor", "selfpromo"]:
                    main_end_of_segment = 0
                    main_start_of_segment = 0
                    action_type = "full"
                    category_key = "selfpromo"

                    print(
                        f"{color.BLUE}Setting segment to full for Video_id {video_id}"
                    )

            if category_key == "sponsor":
                sponsor_segments.append(
                    return_segment(
                        main_start_of_segment,
                        main_end_of_segment,
                        category_key,
                        action_type,
                    )
                )
            elif category_key == "selfpromo":
                selfpromo_segments.append(
                    return_segment(
                        main_start_of_segment,
                        main_end_of_segment,
                        category_key,
                        action_type,
                    )
                )
            elif category_key == "interaction":
                interaction_segments.append(
                    return_segment(
                        main_start_of_segment,
                        main_end_of_segment,
                        category_key,
                        action_type,
                    )
                )
            elif category_key == "outro":
                outro_segments.append(
                    return_segment(
                        main_start_of_segment, main_end_of_segment, "outro", action_type
                    )
                )

        with contextlib.suppress(Exception):

            time_to_merge = 20 if duration < 300 else 60

            sponsor_segments = merge_segments(sponsor_segments, time_to_merge)
            selfpromo_segments = merge_segments(selfpromo_segments, time_to_merge)
            interaction_segments = merge_segments(interaction_segments, time_to_merge)
            outro_segments = merge_segments(outro_segments, time_to_merge)

        if not sponsor_segments:

            if chapters:
                for chapter in chapters:
                    if "sponsor" in chapter["text"].lower():
                        sponsor_segments.append(
                            return_segment(
                                chapter["start"], chapter["end"], "sponsor", "skip"
                            )
                        )
                        user_id = random_choice(full_sponsor_user_ids)

        if not sponsor_segments:

            if (
                "sponsor" in description.lower()
                or "sponsor" in title.lower()
                or "sponsor" in description.lower()
            ):

                sponsor_segments.append(return_segment(0, 0, "sponsor", "full"))

                user_id = random_choice(full_sponsor_user_ids)

    model_segments = (
        sponsor_segments + selfpromo_segments + interaction_segments + outro_segments
    )

    if not model_segments and not all_segments:

        all_segments, user_id = make_silence_all_segments(
            video_id,
            url,
            sbb_url,
            title,
            duration,
            views,
            uploader_subscriber_count,
            description,
            words,
            is_generated,
            user_ids,
            user_id,
            is_recognized,
            True,
        )

        if outro_segments:

            for segment in all_segments:

                if segment["category"] == "outro":

                    all_segments.remove(segment)

    submit_segments = model_segments + all_segments

    if len(model_segments) > len(all_segments):

        pass

    link = yt_link_with_segments(video_id, submit_segments)

    print(f"{color.GREEN}Link to video with auto segments: {link}{color.END}")

    if submit_segments:

        make_request(
            video_id=video_id,
            segment_type="auto",
            submit_segments=submit_segments,
            user_ids=user_ids,
            user_id=user_id,
            duration=duration,
            data_frame_of_uuids_and_user_ids=data_frame_of_uuids_and_user_ids,
        )

    else:
        write_video_id_in_cache(video_id)


def print_most_detail_of_a_video(
    video_id,
    url,
    sbb_url,
    title,
    upload_date,
    year,
    month,
    day,
    channel_name,
    uploader_url,
    duration,
    views,
    likes,
    uploader_subscriber_count,
    subtitles,
):
    """
    Prints most of the details of a video
    """

    if max_workers_for_the_pp < max_max_workers_for_the_pp:
        print(
            f"""{color.GREEN}Making segment for video {video_id}
title: {title}
date: {upload_date} day: {day} month: {month} year: {year}
channel: {channel_name} ({uploader_url}) subscribed: {uploader_subscriber_count}
duration: {duration}
views: {views}
likes: {likes}
sbb is at {sbb_url}
hm at {url}{color.END}"""
        )


if __name__ == "__main__":

    ID = "techbar"
    # if len(sys.argv) < 2:
    #     print("not enough arguments")
    # elif len(sys.argv) == 2:
    #     ID = sys.argv[1]
    # else:
    #     print("too many arguments")
    # main(ID, recognize_speech=True)
    video_ids = video_ids_from_main_id(ID)

    make_segments(video_ids)
