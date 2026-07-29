import os
from concurrent import futures

from f import WORKING_DIRECTORY
from yt_api import video_ids_from_main_id


def remove_dead_ci():
    """
    Removes all the dead channel IDs from the ci.txt file
    """
    filename = "ci.txt"
    full_path = os.path.join(WORKING_DIRECTORY, filename)
    with open(full_path, "r", encoding="utf-8") as file:
        ids = file.read().splitlines()
    print("Got IDs from file")

    with futures.ThreadPoolExecutor(max_workers=1000) as executor:
        the_futures = [executor.submit(video_ids_from_main_id, id) for id in ids]

        for _ in futures.as_completed(the_futures):
            pass

    print("Got video IDs from API")

    with open(full_path, "w", encoding="utf-8") as file:

        for id, the_futures in zip(ids, the_futures):
            if the_futures.result():
                file.write(id + "\n")


if __name__ == "__main__":
    remove_dead_ci()
