import traceback
from f import PING_TIMEOUT_TIME, print_status_and_text_from_response
from reques import get_url, get_urls
from reques import TIMEOUT_TIME


def get_location(proxy_addresses=None):
    """Get location of the machine from the ip address."""

    for proxy_address in proxy_addresses or [None]:

        if proxy_address is not None:

            print(f"Using proxy: {proxy_address}")

            proxies = {"http": proxy_address, "https": proxy_address}

            timeout = 3

        else:

            proxies = None

            timeout = TIMEOUT_TIME

        print(f"Getting location from ip address with proxy: {proxy_address}")
        response = get_url(
            "https://ipapi.co/json/",
            proxies=proxies,
            timeout=timeout,
        )
        if response.ok:
            print("Successfully got location from ip address")
            print(response.json())

        else:
            print("Failed to get location from ip address")
            print_status_and_text_from_response(response)
            continue


def get_live_urls(urls, timeout=PING_TIMEOUT_TIME):
    """Returns the live urls."""
    try:
        instances = []
        responses = get_urls(urls, timeout=timeout)
        for response, url in zip(responses, urls):
            if response.ok:
                url = response.history[0].url if response.history else response.url
                # remove the trailing slash
                if url.endswith("/"):
                    url = url[:-1]
                instances_with_elapsedtime = (url, response.elapsed.total_seconds())
                instances.append(instances_with_elapsedtime)
        instances.sort(key=lambda x: x[1])

        return [instance[0] for instance in instances]

    except Exception as error:  # pylint: disable=broad-except
        print(error)
        traceback.print_exc()
        return get_live_urls(urls, timeout=timeout * 2)
