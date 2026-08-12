"""Shared pytest fixtures and tiny synthetic helpers."""

from __future__ import annotations


def make_words(texts: list[str], start: float = 0.0, word_dur: float = 1.0):
    """Build a synthetic Word list from a list of tokens."""
    words = []
    t = start
    for txt in texts:
        words.append({"text": txt, "start": round(t, 3), "end": round(t + word_dur, 3)})
        t += word_dur
    return words


def make_segment(start: float, end: float, category: str = "sponsor"):
    return {"startTime": start, "endTime": end, "category": category}
