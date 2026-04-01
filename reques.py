from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

import requests
from requests import Timeout

from config import to
from f import color

TIMEOUT_TIME = to

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_1) AppleWebKit/537.36 "
    + "(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}


class ModelResponse:  # pylint: disable=too-few-public-methods
    """The :class:`Response <Response>` object, which contains a
    server's response to an HTTP request.
    """

    def __init__(self, url, status_code=544, text="timeout"):
        self.status_code = status_code
        self.ok = self.status_code < 400  # pylint: disable=invalid-name
        self.text = text
        self.url = url


def get_single_float_from_gist(gist_id, file_name):
    """Returns the timeout time."""
    url = f"https://gist.githubusercontent.com/chirag127/{gist_id}/raw/{file_name}"

    try:

        response = requests.get(url, timeout=1)
        if response.ok:
            text = response.text
            # strip the new line character
            text = text.strip()

            return float(text)

    except Exception as error:  # pylint: disable=broad-except
        print(error)

    return get_single_float_from_gist(gist_id, file_name)


def request_url(request_type, url, timeout=TIMEOUT_TIME, **kwargs):
    # sourcery skip: inline-immediately-returned-variable
    """Sends a request to a URL and returns the response."""
    try:

        # add headers to **kwargs if they don't exist
        if "headers" not in kwargs:
            kwargs["headers"] = DEFAULT_HEADERS
        # print(f"{request_type}ing the {url}")
        response = requests.request(request_type, url, timeout=timeout, **kwargs)
        # print(f"{request_type}ed the {url}")
        print_details(response)
        return response

    except Timeout:
        print(f"""{color.RED}Timeout {url}
{request_type} request,
timeout of {timeout} seconds{color.END}""")

    except Exception as error:  # pylint: disable=broad-except

        print(f"{color.RED}\nError {url} \n{error}{color.END}")
    return ModelResponse(url)


def get_url(url, timeout=TIMEOUT_TIME, **kwargs):
    """Sends a GET request to the server."""
    return request_url("GET", url, timeout=timeout, **kwargs)


def post_url(url, timeout=TIMEOUT_TIME, **kwargs):
    """Sends a POST request to the server."""
    return request_url("POST", url, timeout=timeout, **kwargs)


def request_urls(request_type, urls, max_workers=100, timeout=TIMEOUT_TIME):
    """Returns a list of responses for a list of urls."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        responses = executor.map(
            request_url, repeat(request_type), urls, repeat(timeout)
        )

    return responses


def get_urls(urls, max_workers=100, timeout=TIMEOUT_TIME):
    """Sends a GET request to the server."""
    return request_urls("GET", urls, max_workers=max_workers, timeout=timeout)


def post_urls(urls, max_workers=100, timeout=TIMEOUT_TIME):
    """Sends a POST request to the server."""
    return request_urls("POST", urls, max_workers=max_workers, timeout=timeout)


def print_details(response):
    """Prints details of a response."""
    # print(f"time elapsed: {response.elapsed.total_seconds()} seconds")

    pass


def get_url_with_retry(url, timeout=TIMEOUT_TIME, retries=10, **kwargs):
    """
    Returns a get response for a url with a time out of 10 seconds.
    if the url is not reachable then retry the url.
    """
    for _ in range(retries):
        response = get_url(url, timeout=timeout, **kwargs)
        if response.ok:
            return response
    return response


def get_urls_with_retry(urls, max_workers=100, timeout=TIMEOUT_TIME, retries=10):
    """
    Returns a list of get responses for a list of urls.
    if the url is not reachable then retry the url.
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        responses = executor.map(
            get_url_with_retry, urls, repeat(timeout), repeat(retries)
        )
    return responses


def get_json_from_url(url, **kwargs):
    """Returns a json response for a url."""
    response = get_url(url, **kwargs)
    return response.json()


def post_json_from_url(url, **kwargs):
    """Returns a json response for a url."""
    response = post_url(url, **kwargs)
    return response.json()


if __name__ == "__main__":
    print(get_url("http://www.google.com/", timeout=6))
