"""
this module is used to make requests to the api to create segments
for the intro and the middle segments
so that the api can be used to create segments for the intro and the middle segments
"""

import os

from f import (WORKING_DIRECTORY, process_responses, random_choice,
               user_ids_from_segment_type)
from reques import post_urls
from sb_api import return_url_to_post
from sync_already_run import sync_already_run
from yt_api import not_already_run_video_ids_from_main_id_and_category

user_ids = user_ids_from_segment_type()


def make_middle_segment_from_id(
    main_id, start_of_segment, end, segment_category="filler", action_type="skip"
):
    """this function makes a request to the api to create a middle segment"""
    make_request_from_id(main_id, start_of_segment, end, segment_category, action_type)


def make_request_from_id(main_id, start, end, category, action_type="skip"):
    """this function makes a request to the api to create a middle segment"""

    sync_already_run(category)

    video_ids = not_already_run_video_ids_from_main_id_and_category(main_id, category)

    chunk_size = 100

    video_ids_chunks = [
        video_ids[i : i + chunk_size] for i in range(0, len(video_ids), chunk_size)
    ]

    for video_ids in video_ids_chunks:

        print(f"found {len(video_ids)} video ids to process")

        if len(video_ids) == 0:
            print(f"no video ids found for {main_id}")
            return

        print(f"{action_type}ing {category} from {start} to {end} with {video_ids}")

        user_id = random_choice(user_ids)

        urls = [
            return_url_to_post(
                video_id,
                start,
                end,
                category,
                action_type,
                user_id=user_id,
            )
            for video_id in video_ids
        ]

        responses = post_urls(urls)

        process_responses(video_ids, category, action_type, responses)


def make_intro(main_id, end, segment_category="intro", action_type="skip"):
    """this function makes a request to the api to create an intro segment"""
    make_request_from_id(main_id, 0, end, segment_category, action_type)


def video_ids_urls_from_id_segment_category(main_id, segment_category):
    """this function gets the video ids and urls from the api for a segment category"""

    sync_already_run(segment_category)

    video_ids = not_already_run_video_ids_from_main_id_and_category(
        main_id, segment_category
    )

    print(f"found {len(video_ids)} video ids to process")

    urls = []
    return video_ids, urls


if __name__ == "__main__":

    cd_first = os.getcwd()

    try:
        os.chdir(WORKING_DIRECTORY)

        import sys

        MAIN_SEGMENT_POSITION_TYPE = sys.argv[1]
        main_segment_category = "filler"  # pylint: disable=invalid-name
        main_main_id = sys.argv[2]  # pylint: disable=invalid-name
        if MAIN_SEGMENT_POSITION_TYPE == "i":
            if len(sys.argv) == 4:

                main_end = float(sys.argv[3])
                make_intro(main_main_id, main_end, main_segment_category)
            elif len(sys.argv) == 5:
                main_end = float(sys.argv[3])
                main_segment_category = sys.argv[4]
                make_intro(main_main_id, main_end, main_segment_category)
        elif MAIN_SEGMENT_POSITION_TYPE == "m":
            if len(sys.argv) == 5:
                main_end = float(sys.argv[4])
                main_start = float(sys.argv[3])
                make_middle_segment_from_id(
                    main_main_id, main_start, main_end, main_segment_category
                )
            elif len(sys.argv) == 6:
                main_start = float(sys.argv[3])
                main_end = float(sys.argv[4])
                main_segment_category = sys.argv[5]
                make_middle_segment_from_id(
                    main_main_id, main_start, main_end, main_segment_category
                )
            else:
                print("wrong number of arguments")
                print("usage:")
                print(
                    "python3 auto_im.py m<main_main_id> <start_of_segment> "
                    + "<end> <segment_category>"
                )

    except Exception as e:  # pylint: disable=broad-except
        print(e)
    finally:
        os.chdir(cd_first)
