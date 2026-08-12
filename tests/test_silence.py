"""Tests for silence boundary refinement."""

from __future__ import annotations

import pytest

from sponsorblock_ai.inference.silence import refine_boundaries
from tests.conftest import make_words


def _seg(start, end, cat="sponsor"):
    return {"start": start, "end": end, "category": cat, "confidence": 0.9}


def test_refine_snaps_to_silence():
    # Words at [0,1], [2,3], [6,7], [8,9]
    # Gap [3,6] = 3s silence
    words = [
        {"text": "a", "start": 0.0, "end": 1.0},
        {"text": "b", "start": 2.0, "end": 3.0},
        {"text": "c", "start": 6.0, "end": 7.0},
        {"text": "d", "start": 8.0, "end": 9.0},
    ]
    seg = _seg(4.0, 9.0)  # start inside silence [3,6]
    refined = refine_boundaries([seg], words)
    # Should snap start to end of "b" = 3.0
    assert refined[0]["start"] == pytest.approx(3.0)


def test_refine_no_words_passthrough():
    seg = _seg(5.0, 10.0)
    refined = refine_boundaries([seg], [])
    assert refined[0]["start"] == 5.0
    assert refined[0]["end"] == 10.0


def test_refine_preserves_category():
    words = make_words(list("abcde"), word_dur=1.0)
    seg = _seg(1.0, 4.0, cat="intro")
    refined = refine_boundaries([seg], words)
    assert refined[0]["category"] == "intro"


def test_refine_multiple_segments():
    words = make_words(list("abcdefghij"), word_dur=1.0)
    segs = [_seg(0.0, 3.0, "sponsor"), _seg(6.0, 9.0, "outro")]
    refined = refine_boundaries(segs, words)
    assert len(refined) == 2
