"""Submit detected segments to the SponsorBlock API.

Salvaged + rewritten from archive api/sb_api.py.
Logic: build POST payload, try each mirror host in order, handle 409 (duplicate).
"""

from __future__ import annotations

import logging
import os
import random
import string
from typing import TypedDict

import httpx

from sponsorblock_ai.constants import SB_HOSTS, SB_PRIMARY_HOST
from sponsorblock_ai.inference.predict import DetectedSegment

logger = logging.getLogger(__name__)

# Extension version used as user-agent identifier
_EXT_VERSION = "5.10.0"
_USER_AGENT = f"mnjggcdmjocbbbhaepdhchncahnbgone/v{_EXT_VERSION}"


class SubmitResult(TypedDict):
    video_id: str
    submitted: int
    skipped: int
    errors: list[str]


def _generate_user_id(length: int = 36) -> str:
    """Generate a random alphanumeric private user ID."""
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=length))


def build_submit_url(
    video_id: str,
    host: str = SB_PRIMARY_HOST,
) -> str:
    """Return the POST endpoint URL for skipSegments."""
    return f"{host.rstrip('/')}/api/skipSegments"


def _segment_payload(seg: DetectedSegment) -> dict:
    return {
        "segment": [round(seg["start"], 3), round(seg["end"], 3)],
        "category": seg["category"],
        "actionType": "skip",
    }


def submit_segments(
    video_id: str,
    segments: list[DetectedSegment],
    user_id: str | None = None,
    video_duration: float = 0.0,
    hosts: list[str] = SB_HOSTS,
    timeout: float = 30.0,
) -> SubmitResult:
    """POST segments to SponsorBlock API.

    Args:
        video_id: YouTube video ID.
        segments: Detected segments to submit.
        user_id: Private SB user ID (generated if None; set SB_USER_ID env var).
        video_duration: Video length in seconds (0 = omit).
        hosts: Mirror list to try in order.
        timeout: Per-request timeout.

    Returns:
        SubmitResult summary.
    """
    uid = user_id or os.environ.get("SB_USER_ID") or _generate_user_id()

    payload_segments = [_segment_payload(s) for s in segments]

    if not payload_segments:
        return SubmitResult(video_id=video_id, submitted=0, skipped=0, errors=[])

    # Guard: don't submit if segments cover > 70% of video
    if video_duration > 0:
        total_seg = sum(s["end"] - s["start"] for s in segments)
        if total_seg / video_duration > 0.70:
            pct = total_seg / video_duration * 100
            logger.warning("Segments cover %.0f%% of video — refusing to submit", pct)
            return SubmitResult(
                video_id=video_id,
                submitted=0,
                skipped=len(segments),
                errors=["coverage_too_high"],
            )

    data: dict = {
        "videoID": video_id,
        "userID": uid,
        "userAgent": _USER_AGENT,
        "segments": payload_segments,
    }
    if video_duration > 0:
        data["videoDuration"] = round(video_duration, 3)

    errors: list[str] = []
    for host in hosts:
        url = build_submit_url(video_id, host)
        try:
            resp = httpx.post(url, json=data, timeout=timeout)
            if resp.status_code == 200:
                logger.info("Submitted %d segments for %s via %s", len(segments), video_id, host)
                return SubmitResult(
                    video_id=video_id,
                    submitted=len(segments),
                    skipped=0,
                    errors=[],
                )
            if resp.status_code == 409:
                logger.info("409 duplicate for %s — already submitted", video_id)
                return SubmitResult(
                    video_id=video_id,
                    submitted=0,
                    skipped=len(segments),
                    errors=["409_duplicate"],
                )
            errors.append(f"{host}: HTTP {resp.status_code} {resp.text[:120]}")
            logger.warning(
                "Failed %s via %s: %s %s", video_id, host, resp.status_code, resp.text[:120]
            )
        except httpx.RequestError as exc:
            errors.append(f"{host}: {exc}")
            logger.warning("Request error for %s via %s: %s", video_id, host, exc)

    return SubmitResult(video_id=video_id, submitted=0, skipped=len(segments), errors=errors)
