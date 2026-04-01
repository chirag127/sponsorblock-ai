import os
import random
import subprocess

from f import (WORKING_DIRECTORY, append_to_file,
               delete_all_files_in_directory, return_already_run_videos,
               write_to_file)
from gist_api import get_from_gist, write_to_gist
from snippets_api import (get_raw_snippet_content_by_id_or_title,
                          update_snippet_by_snippet_title)

AR_GIST_ID = "1b61ccaa59c5523f445455e9281658a6"


def delete_recent(segment_type="recent"):
    """Delete recent files."""

    remote_file_name = f"already_run_{segment_type}.txt"

    print("remote file name:", remote_file_name)

    local_file_name = f"already_run/already_run_{segment_type}.txt"

    print("local file name:", local_file_name)
    if segment_type == "recent":

        write_to_file(local_file_name, "")

        if random.random() < 0.05:

            write_to_gist(AR_GIST_ID, remote_file_name, "12345678912")


def write_to_the_remote_file(
    remote_file_name, gist_id, already_run_video_ids_data_for_gist, gitlab
):
    print(f"writing to remote file {remote_file_name}")

    if gitlab:
        update_snippet_by_snippet_title(
            remote_file_name, already_run_video_ids_data_for_gist
        )
    else:

        write_to_gist(
            gist_id, remote_file_name, already_run_video_ids_data_for_gist, tries=1
        )

    print(f"wrote to remote file {remote_file_name}")


def get_from_the_remote_file(gist_id, remote_file_name, gitlab):
    if gitlab:
        return get_raw_snippet_content_by_id_or_title(snippet_title=remote_file_name)

    else:
        return get_from_gist(gist_id, remote_file_name, tries=1, acc="FacebookAI")


def delete_bad_files():
    delete_all_files_in_directory("/tmp")

    delete_all_files_in_directory("audio")

    delete_all_files_in_directory("subtitles")

    for file in os.listdir():
        if file.endswith(".json"):
            os.remove(file)

    subprocess.call(["rm", "sponsorTimes.csv"])

    subprocess.call(["find", ".", "-name", "sponsorTimes*", "-delete"])


def sync_already_run(
    segment_type="auto",
    file_number=None,
    can_write=False,
    write_remote=False,
    gitlab=True,
):
    # sourcery skip: low-code-quality
    """syncs already run videos between local and remote in gist and
    updates the local file and the gist"""
    min_vid = 300000
    number_of_files = 10
    if segment_type == "auto" and file_number is None:

        if (
            random.random() < 0.0001 or len(return_already_run_videos()) < min_vid
        ) and can_write is False:
            for i in range(1, number_of_files + 1):
                sync_already_run(
                    segment_type, i, can_write=True, write_remote=write_remote
                )

        for i in range(1, number_of_files + 1):
            sync_already_run(
                "auto", i, can_write=can_write, write_remote=write_remote, gitlab=gitlab
            )

        return

    if (
        segment_type == "auto"
        and random.random() > 0.01
        and file_number < number_of_files
        and can_write is False
        and write_remote is False
    ):

        print("skipping file number", file_number)

        return

    if segment_type == "auto":

        gist_id = "1b61ccaa59c5523f445455e9281658a6"

    else:
        gist_id = AR_GIST_ID

    print(f"saving files in {WORKING_DIRECTORY}")

    os.chdir(WORKING_DIRECTORY)

    print("syncing already run videos")

    if file_number:

        remote_file_name = f"already_run_{segment_type}_{file_number}.txt"

    else:

        remote_file_name = f"already_run_{segment_type}.txt"

    print("remote file name:", remote_file_name)

    local_file_name = f"already_run/already_run_{segment_type}.txt"

    print("local file name:", local_file_name)

    print(f"getting remote file {remote_file_name}")

    already_run_video_ids_data = get_from_the_remote_file(
        gist_id, remote_file_name, gitlab
    )

    print(f"got remote file {remote_file_name}")

    print(f"got {len(already_run_video_ids_data.splitlines())} videos")

    print(f"appending local file {local_file_name}")

    append_to_file(local_file_name, f"\n{already_run_video_ids_data}\n")

    print(f"appended local file {local_file_name}")

    print(f"getting local file {local_file_name}")

    already_run_video_ids = return_already_run_videos(segment_type)

    print(f"got local file {local_file_name}")

    print(
        "number of already run videos:",
        len(already_run_video_ids),
        "in",
        local_file_name,
    )

    if (
        segment_type == "auto"
        and random.random() > 0.05
        and file_number < number_of_files
        and can_write is False
        and write_remote is False
    ):

        return

    good_already_run_video_ids = [
        video_id for video_id in already_run_video_ids if len(video_id) == 11
    ]

    print(
        "number of already run videos:",
        len(good_already_run_video_ids),
        "in",
        local_file_name,
        "with 11 characters",
    )

    good_already_run_video_ids = list(set(good_already_run_video_ids))

    print(
        "number of already run videos:",
        len(good_already_run_video_ids),
        "in",
        local_file_name,
        "without duplicates",
    )
    already_run_video_ids_data = "\n".join(good_already_run_video_ids)

    print(
        "number of already run videos:",
        len(already_run_video_ids_data.split("\n")),
        "in",
        local_file_name,
    )
    if file_number and len(good_already_run_video_ids) > min_vid:

        already_run_video_ids_data_for_gist = (
            get_the_already_run_video_ids_data_for_gist(
                good_already_run_video_ids, number_of_files, file_number
            )
        )

    else:
        already_run_video_ids_data_for_gist = already_run_video_ids_data

    if len(already_run_video_ids_data.split("\n")) > 30000 and segment_type == "recent":
        delete_recent(segment_type)
        already_run_video_ids_data = "12345678912"

    print(
        f"writing {len(already_run_video_ids_data.splitlines())} ",
        f"lines to {local_file_name}",
    )

    write_to_file(local_file_name, already_run_video_ids_data)

    print(f"wrote to local file {local_file_name}")

    if (
        random.random() < 0.1
        or (write_remote and gitlab)
        or file_number == number_of_files
    ):
        write_to_the_remote_file(
            remote_file_name,
            gist_id,
            already_run_video_ids_data_for_gist,
            gitlab=gitlab,
        )

    else:

        print(f"skipping writing to remote file {remote_file_name}")

    print("synced already run videos")

    try:
        delete_bad_files()
    except Exception as error:  # pylint: disable=broad-except
        print(error)


# TODO Rename this here and in `sync_already_run`
def get_the_already_run_video_ids_data_for_gist(
    good_already_run_video_ids, number_of_files, file_number
):
    chunk_size = len(good_already_run_video_ids) // number_of_files

    print("chunk size:", chunk_size)

    start = (file_number - 1) * chunk_size

    if file_number == number_of_files + 1:
        end = len(good_already_run_video_ids) - 100000

    else:
        end = file_number * chunk_size

    print("start:", start)
    print("end:", end)

    good_already_run_video_ids = good_already_run_video_ids[start:end]

    return "\n".join(good_already_run_video_ids)


if __name__ == "__main__":
    sync_already_run()
