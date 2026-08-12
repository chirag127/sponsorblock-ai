"""Integration test: tiny Trainer training loop on synthetic data."""

from __future__ import annotations

import pytest

# Skip if transformers/torch not available or on very slow CI
pytest.importorskip("transformers")


def _make_tiny_dataset(n: int = 7, seq_len: int = 16, num_labels: int = 7):
    from datasets import Dataset  # type: ignore

    # Ensure all 7 labels are represented
    data = {
        "input_ids": [[1] * seq_len for _ in range(n)],
        "attention_mask": [[1] * seq_len for _ in range(n)],
        "labels": [i % num_labels for i in range(n)],
    }
    return Dataset.from_dict(data)


def test_trainer_runs_on_tiny_data(tmp_path):
    """Prove Trainer wiring works end-to-end on 6 fake examples (CPU, fast)."""
    from datasets import DatasetDict  # type: ignore
    from transformers import (  # type: ignore
        AutoModelForSequenceClassification,
        Trainer,
        TrainingArguments,
    )

    from sponsorblock_ai.constants import BASE_MODEL_ID, ID2LABEL, LABEL2ID, NUM_LABELS
    from sponsorblock_ai.model.trainer import compute_metrics

    ds = _make_tiny_dataset(n=6)
    dd = DatasetDict({"train": ds, "validation": ds})

    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL_ID,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        ignore_mismatched_sizes=True,
    )

    args = TrainingArguments(
        output_dir=str(tmp_path),
        num_train_epochs=1,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        eval_strategy="epoch",
        fp16=False,
        logging_steps=1,
        report_to="none",
        use_cpu=True,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dd["train"],
        eval_dataset=dd["validation"],
        compute_metrics=compute_metrics,
    )

    # Should not raise
    trainer.train()
    results = trainer.evaluate()
    assert "eval_loss" in results
