"""
This script removes all the channel IDs from the ci.txt file
whose videos don't have captions,
if any one of the videos have captions then the channel ID is kept.
"""

import os
import random

from f import WORKING_DIRECTORY
from yt_api import info_from_video_id, video_ids_from_main_id


def get_all_channel_ids():
    """
    Gets all the channel IDs from the ci.txt file
    """
    filename = "ci.txt"
    full_path = os.path.join(WORKING_DIRECTORY, filename)
    with open(full_path, "r", encoding="utf-8") as file:
        ids = file.read().splitlines()
    print("Got IDs from file")
    return ids


def get_all_video_ids(channel_id):
    """
    Gets all the video IDs from the channel ID
    """
    video_ids = video_ids_from_main_id(channel_id, False)

    random.shuffle(video_ids)

    if len(video_ids) > 2:
        video_ids = video_ids[:2]


def get_all_video_info(video_ids):
    """
    Gets all the video info from the video IDs
    """
    video_infos = []

    if video_ids is None:
        return video_infos
    for video_id in video_ids:
        info = info_from_video_id(video_id)
        video_infos.append(info)
    return video_infos


def get_all_video_ids_with_captions(video_infos):
    """
    Gets all the video IDs with captions from the video info
    """
    video_ids_with_captions = []
    for info in video_infos:

        if info is None:
            continue
        if info["subtitles"] != []:
            video_ids_with_captions.append(info["video_id"])
    return video_ids_with_captions


def remove_non_caption_channel_ids(channel_ids):
    """
    Removes all the channel IDs from the ci.txt file whose videos don't have captions,
    if any one of the videos have captions then the channel ID is kept.
    """
    channel_ids_with_captions = []
    for channel_id in channel_ids:
        video_ids = get_all_video_ids(channel_id)
        video_infos = get_all_video_info(video_ids)
        video_ids_with_captions = get_all_video_ids_with_captions(video_infos)
        if len(video_ids_with_captions) > 0:
            channel_ids_with_captions.append(channel_id)
    return channel_ids_with_captions


def write_channel_ids_to_file(channel_ids):
    """
    Writes the channel IDs to the ci.txt file
    """
    filename = "ci.txt"
    full_path = os.path.join(WORKING_DIRECTORY, filename)
    with open(full_path, "w", encoding="utf-8") as file:
        for channel_id in channel_ids:
            file.write(channel_id + "\n")
    print("Wrote IDs to file")


def main():
    """
    Main function
    """
    channel_ids = get_all_channel_ids()
    channel_ids_with_captions = remove_non_caption_channel_ids(channel_ids)
    write_channel_ids_to_file(channel_ids_with_captions)


if __name__ == "__main__":
    main()
