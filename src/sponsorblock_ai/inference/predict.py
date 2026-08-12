"""Core inference: video URL/ID → list of detected segments."""

from __future__ import annotations

import logging
from typing import TypedDict

from sponsorblock_ai.constants import ID2LABEL
from sponsorblock_ai.data.transcript import fetch_transcript
from sponsorblock_ai.data.windowing import make_windows
from sponsorblock_ai.inference.silence import refine_boundaries

logger = logging.getLogger(__name__)


class DetectedSegment(TypedDict):
    start: float
    end: float
    category: str
    confidence: float


def _merge_adjacent(
    segments: list[DetectedSegment], gap_tolerance: float = 2.0
) -> list[DetectedSegment]:
    """Merge consecutive windows that share the same category."""
    if not segments:
        return []
    merged: list[DetectedSegment] = [dict(segments[0])]
    for seg in segments[1:]:
        last = merged[-1]
        if seg["category"] == last["category"] and seg["start"] - last["end"] <= gap_tolerance:
            last["end"] = seg["end"]
            last["confidence"] = (last["confidence"] + seg["confidence"]) / 2
        else:
            merged.append(dict(seg))
    return merged


def predict_video(
    video_id: str,
    model=None,
    tokenizer=None,
    model_id: str | None = None,
    window_size: int = 128,
    stride: int = 64,
    confidence_threshold: float = 0.5,
    refine: bool = True,
) -> list[DetectedSegment]:
    """Detect sponsor segments in a YouTube video.

    Args:
        video_id: YouTube video ID (11 chars).
        model: Pre-loaded model (loaded from hub if None).
        tokenizer: Pre-loaded tokenizer (loaded from hub if None).
        model_id: Override HF hub model id.
        window_size: Transcript window size in words.
        stride: Window stride.
        confidence_threshold: Min confidence to keep a segment.
        refine: Snap boundaries to silence.

    Returns:
        List of DetectedSegment dicts sorted by start time.
    """
    import torch  # type: ignore
    import torch.nn.functional as F  # type: ignore

    from sponsorblock_ai.model.architecture import load_model_for_inference

    if model is None or tokenizer is None:
        model, tokenizer = load_model_for_inference(model_id)

    model.eval()

    result = fetch_transcript(video_id)
    if result is None or not result["words"]:
        logger.warning("No transcript available for %s", video_id)
        return []

    words = result["words"]
    windows = make_windows(words, segments=[], window_size=window_size, stride=stride)
    if not windows:
        return []

    texts = [w["text"] for w in windows]
    enc = tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors="pt")

    with torch.no_grad():
        logits = model(**enc).logits
        probs = F.softmax(logits, dim=-1)

    detected: list[DetectedSegment] = []
    for i, window in enumerate(windows):
        label_id = int(probs[i].argmax())
        category = ID2LABEL[label_id]
        if category == "none":
            continue
        confidence = float(probs[i][label_id])
        if confidence < confidence_threshold:
            continue
        detected.append(
            DetectedSegment(
                start=window["start"],
                end=window["end"],
                category=category,
                confidence=round(confidence, 4),
            )
        )

    merged = _merge_adjacent(detected)

    if refine:
        merged = refine_boundaries(merged, words)

    return sorted(merged, key=lambda s: s["start"])
