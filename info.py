"""
This file is used to disable warnings for users with warnings.
"""
import sys
from concurrent.futures import ThreadPoolExecutor

from f import append_to_file, user_ids_from_segment_type
from reques import post_url
from sb_api import info_from_user_id

print("start")


def main(user_id):

    """
    Main function to be called for each user_id
    :param user_id:
    :return:
    """
    info = info_from_user_id(user_id)
    warnings = info["warnings"]
    public_user_id = info["userID"]
    reputation = info["reputation"]
    user_name = info["userName"]

    if reputation > 0:
        append_to_file(
            "txt/reputation1.txt",
            f"{reputation}\t{user_id}\t{public_user_id}\t{user_name}\n",
        )

        if user_name != public_user_id:
            append_to_file(
                "txt/reputation2.txt",
                f"{reputation}\t{user_id}\t{public_user_id}\t{user_name}\n",
            )

    if warnings > 0:
        _extracted_from_main_27(user_id, warnings, public_user_id)
    return warnings


# TODO Rename this here and in `main`
def _extracted_from_main_27(user_id, warnings, public_user_id):
    append_to_file(
        "txt/warnings.txt",
        f"{user_id} has {warnings} warnings with public user id {public_user_id}\n",
    )

    url = "https://sponsor.ajay.app/api/warnUser"

    data = {"userID": user_id, "enabled": False}

    response = post_url(url, json=data)
    print(response.text)

    if response.ok:
        append_to_file(
            "txt/warnings.txt",
            f"""{user_id} has {warnings} warnings with public user id {public_user_id}
                and disabled""",
        )
    else:
        append_to_file(
            "txt/warnings.txt",
            f"""{user_id} has {warnings} warnings with public user id {public_user_id}
                and failed to disable""",
        )


TYPE = sys.argv[1]

user_ids = user_ids_from_segment_type(TYPE)

with ThreadPoolExecutor(max_workers=1000) as executor:
    responses = executor.map(main, user_ids)
