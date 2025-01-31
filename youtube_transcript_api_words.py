import json
import os
import re
from functools import lru_cache
import traceback

import requests
from youtube_transcript_api import (
    CouldNotRetrieveTranscript,
    TooManyRequests,
    YouTubeRequestFailed,
    YouTubeTranscriptApi,
)

from f import wait_for_time_between_1_and_specified_time
from free_proxy import FreeProxy
from shared import CustomTokens
from words import get_words_from_video_info

PROFANITY_RAW = "[ __ ]"  # How YouTube transcribes profanity
PROFANITY_CONVERTED = "*****"  # Safer version for tokenizing


NUM_DECIMALS = 3

# https://www.fincher.org/Utilities/CountryLanguageList.shtml
# https://lingohub.com/developers/supported-locales/language-designators-with-regions
LANGUAGE_PREFERENCE_LIST = [
    "en-GB",
    "en-US",
    "en-CA",
    "en-AU",
    "en-NZ",
    "en-ZA",
    "en-IE",
    "en-IN",
    "en-JM",
    "en-BZ",
    "en-TT",
    "en-PH",
    "en-ZW",
    "en",
]


def Diff(li1, li2):
    return [i for i in li1 + li2 if i not in li1 or i not in li2]


language_code_file = os.path.join(os.path.dirname(__file__), "language_codes.txt")
with open(language_code_file, "r", encoding="utf-8") as file:
    ALL_LANGUAGE_PREFERENCE_LIST = file.read().splitlines()


OTHER_LANGUAGE_PREFERENCE_LIST = Diff(
    ALL_LANGUAGE_PREFERENCE_LIST, LANGUAGE_PREFERENCE_LIST
)


def parse_transcript_json(json_data, granularity):
    # sourcery skip: low-code-quality
    if json_data["wireMagic"] != "pb3":
        raise AssertionError

    if granularity not in ("word", "chunk"):
        raise AssertionError

    parsed_transcript = []

    events = json_data["events"]

    for event_index, event in enumerate(events):
        segments = event.get("segs")
        if not segments:
            continue

        # This value is known (when phrase appears on screen)
        start_ms = event["tStartMs"]
        total_characters = 0

        new_segments = []
        for seg in segments:
            # Replace \n, \t, etc. with space
            text = " ".join(seg["utf8"].split())

            # Remove zero-width spaces and strip trailing and leading whitespace
            text = (
                text.replace("\u200b", "")
                .replace("\u200c", "")
                .replace("\u200d", "")
                .replace("\ufeff", "")
                .strip()
            )

            # Alternatively,
            # text = text.encode('ascii', 'ignore').decode()

            # Needed for auto-generated transcripts
            text = text.replace(PROFANITY_RAW, PROFANITY_CONVERTED)

            if not text:
                continue

            offset_ms = seg.get("tOffsetMs", 0)

            new_segments.append(
                {
                    "text": text,
                    "start": round((start_ms + offset_ms) / 1000, NUM_DECIMALS),
                }
            )

            total_characters += len(text)

        if not new_segments:
            continue

        if event_index < len(events) - 1:
            next_start_ms = events[event_index + 1]["tStartMs"]
            total_event_duration_ms = min(
                event.get("dDurationMs", float("inf")), next_start_ms - start_ms
            )
        else:
            total_event_duration_ms = event.get("dDurationMs", 0)

        # Ensure duration is non-negative
        total_event_duration_ms = max(total_event_duration_ms, 0)

        avg_seconds_per_character = (total_event_duration_ms / total_characters) / 1000

        num_char_count = 0
        for seg_index, seg in enumerate(new_segments):
            num_char_count += len(seg["text"])

            # Estimate segment end
            seg_end = seg["start"] + (num_char_count * avg_seconds_per_character)

            if seg_index < len(new_segments) - 1:
                # Do not allow longer than next
                seg_end = min(seg_end, new_segments[seg_index + 1]["start"])

            seg["end"] = round(seg_end, NUM_DECIMALS)
            parsed_transcript.append(seg)

    final_parsed_transcript = []
    for i, item in enumerate(parsed_transcript):

        word_level = granularity == "word"
        if word_level:
            split_text = item["text"].split()
        elif granularity == "chunk":
            # Split on space after punctuation
            split_text = re.split(r"(?<=[.!?,-;])\s+", item["text"])
            if len(split_text) == 1:
                split_on_whitespace = item["text"].split()

                if len(split_on_whitespace) >= 8:  # Too many words
                    # Rather split on whitespace instead of punctuation
                    split_text = split_on_whitespace
                else:
                    word_level = True
        else:
            raise ValueError("Unknown granularity")

        segment_end = item["end"]
        if i < len(parsed_transcript) - 1:
            segment_end = min(segment_end, parsed_transcript[i + 1]["start"])

        segment_duration = segment_end - item["start"]

        num_chars_in_text = sum(map(len, split_text))

        num_char_count = 0
        current_offset = 0
        for s in split_text:
            num_char_count += len(s)

            next_offset = (num_char_count / num_chars_in_text) * segment_duration

            word_start = round(item["start"] + current_offset, NUM_DECIMALS)
            word_end = round(item["start"] + next_offset, NUM_DECIMALS)

            # Make the reasonable assumption that min wps is 1.5
            final_parsed_transcript.append(
                {
                    "text": s,
                    "start": word_start,
                    "end": min(word_end, word_start + 1.5) if word_level else word_end,
                }
            )
            current_offset = next_offset

    return final_parsed_transcript


def list_transcripts(video_id, proxies=None, cookies=None):
    try:
        return YouTubeTranscriptApi.list_transcripts(
            video_id, proxies=proxies, cookies=cookies
        )
    except json.decoder.JSONDecodeError:
        return None


