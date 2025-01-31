"""This module is used to like or dislike or undo the votes on the segments."""

import sys
from concurrent.futures import ThreadPoolExecutor

from sb_api import post_view, post_vote, uuids_from_sbb


def vote_on_type_pui(vote_type, url=None):
    """
    Vote on the segments of the given type.

    :param vote_type: The vote
    :param url: The url of the segment
    :return: None
    """
    if url is None:

        print("Please enter a url")
        return
    uuids = uuids_from_sbb(url)
    with ThreadPoolExecutor() as executor:
        for uuid in uuids:
            executor.submit(post_vote, uuid, vote_type)


def view_all_pui(url):
    """
    It takes a URL, gets all the UUIDs from that URL, and then posts view to those UUIDs

    :param url: the url of the sbb page you want to view all the pui's from
    """
    uuids = uuids_from_sbb(url)

    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(post_view, uuids)


def main(post_type, url, vote_type=None):
    """
    calls the appropriate function

    :param post_type: This is the type of post you want to make.
    :param url: The url of the post you want to vote on
    :param vote_type: upvote or downvote
    """
    if post_type == "vote":
        vote_on_type_pui(vote_type, url)
    elif post_type == "view":
        view_all_pui(url)
    elif post_type == "all":
        pages = list(range(3000))
        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(a, pages)
    else:
        print("Invalid post type")


def a(page, username="NN-Block"):
    """
    :param page: The page number of the user's profile
    :param username: The username of the user you want to view the posts of
    defaults to NN-Block (optional)
    """
    url = f"https://sb.ltn.fi/username/{username}/?page={page}"
    uuids = uuids_from_sbb(url)
    print(uuids)
    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(post_view, uuids)


if __name__ == "__main__":

    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Invalid number of arguments")
