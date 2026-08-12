"""Tests for windowing and label assignment."""

from __future__ import annotations

import pytest

from sponsorblock_ai.constants import LABEL2ID
from sponsorblock_ai.data.windowing import assign_label, make_windows
from tests.conftest import make_segment, make_words


def test_assign_label_majority_overlap():
    # 8s window: [2,10). Segment covers 3–9 (6s out of 8s = 75%) → sponsor
    assert assign_label(2.0, 10.0, [make_segment(3.0, 9.0)]) == "sponsor"


def test_assign_label_below_threshold():
    # 10s window: [0,10). Segment covers 0–4 (40%) → none
    assert assign_label(0.0, 10.0, [make_segment(0.0, 4.0)]) == "none"


def test_assign_label_no_segments():
    assert assign_label(0.0, 10.0, []) == "none"


def test_make_windows_basic():
    words = make_words([f"w{i}" for i in range(20)], word_dur=1.0)
    segs = [make_segment(5.0, 10.0, "sponsor")]
    windows = make_windows(words, segs, window_size=5, stride=5)
    assert len(windows) == 4  # 20 words / 5 stride = 4
    for w in windows:
        assert "text" in w
        assert "label" in w
        assert w["label"] in LABEL2ID


def test_make_windows_labels():
    words = make_words([f"w{i}" for i in range(10)], word_dur=1.0)
    # Full window [0,10) labeled sponsor by segment [0,10)
    segs = [make_segment(0.0, 10.0, "sponsor")]
    windows = make_windows(words, segs, window_size=10, stride=10)
    assert windows[0]["label"] == "sponsor"
    assert windows[0]["label_id"] == LABEL2ID["sponsor"]


def test_make_windows_empty():
    assert make_windows([], [], window_size=5, stride=5) == []


def test_make_windows_stride_overlap():
    words = make_words(list("abcdefghij"), word_dur=1.0)
    windows = make_windows(words, [], window_size=4, stride=2)
    # i=0,2,4,6,8 → 5 windows
    assert len(windows) == 5


def test_window_start_end():
    words = make_words(["hello", "world"], word_dur=2.0)
    windows = make_windows(words, [], window_size=2, stride=2)
    assert windows[0]["start"] == pytest.approx(0.0)
    assert windows[0]["end"] == pytest.approx(4.0)  # last word ends at 0+2+2=4