WORDS_TO_REMOVE = [
    CustomTokens.MUSIC.value,
    CustomTokens.APPLAUSE.value,
    CustomTokens.LAUGHTER.value,
]

cookies_file = "youtube.com_cookies.txt"

# file is relative to the current file

cookies_file_path = os.path.join(os.path.dirname(__file__), cookies_file)


@lru_cache(maxsize=16)
def get_words(
    video_id,
    process=True,
    transcript_type="auto",
    fallback="manual",
    filter_words_to_remove=True,
    granularity="word",
    retry_count=4,
    proxies=None,
    cookies=None,
    not_download=True,
    video_info=None,
):  # sourcery skip: low-code-quality
    """Get parsed video transcript with caching system
    returns None if not processed yet and process is False
    """

    if "finetune" in os.getcwd():
        not_download = False

    auto_generated_filepath = os.path.join("transcripts", "auto", f"{video_id}.json")

    manual_generated_filepath = os.path.join(
        "transcripts", "manual", f"{video_id}.json"
    )

    if os.path.exists(auto_generated_filepath):
        with open(auto_generated_filepath, "r") as f:
            return json.load(f), True

    if os.path.exists(manual_generated_filepath):
        with open(manual_generated_filepath, "r") as f:
            return json.load(f), False

    is_generated = False
    # NOTE: granularity='chunk' should
    # only be used for generating training data... nowhere else

    # if video_info is None:
    #     video_info = info_from_video_id(video_id)

    if video_info:

        words, is_generated = get_words_from_video_info(video_info)

        if words is not None:

            if not_download is False:
                if is_generated:
                    with open(auto_generated_filepath, "w") as f:
                        json.dump(words, f)
                else:
                    with open(manual_generated_filepath, "w") as f:
                        json.dump(words, f)

            return words, is_generated

    raw_transcript_json = None
    try:

        if retry_count <= 0:
            return None

        if process:

            transcript_list = list_transcripts(
                video_id, cookies=cookies, proxies=proxies
            )

            if transcript_list is not None:
                if transcript_type == "manual":
                    ts = transcript_list.find_manually_created_transcript(
                        ALL_LANGUAGE_PREFERENCE_LIST
                    )

                else:
                    ts = transcript_list.find_generated_transcript(
                        ALL_LANGUAGE_PREFERENCE_LIST
                    )

                is_generated = ts.is_generated
                language_of_transcript = ts.language
                language_of_transcript = language_of_transcript.lower()
                if "english" not in language_of_transcript:
                    ts = ts.translate("en")

                raw_transcript = ts._http_client.get(
                    f"{ts._url}&fmt=json3"
                ).content  # pylint: disable=protected-access

                if raw_transcript:
                    raw_transcript_json = json.loads(raw_transcript)

    except (TooManyRequests, YouTubeRequestFailed) as error:
        print("got too many requests or request failed error")
        print(error)
        wait_for_time_between_1_and_specified_time(300, 100)
        try:
            print("retrying")
            proxy_addresses = FreeProxy(https=True, rand=True, timeout=2).get()

            for proxy_address in proxy_addresses:
                print(f"trying proxy {proxy_address}")

                proxies = {"http": proxy_address, "https": proxy_address}

                try:
                    return get_words(
                        video_id=video_id,
                        process=process,
                        transcript_type=transcript_type,
                        fallback=fallback,
                        granularity=granularity,
                        retry_count=retry_count - 1,
                        proxies=proxies,
                        cookies=None,
                    )

                except Exception as e:
                    print(e)
                    print("proxy failed")
                    traceback.print_exc()
                    continue

        except Exception as second_error:  # pylint: disable=broad-except
            print("got second error", second_error)
            wait_for_time_between_1_and_specified_time(100, 10)

            get_words(
                video_id=video_id,
                process=process,
                transcript_type=transcript_type,
                fallback=fallback,
                granularity=granularity,
                retry_count=retry_count,
                proxies=None,
                cookies=None,
            )
        raise  # Cannot recover from these errors and do not mark as empty transcript

    except requests.exceptions.RequestException:  # Can recover
        print("got request exception")
        wait_for_time_between_1_and_specified_time(20, 10)
        return get_words(
            video_id=video_id,
            process=process,
            transcript_type=transcript_type,
            fallback=fallback,
            granularity=granularity,
        )

    except CouldNotRetrieveTranscript:
        pass
        # Retrying won't solve
        # Mark as empty transcript

    except json.decoder.JSONDecodeError as error:
        print("could not decode transcript with error", error)
        print(traceback.format_exc())
        wait_for_time_between_1_and_specified_time(20, 10)

        return get_words(
            video_id=video_id,
            process=process,
            transcript_type=transcript_type,
            fallback=fallback,
            granularity=granularity,
            cookies=None,
        )

    transcript_path = os.path.join("transcripts", transcript_type, f"{video_id}.json")

    if not_download is False:
        with open(transcript_path, "w", encoding="utf-8") as file:
            json.dump(raw_transcript_json, file)

    if not raw_transcript_json and fallback is not None:

        return get_words(
            video_id=video_id,
            process=process,
            transcript_type=fallback,
            fallback=None,
            granularity=granularity,
            cookies=None,
        )

    if raw_transcript_json:

        processed_transcript = parse_transcript_json(raw_transcript_json, granularity)
        if filter_words_to_remove:
            processed_transcript = list(
                filter(lambda x: x["text"] not in WORDS_TO_REMOVE, processed_transcript)
            )
    else:
        processed_transcript = raw_transcript_json  # Either None or []

    return processed_transcript, is_generated


if __name__ == "__main__":
    print(get_words("UkPCrS-H1vM", "en", "en", "en", "word"))
