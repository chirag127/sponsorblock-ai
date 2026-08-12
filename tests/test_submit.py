"""Tests for the SponsorBlock submit URL builder and segment payload."""

from __future__ import annotations

from sponsorblock_ai.submit.api import _generate_user_id, _segment_payload, build_submit_url


def test_build_submit_url_default():
    url = build_submit_url("abc123")
    assert url == "https://sponsor.ajay.app/api/skipSegments"


def test_build_submit_url_custom_host():
    url = build_submit_url("abc123", host="https://sponsorblock.kavin.rocks")
    assert "kavin.rocks" in url
    assert url.endswith("/api/skipSegments")


def test_build_submit_url_trailing_slash():
    url = build_submit_url("abc", host="https://sponsor.ajay.app/")
    assert not url[len("https://sponsor.ajay.app"):].startswith("//")


def test_segment_payload_structure():
    seg = {"start": 10.5, "end": 45.2, "category": "sponsor", "confidence": 0.9}
    payload = _segment_payload(seg)
    assert payload["segment"] == [10.5, 45.2]
    assert payload["category"] == "sponsor"
    assert payload["actionType"] == "skip"


def test_generate_user_id_length():
    uid = _generate_user_id(36)
    assert len(uid) == 36


def test_generate_user_id_unique():
    ids = {_generate_user_id() for _ in range(10)}
    assert len(ids) == 10
