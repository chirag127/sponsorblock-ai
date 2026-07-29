"""This is the main function that is called when the program is run."""

import os
import random
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import List

from add_to_watch_later import wl_main

wl_main()

from auto import all_auto_channel_ids_processing, process_video_ids
from config import mto
from f import (WORKING_DIRECTORY, execute,
               install_requirements_for_recognition, return_already_run_videos,
               return_de_duped_list, system_information, write_to_file)
from yt_api import get_feed, video_ids_from_main_id

LIMIT_OR_NOT = random.random() < 0.9


MAX_WORKERS = 400


def video_ids_from_main_id_all(function_id: str) -> List[str]:
    """Get all video IDs from a given ID"""
    # print("Getting video IDs from main ID")
    return video_ids_from_main_id(function_id, LIMIT_OR_NOT)


def get_list_of_list_of_video_ids(ids: List[str]):
    """Get all video IDs from a given ID"""

    try:
        print(f"max_workers: {MAX_WORKERS}")
        return get_responses(ids)

    except Exception as error:  # pylint: disable=broad-except
        traceback.print_exc()
        print(error)
        print("Error")
        return []


def get_responses(ids: List[str]) -> List[List[str]]:
    """Get all video IDs from a given ID"""
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        responses = executor.map(video_ids_from_main_id_all, ids)
    print("Got video IDs")
    return responses


if ("/work" in WORKING_DIRECTORY) and ("kaggle" not in WORKING_DIRECTORY):
    MAIN_TIMEOUT = mto
    MAIN_TIMEOUT = int(MAIN_TIMEOUT)

else:
    MAIN_TIMEOUT = 60 * 60 * 24 * 7 * 4 * 2 * 2


# @timeout(MAIN_TIMEOUT, use_signals=False)
def main(recognize_speech=True, ids=None):
    """
    This is the main function that is called when the program is run.
    timeout is set to 1.5 hours
    """
    try:
        # if random.random() < 0.9:
        # wl_main()

        if recognize_speech:
            recognize_speech = (
                "studiolab" not in WORKING_DIRECTORY
                and "hex" not in WORKING_DIRECTORY
                and "kaggle" not in WORKING_DIRECTORY
                and "/workspaces/Autosb" not in WORKING_DIRECTORY
            )

        if recognize_speech and not all_auto_channel_ids_processing:
            install_requirements_for_recognition()
        system_information()

    except Exception as error:  # pylint: disable=broad-except
        print(error)
        print("Error")

    if ids is None:
        ids = sys.argv[1:] if len(sys.argv) > 1 else get_ids_if_not_ids()
    print(f"found {len(ids)} ids")
    ids = [id for id in ids if id != ""]

    # size = MAX_WORKERS * 15

    print(f"Processing {len(ids)} ids")

    video_ids = []

    responses = get_list_of_list_of_video_ids(ids)

    for response in responses:
        video_ids.extend(response)
        print(f"Got {len(video_ids)} video IDs")

    if not all_auto_channel_ids_processing:
        print("adding popular videos")

        try:
            pass

        # video_ids = invidious_popular() + video_ids

        except Exception as error:  # pylint: disable=broad-except
            print(error)
            print("Error")

        print("adding trending videos")

        # try:
        #  video_ids.extend(get_trending_videos())
        # except Exception as error:  # pylint: disable=broad-except
        # print(error)

        try:
            video_ids.extend(get_feed())
        except Exception as error:  # pylint: disable=broad-except
            print(error)

    number_of_videos = len(video_ids)
    already_run_video_ids = return_already_run_videos()

    if number_of_videos > 100000 and len(already_run_video_ids) > 13000000:
        local_file_name = "already_run/already_run_auto.txt"

        # get common video ids from already run and new video ids
        # get intersection of already run and new video ids
        common_video_ids = list(set(already_run_video_ids).intersection(video_ids))

        string_to_write = "\n".join(common_video_ids)

        write_to_file(local_file_name, string_to_write)

        # remove common video ids from new video ids
        video_ids = list(set(video_ids) - set(common_video_ids))

    process_video_ids(video_ids, recognize_speech)

    execute(
        ["python", "auto_im.py", "m", "UCjvgGbPPn-FgYeguc5nxG4A", "0", "4.1", "preview"]
    )
    execute(
        ["python", "auto_im.py", "m", "UCjvgGbPPn-FgYeguc5nxG4A", "4", "7.1", "intro"]
    )

    execute(["python", "auto_im.py", "m", "c/NomadicIndian", "0", "20.1", "intro"])
    execute(["python", "auto_im.py", "i", "c/HasteRaho", "1.1", "intro"])

    execute(["python", "auto_im.py", "i", "c/UltraGujarati", "1.1"])

    execute(["python", "auto_im.py", "i", "c/LIVCrime", "5.1", "interaction"])

    execute(
        [
            "python",
            "auto_im.py",
            "i",
            "PLzufeTFnhupwdg6mzrhRwjhHBbrwiQePd",
            "6.1",
            "intro",
        ]
    )
    execute(
        [
            "python",
            "auto_im.py",
            "i",
            "PLzufeTFnhupxrJy3qyXg_YyDqEp2jATTL",
            "5.1",
            "intro",
        ]
    )
    execute(
        [
            "python",
            "auto_im.py",
            "i",
            "PLzufeTFnhupziGQj2eZahE8ITI9O-x1g5",
            "5.1",
            "intro",
        ]
    )
    execute(
        [
            "python",
            "auto_im.py",
            "i",
            "PLzufeTFnhupwXuDiSs6KbxfF9rO1wuAzW",
            "5.1",
            "intro",
        ]
    )

    # if recognize_speech:

    #     # write_video_ids_reverse_order_if_in_cache(video_ids)


