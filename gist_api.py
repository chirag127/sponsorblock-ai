"""
Gist functions.
"""
import time
from f import (
    print_status_and_text_from_response,
    wait_for_time_between_1_and_specified_time,
)

from reques import request_url, get_url


def return_lines_from_gist(gist_id, file_name):
    """Return lines from gist."""
    text = get_from_gist(gist_id, file_name)
    return text.splitlines()


def write_to_gist(gist_id, filename, content, tries=5):
    """Update a gist with the given content"""
    url = f"https://api.github.com/gists/{gist_id}"

    bearer = "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"

    headers = {"Authorization": f"token {bearer}"}

    data = {"files": {filename: {"content": content}}}

    if tries == 0:
        print("Failed to update gist")
        return

    try:
        response = request_url("patch", url, json=data, headers=headers, timeout=60)

        if response.ok:
            print("Gist updated successfully")
            return
        print("Error in updating gist")
        print_status_and_text_from_response(response)
        wait_for_time_between_1_and_specified_time(5)

        write_to_gist(gist_id, filename, content, tries - 1)

    except Exception as error:  # pylint: disable=broad-except
        print("Error updating gist: ", error)
        wait_for_time_between_1_and_specified_time(5)
        return write_to_gist(gist_id, filename, content, tries - 1)


def get_from_gist(gist_id, file_name, tries=3, acc="chirag127"):
    """Return text from gist."""
    url = f"https://gist.githubusercontent.com/{acc}/{gist_id}/raw/{file_name}"

    if tries == 0:
        return ""

    response = get_url(url)
    if response.ok:
        return response.text
    print(f"Failed to get lines from gist: {gist_id}")
    print_status_and_text_from_response(response)
    print("retrying in 1 second")
    time.sleep(1)
    return get_from_gist(gist_id, file_name, tries=tries - 1)
