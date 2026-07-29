from f import (print_status_and_text_from_response,
               wait_for_time_between_1_and_specified_time)
from reques import get_url, post_url, request_url

GITLAB_TOKEN = "glpat-gb58VsQpQa3NaBCSAe_k"
git_url = "https://gitlab.com/api/v4/snippets"


def list_all_snippets_for_user():
    """List all snippets for a user"""
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}

    responses = []
    response = get_url(git_url, headers=headers)

    if response.ok:
        responses.extend(response.json())
    else:

        print_status_and_text_from_response(response)

    # sort the snipped by title
    # responses.sort(key=lambda x: x["title"])

    # return responses

    return responses


def get_id_of_snippet_by_title(title):
    """Get id of snippet by title"""

    try:
        snippets = list_all_snippets_for_user()
        return next(
            (snippet["id"] for snippet in snippets if snippet["title"] == title), None
        )
    except Exception as error:  # pylint: disable=broad-except
        print(error)


def get_raw_snippet_content_by_id_or_title(snippet_id=None, snippet_title=None):
    """Get raw snippet content by id or title"""
    if snippet_id is None and snippet_title is None:
        print("snippet_id or snippet_title is required")
        return "Not found11"

    if snippet_id is None:
        snippet_id = get_id_of_snippet_by_title(snippet_title)
    if snippet_id is None:
        print("Snippet not found")
        return "Not found11"
    url = f"https://gitlab.com/api/v4/snippets/{snippet_id}/raw"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    response = get_url(url, headers=headers)
    if response.ok:
        return response.text
    print_status_and_text_from_response(response)
    return "Not found11"


def get_raw_snippet_content_by_id_and_file_path(snippet_id, file_path):
    """Get raw snippet content by id and file path"""
    url = f"https://gitlab.com/api/v4/snippets/{snippet_id}/files/{file_path}/raw"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    response = get_url(url, headers=headers)
    return response.text


def create_snippet(filename, content):

    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    data = {
        "title": filename,
        "visibility": "private",
        "files": [{"content": content, "file_path": filename}],
    }
    try:

        response = post_url(git_url, headers=headers, json=data, timeout=60)

        if response.ok:
            return response.json()
        print_status_and_text_from_response(response)
        return None
    except Exception as error:  # pylint: disable=broad-except
        print(error)
        return None


def update_snippets_api(snippet_id, filename, content, tries=1, timeout=60):
    """Update a snippet with the given content"""

    url = f"https://gitlab.com/api/v4/snippets/{snippet_id}"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN, "Content-Type": "application/json"}
    data = {
        "id": snippet_id,
        "files": [{"action": "update", "file_path": filename, "content": content}],
    }
    for _ in range(tries):

        try:
            response = request_url(
                "PUT", url, json=data, headers=headers, timeout=timeout
            )

            if response.ok:
                print("snippet updated successfully")
                return
            print("problem in updating snippet")
            print_status_and_text_from_response(response)
            wait_for_time_between_1_and_specified_time(2)

            update_snippets_api(snippet_id, filename, content, tries - 1)
            delete_snippet(snippet_id)
            create_snippet(filename, content)

        except Exception as error:  # pylint: disable=broad-except

            print("Error updating snippet: ", error)
            wait_for_time_between_1_and_specified_time(2)


def update_snippet_by_snippet_title(filename, content):
    """Update a snippet by snippet title"""
    snippet_id = get_id_of_snippet_by_title(filename)
    if snippet_id:
        update_snippets_api(snippet_id, filename, content)
    else:
        print("Snippet not found")
        create_snippet(filename, content)


def delete_snippet(snippet_id=None, snippet_title=None):
    """Delete a snippet by id or title"""

    if snippet_id is None and snippet_title is None:
        print("snippet_id or snippet_title is required")
        return

    if snippet_id is None:
        snippet_id = get_id_of_snippet_by_title(snippet_title)
    if snippet_id is None:
        print("Snippet not found")
        return
    try:
        url = f"https://gitlab.com/api/v4/snippets/{snippet_id}"
        headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
        response = request_url("DELETE", url, headers=headers)
        print_status_and_text_from_response(response)
        return response
    except Exception as error:  # pylint: disable=broad-except
        print("Error deleting snippet: ", error)


def delete_snippet_by_snippet_title(snippet_title):
    """Delete a snippet by snippet title"""
    snippet_id = get_id_of_snippet_by_title(snippet_title)
    if snippet_id:
        delete_snippet(snippet_id)
    else:
        print("Snippet not found")


def get_user_agent_details(snippet_id):
    """Get user agent details"""
    url = f"https://gitlab.com/api/v4/snippets/{snippet_id}/user_agent_detail"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    response = request_url("GET", url, headers=headers)
    print_status_and_text_from_response(response)
    return response


def delete_all_snippets():
    """Delete all snippets"""
    snippets = list_all_snippets_for_user()
    for snippet in snippets:
        delete_snippet(snippet["id"])


if __name__ == "__main__":
    print(list_all_snippets_for_user())

    # for i in range(1,22):
    # delete_all_snippets()
    #     create_snippet(f"already_run_auto_{i}.txt", "12345678901")
