import requests

from f import merge_segments, return_segment


def get_skip_sponsor_api_response(video_id):
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Origin": "chrome-extension://lbkmajfgpafkmmfdppcmgdabanlobfnf",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46",
    }

    params = {
        "video_id": video_id,
    }

    response = requests.get(
        "https://gkbwcqkoc3f5wyv7ydb5si2koe0xogku.lambda-url.eu-west-2.on.aws/",
        params=params,
        headers=headers,
    )

    if (
        response.status_code == 200
        and response.json() == []
        or response.status_code != 200
    ):
        return None

    response_json = response.json()
    sponsor_segments = []
    # example response: [[407.46,426.83],[423.9,467.029]]

    if response_json == []:
        return sponsor_segments

    for sponsor in response_json:
        sponsor[0] = round(sponsor[0], 2)
        sponsor[1] = round(sponsor[1], 2)

        sponsor_segments.append(return_segment(sponsor[0], sponsor[1]))

    return sponsor_segments


if __name__ == "__main__":
    video_id = "mWUKo_0iKyc"

    response = get_skip_sponsor_api_response(video_id)

    response = merge_segments(response)

    print(response)
