"""Load and initialise the ModernBERT sequence-classification model."""

from __future__ import annotations

from sponsorblock_ai.constants import BASE_MODEL_ID, ID2LABEL, LABEL2ID, NUM_LABELS


def load_model_for_training(base_model: str = BASE_MODEL_ID):
    """Return (model, tokenizer) ready for Trainer fine-tuning."""
    from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForSequenceClassification.from_pretrained(
        base_model,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        ignore_mismatched_sizes=True,
    )
    return model, tokenizer


def load_model_for_inference(model_id: str | None = None):
    """Return (model, tokenizer) from HF Hub or local path.

    Falls back to base model if the fine-tuned hub model is unavailable.
    """
    from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore

    from sponsorblock_ai.constants import HF_MODEL_ID

    target = model_id or HF_MODEL_ID

    try:
        tokenizer = AutoTokenizer.from_pretrained(target)
        model = AutoModelForSequenceClassification.from_pretrained(
            target,
            num_labels=NUM_LABELS,
            id2label=ID2LABEL,
            label2id=LABEL2ID,
        )
        return model, tokenizer
    except Exception:
        # Fine-tuned model not yet on hub — fall back to base
        return load_model_for_training(BASE_MODEL_ID)
