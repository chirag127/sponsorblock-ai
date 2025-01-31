"""
contains the functions to
1. merge segments
2. return segment
3. return_silence_segments
"""
import traceback
from f import (
    end_of_video,
    merge_segments,
    random_choice,
    return_segment,
    user_ids_from_segment_type,
)

filler_user_ids = user_ids_from_segment_type("filler")
intro_user_ids = user_ids_from_segment_type("intro")
outro_user_ids = user_ids_from_segment_type("intro")


def return_silence_segments(
    words, min_silence_duration=5, duration=100000000, is_generated=False
):  # sourcery skip: low-code-quality
    """returns the silence segments"""
    intro_segments = []
    outro_segments = []
    filler_segments = []
    intro_length = 0
    outro_length = 0
    number_of_silence = 0
    number_of_silence_intro = 0
    number_of_silence_outro = 0
    number_of_silence_filler = 0
    total_filler_duration = 0
    total_silence_duration = 0
    ignore = False

    if not words:

        return (
            intro_segments,
            outro_segments,
            filler_segments,
            intro_length,
            outro_length,
            total_filler_duration,
            total_silence_duration,
            number_of_silence,
            number_of_silence_filler,
            ignore,
        )

    for i in range(len(words) + 1):
        if i == 0:
            start = 0
            end = words[i]["start"]
            if end - start > 0.5:
                intro_segments = [return_segment(start, end, "intro")]
                continue
        else:

            start = words[i - 1]["end"]
            if is_generated:
                start = start - 0.2
            try:
                end = words[i]["start"]
            except IndexError:
                end = end_of_video(duration)
                if end - start > 4:
                    outro_segments = [return_segment(start, end, "outro")]
                continue

            silence_time = end - start
            if silence_time > min_silence_duration:
                if start < 10:
                    start = 0
                    intro_segments = [return_segment(start, end, "intro")]
                elif end > duration - 3:
                    end = end_of_video(duration)
                    outro_segments = [return_segment(start, end, "outro")]
                    break
                else:
                    filler_segments.append(return_segment(start, end, "filler"))

    if filler_segments:
        (
            filler_segments,
            total_filler_duration,
            number_of_silence_filler,
            ignore,
        ) = return_processed_filtered_segments(
            duration,
            filler_segments,
            ignore,
        )
    if intro_segments:

        (
            intro_segments,
            intro_length,
            number_of_silence_intro,
            ignore,
        ) = return_processed_filtered_segments(duration, intro_segments, ignore)

    if outro_segments:

        (
            outro_segments,
            outro_length,
            number_of_silence_outro,
            ignore,
        ) = return_processed_filtered_segments(duration, outro_segments, ignore)

        try:
            if filler_segments and outro_segments:

                outro_and_last_filler_segments = [
                    filler_segments[-1],
                    outro_segments[0],
                ]

                (
                    outro_and_last_filler_segments,
                    total_outro_and_last_filler_duration,
                    number_of_silence_outro_and_last_filler,
                    ignore,
                ) = return_processed_filtered_segments(
                    duration,
                    outro_and_last_filler_segments,
                    ignore,
                )

                if len(outro_and_last_filler_segments) == 1:
                    if outro_and_last_filler_segments[0]["category"] == "outro":

                        total_filler_duration = (
                            total_filler_duration
                            - total_outro_and_last_filler_duration
                            + outro_length
                        )
                        filler_segments = filler_segments[:-1]
                        number_of_silence_filler = number_of_silence_filler - 1

                        outro_segments = outro_and_last_filler_segments
                        number_of_silence_outro = (
                            number_of_silence_outro_and_last_filler
                        )
                        outro_length = total_outro_and_last_filler_duration

                    else:
                        filler_segments[-1] = outro_and_last_filler_segments[0]
                        number_of_silence_filler = (
                            number_of_silence_outro_and_last_filler
                        )
                        total_filler_duration = total_filler_duration + outro_length
                        outro_segments = []
                        outro_length = 0

        except Exception as error:  # pylint: disable=broad-except
            print(error)
            traceback.print_exc()

    total_silence_duration = intro_length + outro_length + total_filler_duration

    number_of_silence = (
        number_of_silence_filler + number_of_silence_intro + number_of_silence_outro
    )

    return (
        intro_segments,
        outro_segments,
        filler_segments,
        intro_length,
        outro_length,
        total_filler_duration,
        total_silence_duration,
        number_of_silence,
        number_of_silence_filler,
        ignore,
    )


