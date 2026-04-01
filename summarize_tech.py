import random
import string

from reques import post_url

# 'deviceId': 'x9h-Ep7cCliKiB412345', # 20 characters


def generate_device_id():
    return "".join(random.choices(string.ascii_letters + string.digits, k=20))


def get_response_from_summarize_tech(video_id):
    json_data = {
        "url": "https://www.youtube.com/watch?v=" + video_id,
        "deviceId": generate_device_id(),
        "idToken": None,
    }

    headers = {
        "authority": "www.summarize.tech",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://www.summarize.tech",
        "referer": "https://www.summarize.tech/www.youtube.com/watch?v=sflZWeCjdco",
        "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", '
        + '"Microsoft Edge";v="108"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46",
    }

    response = post_url(
        "https://www.summarize.tech/api/summary", headers=headers, json=json_data
    )
    return response.json()


if __name__ == "__main__":
    # video_id = "oqqWdaaTq7A"
    # print(get_response_from_summarize_tech(video_id))
    import os

    print(os.getcwd())
