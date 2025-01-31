from yt_api import duration_from_video_id
from silence import return_silence_segments
from youtube_transcript_api_words import get_words
import json
import sys
import webbrowser
from urllib.parse import quote

TRANSCRIPT_TYPES = {
    "AUTO_MANUAL": {
        "label": "Auto-generated (fallback to manual)",
        "type": "auto",
        "fallback": "manual",
    },
    "MANUAL_AUTO": {
        "label": "Manual (fallback to auto-generated)",
        "type": "manual",
        "fallback": "auto",
    },
}


def main(video_id, min_silence_duration=5, duration=None):
    ts_type_id = "AUTO_MANUAL"
    # ts_type_id = "MANUAL_AUTO"
    words, is_generated = get_words(
        video_id,
        transcript_type=TRANSCRIPT_TYPES[ts_type_id]["type"],
        fallback=TRANSCRIPT_TYPES[ts_type_id]["fallback"],
    )

    if duration is None:
        duration = duration_from_video_id(video_id)

    (
        intro_segment,
        outro_segments,
        filler_segments,
        intro_length,
        outro_length,
        total_filler_duration,
        total_silence_duration,
        number_of_silence,
        number_of_silence_filler,
        ignore,
    ) = return_silence_segments(words, min_silence_duration, duration, is_generated)

    print(f"{intro_segment}")
    print(f"{outro_segments}")
    print(f"{filler_segments}")
    print(f"{intro_length}")
    print(f"{outro_length}")
    print(f"{total_filler_duration}")
    print(f"{total_silence_duration}")
    print(f"{number_of_silence}")
    print(f"{number_of_silence_filler}")
    print(f"{ignore}")

    submit_segments = intro_segment + filler_segments + outro_segments

    if len(submit_segments) == 0:

        print("No silence detected")
        return

    json_data = quote(json.dumps(submit_segments))
    link = f"https://www.youtube.com/watch?v={video_id}#segments={json_data}"

    try:
        import pyperclip

        pyperclip.copy(link)

        webbrowser.open(link)
    except Exception as e:  # pylint: disable=broad-except



        print(e)
        print("Could not open link in browser")
        print(link)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python3 find_silence.py <video_id>")
        main("MJkpbyonZZk", 1)
    elif len(sys.argv) == 2:
        main(sys.argv[1],1)
    elif len(sys.argv) == 3:
        main(sys.argv[1], int(sys.argv[2]))
