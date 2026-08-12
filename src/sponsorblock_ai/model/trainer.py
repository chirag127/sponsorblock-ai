"""Training loop using HuggingFace Trainer.

Designed to run on Colab/Kaggle GPU. Called from the notebook.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def compute_metrics(eval_pred):
    """Compute per-class precision/recall/F1 + macro average."""
    import numpy as np
    from sklearn.metrics import classification_report  # type: ignore

    from sponsorblock_ai.constants import CATEGORIES, NUM_LABELS

    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    report = classification_report(
        labels,
        preds,
        labels=list(range(NUM_LABELS)),
        target_names=CATEGORIES,
        output_dict=True,
        zero_division=0,
    )
    return {
        "accuracy": report["accuracy"],
        "f1_macro": report["macro avg"]["f1-score"],
        "precision_macro": report["macro avg"]["precision"],
        "recall_macro": report["macro avg"]["recall"],
    }


def train(
    dataset_dict,
    output_dir: str = "outputs/sponsorblock-modernbert",
    num_epochs: int = 3,
    batch_size: int = 32,
    learning_rate: float = 2e-5,
    base_model: str | None = None,
    fp16: bool = True,
    push_to_hub: bool = False,
    hub_model_id: str | None = None,
):
    """Fine-tune ModernBERT on dataset_dict.

    Args:
        dataset_dict: HF DatasetDict with train/validation/test.
        output_dir: Where to save checkpoints.
        num_epochs: Training epochs.
        batch_size: Per-device batch size.
        learning_rate: AdamW LR.
        base_model: Override base model id.
        fp16: Use mixed precision (disable on CPU).
        push_to_hub: Push final model to HF Hub.
        hub_model_id: Hub repo id (requires HF_TOKEN env var).
    """
    from transformers import Trainer, TrainingArguments  # type: ignore

    from sponsorblock_ai.constants import BASE_MODEL_ID
    from sponsorblock_ai.model.architecture import load_model_for_training

    model, tokenizer = load_model_for_training(base_model or BASE_MODEL_ID)

    args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        fp16=fp16,
        logging_steps=50,
        report_to="none",
        push_to_hub=push_to_hub,
        hub_model_id=hub_model_id,
        hub_token=os.environ.get("HF_TOKEN"),
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset_dict["train"],
        eval_dataset=dataset_dict["validation"],
        compute_metrics=compute_metrics,
        tokenizer=tokenizer,
    )

    trainer.train()
    results = trainer.evaluate(dataset_dict["test"])
    logger.info("Test results: %s", results)

    if push_to_hub:
        trainer.push_to_hub()
        tokenizer.push_to_hub(hub_model_id, token=os.environ.get("HF_TOKEN"))

    return trainer, results
