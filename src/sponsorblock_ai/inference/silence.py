"""Silence-based boundary refinement.

Salvaged + rewritten from archive audio/silence.py.
"""

from __future__ import annotations

from sponsorblock_ai.data.transcript import Word

Segment = dict  # {start, end, category, confidence}


def _gap_before(words: list[Word], index: int) -> float:
    """Return silence gap before words[index] (0 if index == 0)."""
    if index == 0:
        return 0.0
    return words[index]["start"] - words[index - 1]["end"]


def _gap_after(words: list[Word], index: int) -> float:
    """Return silence gap after words[index] (0 if last word)."""
    if index >= len(words) - 1:
        return 0.0
    return words[index + 1]["start"] - words[index]["end"]


def _nearest_silence_before(
    words: list[Word], boundary: float, search_window: float = 3.0, min_gap: float = 0.3
) -> float:
    """Snap boundary backward to nearest silence >= min_gap within search_window."""
    for i in range(len(words) - 1, -1, -1):
        if words[i]["end"] < boundary - search_window:
            break
        if words[i]["end"] <= boundary and _gap_after(words, i) >= min_gap:
            return words[i]["end"]
    return boundary


def _nearest_silence_after(
    words: list[Word], boundary: float, search_window: float = 3.0, min_gap: float = 0.3
) -> float:
    """Snap boundary forward to nearest silence >= min_gap within search_window."""
    for i, word in enumerate(words):
        if word["start"] > boundary + search_window:
            break
        if word["start"] >= boundary and _gap_before(words, i) >= min_gap:
            return word["start"]
    return boundary


def refine_boundaries(
    segments: list[Segment],
    words: list[Word],
    search_window: float = 3.0,
    min_gap: float = 0.3,
) -> list[Segment]:
    """Snap segment start/end times to nearest silence boundary.

    Args:
        segments: Detected segments [{start, end, category, confidence}].
        words: Word-timed transcript.
        search_window: Max seconds to search for a silence.
        min_gap: Minimum gap duration to count as silence.

    Returns:
        Segments with refined boundaries (copy; originals unchanged).
    """
    if not words:
        return segments

    refined = []
    for seg in segments:
        new_start = _nearest_silence_before(words, seg["start"], search_window, min_gap)
        new_end = _nearest_silence_after(words, seg["end"], search_window, min_gap)
        if new_end > new_start:
            refined.append({**seg, "start": round(new_start, 3), "end": round(new_end, 3)})
        else:
            refined.append(seg)
    return refined
