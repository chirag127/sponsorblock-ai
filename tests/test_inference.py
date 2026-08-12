"""Integration test: inference predict_video with a mocked model + transcript."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import torch


def _make_fake_model(num_labels: int = 7):
    """Return a mock model that outputs uniform logits."""
    model = MagicMock()
    model.eval = MagicMock(return_value=model)

    def forward(**kwargs):
        batch = kwargs.get("input_ids")
        n = batch.shape[0] if batch is not None else 1
        logits = torch.zeros(n, num_labels)
        # Make label 0 (sponsor) most likely
        logits[:, 0] = 5.0
        out = MagicMock()
        out.logits = logits
        return out

    model.__call__ = forward
    return model


def _make_fake_tokenizer():
    tok = MagicMock()

    def tokenize(texts, **kwargs):
        n = len(texts) if isinstance(texts, list) else 1
        return {
            "input_ids": torch.ones(n, 10, dtype=torch.long),
            "attention_mask": torch.ones(n, 10, dtype=torch.long),
        }

    tok.side_effect = tokenize
    tok.__call__ = tokenize
    return tok


def _fake_transcript(video_id: str):
    from sponsorblock_ai.data.transcript import TranscriptResult

    words = [{"text": f"w{i}", "start": float(i), "end": float(i + 1)} for i in range(30)]
    return TranscriptResult(words=words, is_auto=True, language="en", duration=30.0)


def test_predict_video_with_mocks():
    model = _make_fake_model()
    tokenizer = _make_fake_tokenizer()

    with patch("sponsorblock_ai.inference.predict.fetch_transcript", side_effect=_fake_transcript):
        from sponsorblock_ai.inference.predict import predict_video

        segments = predict_video(
            "dQw4w9WgXcQ",
            model=model,
            tokenizer=tokenizer,
            confidence_threshold=0.0,
            refine=False,
        )

    assert isinstance(segments, list)
    # With sponsor logits dominant and threshold=0, we expect at least 1 merged segment
    assert len(segments) >= 1
    assert all("category" in s for s in segments)
    assert all("confidence" in s for s in segments)


def test_predict_video_no_transcript():
    model = _make_fake_model()
    tokenizer = _make_fake_tokenizer()

    with patch("sponsorblock_ai.inference.predict.fetch_transcript", return_value=None):
        from sponsorblock_ai.inference.predict import predict_video

        segments = predict_video("fakeid", model=model, tokenizer=tokenizer, refine=False)

    assert segments == []