def write_video_ids_reverse_order_if_in_cache(video_ids: list) -> None:
    """
    write video ids in reverse order if in cache
    """

    already_run_ids: list = return_already_run_videos()

    # reverse the order
    reversed_already_run_ids: list = already_run_ids[::-1]

    # extend video id
    reversed_already_run_ids.extend(
        video_id for video_id in video_ids if video_id in already_run_ids
    )
    # remove dupe
    reversed_already_run_ids: list = return_de_duped_list(reversed_already_run_ids)

    # reverse again
    reversed_already_run_ids: list = reversed_already_run_ids[::-1]

    local_file_name: str = "already_run/already_run_auto.txt"

    write_to_file(local_file_name, "\n".join(reversed_already_run_ids))


def get_ids_if_not_ids() -> List[str]:
    full_path = os.path.join(WORKING_DIRECTORY, "ci.txt")
    with open(full_path, "r", encoding="utf-8") as file:
        result = file.read().splitlines()

    full_path = os.path.join(WORKING_DIRECTORY, "cia.txt")
    with open(full_path, "r", encoding="utf-8") as file:
        result = result + file.read().splitlines()

    print("Got IDs from file")
    result = random.sample(result, len(result))
    return result


if __name__ == "__main__":
    print("Starting")
    try:
        if "/work" in WORKING_DIRECTORY and "kaggle" not in WORKING_DIRECTORY:
            try:
                os.chdir(WORKING_DIRECTORY)
            except Exception as main_error:  # pylint: disable=broad-except
                print(main_error)
                print("Error")

            main(
                True,
                [
                    "artificial intelligence",
                    "machine learning",
                    "deep learning",
                    "movie explained",
                    "movie",
                    "movie review",
                    "how to start a business",
                    "how to study",
                    "how to learn",
                    "how to learn to code",
                    "how to learn to kiss",
                    "prank",
                    "english news",
                    "world affairs",
                    "meaning of the poem",
                    "full tutorial",
                    "travel india",
                ],
            )

            # for _ in range(1, 100):
            #     main()
        else:
            for _ in range(1, 100):
                try:
                    os.chdir(WORKING_DIRECTORY)
                except Exception as main_error:  # pylint: disable=broad-except
                    print(main_error)
                    print("Error")
                main()
                main(False)
    except Exception as main_error:  # pylint: disable=broad-except
        print(main_error)
        print("Error")