def return_processed_filtered_segments(
    duration: int,
    filler_segments: list,
    ignore: bool,
    total_silence_duration: int = 0,
    number_of_silence: int = 0,
):
    """returns the processed filtered segments"""
    # Merge the filler segments
    filler_segments = merge_segments(filler_segments, 4)
    # Iterate over filler segments
    for segment in filler_segments:
        # Get start and end of segment
        start = segment["segment"][0]
        end = segment["segment"][1]
        # If the segment is too long
        if end - start > duration * 0.2:
            # Print error message
            print(f"{start}-{end} is too long in {duration}")
            # Remove the segment from the filler segments
            filler_segments.remove(segment)
            # Set ignore to true
            ignore = True
            # Continue to next iteration
            continue

        # Add the duration of the segment to the total silence duration
        total_silence_duration += end - start
    # Add the number of silence segments to the number of silence
    number_of_silence += len(filler_segments)
    # Return the filler segments, total silence duration, number of silence, and ignore
    return filler_segments, total_silence_duration, number_of_silence, ignore


def make_silence_all_segments(
    video_id,
    url,
    sbb_url,
    title,
    duration,
    views,
    uploader_subscriber_count,
    description,
    words,
    is_generated,
    user_ids,
    user_id,
    is_recognized,
    decrease_silence_duration=False,
):  # sourcery skip: low-code-quality

    """returns the silence segments"""
    if user_id is None:
        user_id = random_choice(user_ids)
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
    ) = return_silence_segments(
        words,
        min_silence_duration=10,
        duration=duration,
        is_generated=is_generated,
    )
    if decrease_silence_duration:

        if number_of_silence == 0:
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
            ) = return_silence_segments(
                words,
                min_silence_duration=5,
                duration=duration,
                is_generated=is_generated,
            )

        if number_of_silence == 0:
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
            ) = return_silence_segments(
                words,
                min_silence_duration=3,
                duration=duration,
                is_generated=is_generated,
            )

        if number_of_silence == 0:
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
            ) = return_silence_segments(
                words,
                min_silence_duration=2,
                duration=duration,
                is_generated=is_generated,
            )

        if number_of_silence == 0:

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
            ) = return_silence_segments(
                words,
                min_silence_duration=1,
                duration=duration,
                is_generated=is_generated,
            )

        if number_of_silence == 0:
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
            ) = return_silence_segments(
                words,
                min_silence_duration=0.5,
                duration=duration,
                is_generated=is_generated,
            )

        if number_of_silence == 0:
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
            ) = return_silence_segments(
                words,
                min_silence_duration=0.25,
                duration=duration,
                is_generated=is_generated,
            )

    silence_segments = intro_segment + outro_segments + filler_segments

    intro_and_outro_segments = intro_segment + outro_segments

    if silence_segments != []:

        if (
            (
                (ignore and total_filler_duration / duration > 0.1)
                or (
                    (
                        (views > 10000 and uploader_subscriber_count > 100000)
                        or (is_generated is False)
                    )
                    and (
                        (number_of_silence_filler) > max(1 * (duration / 300), 1)
                        or total_filler_duration / duration > 0.1
                    )
                    and "live" not in title.lower()
                    and "live" not in description.lower()
                    and ignore is True
                )
            )
            or (
                (number_of_silence_filler) > max(2 * (duration / 300), 2)
                and total_filler_duration / duration > 0.15
            )
            or total_filler_duration / duration > 0.25
        ):

            print(
                f"""
video_id: {video_id}
is_recognized: {is_recognized}
title: {title}
sb_url: {sbb_url}
url: {url}
number_of_silence_filler: {number_of_silence_filler}
number_of_silence: {number_of_silence}
total_filler_duration: {total_filler_duration}
total_silence_duration: {total_silence_duration}
duration: {duration}
ignore: {ignore}
intro_length: {intro_length}
outro_length: {outro_length}"""
            )

            intro_and_outro_segments = []
            filler_segments = []

            if views <= 10000 or uploader_subscriber_count <= 100000:
                if intro_length < 10:
                    intro_and_outro_segments = intro_segment
                if outro_length < 60:
                    intro_and_outro_segments = intro_and_outro_segments + outro_segments

        if len(filler_segments) > 4 and is_recognized is False:

            filler_segments = filler_segments[:2] + filler_segments[-2:]

        if len(filler_segments) > 6:
            # only takes in first 3 filler segments
            filler_segments = filler_segments[:3] + filler_segments[-3:]

        if len(filler_segments) > 0:
            filler_segments = []
        elif intro_length < 1 and intro_length > 0:
            user_id = random_choice(intro_user_ids)
        elif outro_length < 3 and outro_length > 0:
            user_id = random_choice(outro_user_ids)

    return filler_segments + intro_and_outro_segments, user_id
