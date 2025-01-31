import contextlib
from yt_api import info_from_video_id


def get_chapters_with_start_and_end_time(chapters, video_duration):
    chapters_with_start_and_end_time = []

    for chapter in chapters:
        if chapter == chapters[-1]:
            chapters_with_start_and_end_time.append(
                {
                    "text": chapter["title"],
                    "start": chapter["start"],
                    "end": video_duration,
                }
            )
        else:
            chapters_with_start_and_end_time.append(
                {
                    "text": chapter["title"],
                    "start": chapter["start"],
                    "end": chapters[chapters.index(chapter) + 1]["start"],
                }
            )

    return chapters_with_start_and_end_time


if __name__ == "__main__":

    video_info = info_from_video_id("t8pPdKYpowI")

    livestream = video_info["livestream"]
    with contextlib.suppress(KeyError):
        print(video_info["livestream"])

        if not livestream:
            livestream = False

    print(livestream)
