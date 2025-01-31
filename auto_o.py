"""
make outro for a id
"""

from concurrent.futures import ProcessPoolExecutor
import os
import sys

from auto_im import video_ids_urls_from_id_segment_category
from f import (
    WORKING_DIRECTORY,
    end_of_video,
    process_responses,
    random_choice,
    user_ids_from_segment_type,
)
from sb_api import return_url_to_post
from yt_api import duration_from_video_id
from reques import post_url

user_ids = user_ids_from_segment_type()


def make_outro_from_id(  # pylint: disable=too-many-locals
    function_id: str,
    function_outro_length: int,
    function_segment_category: str = "outro",
    function_duration: int = None,
    function_action_type: str = "skip",
) -> None:
    """This function is used to make an outro from a function id.

    Args:
        function_id (str): The id of the function.
        function_outro_length (int): The length of the outro.
        function_segment_category (str, optional): The segment category.
        function_duration (int, optional): The duration of the video. Defaults to None.
        function_action_type (str, optional): The action type. Defaults to "skip".
    """

    video_ids, urls = video_ids_urls_from_id_segment_category(
        function_id, function_segment_category
    )

    if len(video_ids) == 0:
        print(f"no video ids found for {function_id}")
        return

    chunk_size = 100
    video_ids_chunks = [
        video_ids[i : i + chunk_size] for i in range(0, len(video_ids), chunk_size)
    ]

    for video_ids in video_ids_chunks:

        with ProcessPoolExecutor(max_workers=100):

            for video_id in video_ids:

                try:

                    if function_duration is None:

                        video_duration = duration_from_video_id(video_id)
                        end = end_of_video(video_duration)
                    else:
                        video_duration = function_duration
                        end = video_duration
                    start = video_duration - function_outro_length

                    user_id = random_choice(user_ids)

                    url = return_url_to_post(
                        video_id,
                        start,
                        end,
                        function_segment_category,
                        function_action_type,
                        user_id,
                    )
                    response = post_url(url)
                    responses = [response]
                    process_responses(
                        video_ids,
                        function_segment_category,
                        function_action_type,
                        responses,
                    )

                except Exception as error:  # pylint: disable=broad-except
                    print(f"error {error} with {video_id}")
                    print(error)


if __name__ == "__main__":

    cd_first = os.cwdir()

    try:
        os.chdir(WORKING_DIRECTORY)

        if len(sys.argv) == 3:

            main_id = sys.argv[1]
            outro_length = float(sys.argv[2])

            make_outro_from_id(main_id, outro_length)
        elif len(sys.argv) == 4:
            main_id = sys.argv[1]
            outro_length = float(sys.argv[2])
            segment_category = sys.argv[3]

            make_outro_from_id(main_id, outro_length, segment_category)

        elif len(sys.argv) == 5:
            main_id = sys.argv[1]
            outro_length = float(sys.argv[2])
            segment_category = sys.argv[3]
            duration = float(sys.argv[4])

            make_outro_from_id(main_id, outro_length, segment_category, duration)

    except Exception as main_error:  # pylint: disable=broad-except
        print(main_error)
    os.chdir(cd_first)
