"""
This module contains the functions to get the words in a video.
"""

import json
import os
import traceback
from datetime import datetime
from typing import Tuple

from enhance_subs import return_corrected_transcription
from f import (
    append_to_file,
    color,
    execute,
    max_max_workers_for_the_pp,
    write_video_id_in_cache,
)
from words import divide_the_text_by_space

MINIMUM_SUBSCRIBERS_FOR_AUTOSUB = 500000
MINIMUM_VIEWS_FOR_AUTOSUB = 100000


def get_words_by_autosub(
    video_id: str,
    language_code: str = "hi-IN",
    duration: int = 500,
    is_recognized: bool = False,
    delta_days: int = 3,
    views: int = 100000,
    subscriber: int = 1000000,
    translate: bool = True,
    source_language: str = "hi",
    destination_language: str = "en",
    max_workers_for_the_pp=5,
) -> Tuple[list, bool, bool]:
    """
    This function uses the autosub library to transcribe the audio of a video
    and return the words in the video.
    Args:
        video_id (str): The id of the video to be transcribed.
        language_code (str): The language code of the video.
        duration (int): The duration of the video.
        is_recognized (bool): Whether the video has been recognized or not.
        delta_days (int): The number of days since the video was uploaded.
        views (int): The number of views the video has.
        subscriber (int): The number of subscribers the channel has.
    Returns:
        list: A list of words in the video.
        bool: Whether the video has been recognized or not.
        bool: Whether the video has been recognized or not.
    """
    new_data = "vnd"
    audio_format = "wav"
    subtitle_folder = "subtitles"

    nop_data = "nop"

    try:
        if duration > 900 and (delta_days > 1 or subscriber < 1000000):
            print(f"the video {video_id} is too long with duration {duration}")
            return nop_data, False, is_recognized

        if duration > 1800:
            print(f"the video {video_id} is too long with duration {duration}")
            return nop_data, False, is_recognized
        if (views < MINIMUM_VIEWS_FOR_AUTOSUB) and (delta_days > 0):
            print(f"the video {video_id} has too few views {views}")
            return nop_data, False, is_recognized
        if subscriber < MINIMUM_SUBSCRIBERS_FOR_AUTOSUB and delta_days > 0:
            print(f"the video {video_id} has too few subscribers {subscriber}")
            return nop_data, False, is_recognized
        if delta_days > 3:
            print(f"the video {video_id} is too old with delta days {delta_days}")
            return nop_data, False, is_recognized
        if delta_days < 1 and subscriber < 1000000:
            print(
                f"""{color.GREEN}{color.BOLD}Video {video_id} has no subtitles
                and has been skipped{color.END}"""
            )
            write_video_id_in_cache(video_id, "recent")
            return new_data, False, is_recognized

        if max_workers_for_the_pp > max_max_workers_for_the_pp:

            return new_data, False, is_recognized
        execute(
            [
                "yt-dlp",
                "-N",
                "10",
                "--extract-audio",
                "--audio-format",
                audio_format,
                "--audio-quality",
                "0",
                "--no-playlist",
                "--no-post-overwrites",
                "--no-check-certificate",
                "--no-warnings",
                "--match-filter",
                "!is_live",
                "--output",
                f"audio/{video_id}.%(ext)s",
                f"https://www.youtube.com/watch?v={video_id}",
            ]
        )
        if not os.path.exists(f"audio/{video_id}.{audio_format}"):
            print("video not downloaded")
            return new_data, False, is_recognized
        if not os.path.exists(subtitle_folder):
            os.makedirs(subtitle_folder)

        if translate:
            subtitle_filename = (
                f"{subtitle_folder}/{video_id}.{destination_language}.json"
            )
            from googletrans import Translator

            translator = Translator()

            def translate_word(*args, **kwargs):
                """
                This function translates the text to english.
                """
                try:
                    return translator.translate(*args, **kwargs).text
                except Exception as error:  # pylint: disable=broad-except
                    print(error)
                    return "This is already in english."

        else:
            subtitle_filename = f"{subtitle_folder}/{video_id}.hi-in.json"
        if subscriber > 10000 and delta_days < 30:
            translate = False

        try:
            if not os.path.exists(subtitle_filename):

                if translate:
                    execute(
                        [
                            "autosub",
                            "-i",
                            f"audio/{video_id}.{audio_format}",
                            "-S",
                            language_code,
                            "-F",
                            "json",
                            "-D",
                            "en",
                            "-SRC",
                            "hi",
                            "-o",
                            f"{subtitle_folder}/{video_id}.json",
                            "--drop-trailing-silence",
                            "--drop-empty-regions",
                            "--energy-threshold",
                            "15",
                            "-sc",
                            "12",
                        ]
                    )

                else:
                    execute(
                        [
                            "autosub",
                            "-i",
                            f"audio/{video_id}.{audio_format}",
                            "-S",
                            language_code,
                            "-F",
                            "json",
                            "-o",
                            f"{subtitle_folder}/{video_id}.json",
                            "--drop-trailing-silence",
                            "--drop-empty-regions",
                            "--energy-threshold",
                            "15",
                            "-sc",
                            "12",
                        ]
                    )

        except Exception as error:  # pylint: disable=broad-except
            print(error)
            # log the traceback and error
            append_to_file(
                f"logs/{video_id}.txt",
                f"{datetime.now()} - {error} - {traceback.format_exc()}",
            )
            return [], False, is_recognized
        try:
            try:
                with open(subtitle_filename, "r", encoding="utf-8") as file:
                    data = json.load(file)

            except Exception as error:  # pylint: disable=broad-except
                print(error)
                return [], False, is_recognized
            new_data = [
                {
                    "text": region["content"],
                    "start": region["start"],
                    "end": region["end"],
                }
                for region in data
                if region["content"] != ""
            ]
            # remove the json file and the audio file
            os.remove(f"audio/{video_id}.{audio_format}")
            # os.remove(f"{subtitle_folder}/{video_id}.en.json")
            if not translate:
                for word in new_data:
                    word["text"] = word["text"].lower()
                new_data = [word for word in new_data if word["text"]]
                print("the video has more than 1 million subscribers")
                print("correcting the words using the cohere api")
                for word in new_data:
                    translated_word = translate_word(
                        word["text"], src=source_language, dest=destination_language
                    )
                    corrected_transcription = return_corrected_transcription(
                        word["text"], translated_word
                    )
                    word["text"] = corrected_transcription
            new_data = divide_the_text_by_space(new_data)
            print(f"{video_id} has been downloaded and transcribed")
            print(f"{len(new_data)} words have been found")
            print(f"{new_data}")
            return new_data, False, is_recognized
        except Exception as error:  # pylint: disable=broad-except
            print(
                f"""{color.RED}{color.BOLD}Error in transcribing the video,error {error}
in video {video_id} {color.END}"""
            )
            return [], False, is_recognized
    except Exception as error:  # pylint: disable=broad-except
        print(
            f"""{color.RED}{color.BOLD}Error in transcribing the video, error {error}
in video {video_id} {color.END}"""
        )
        return [], False, is_recognized
