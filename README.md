# SponsorBlock AI

[![Stars](https://img.shields.io/github/stars/chirag127/sponsorblock-ai?style=flat-square)](https://github.com/chirag127/sponsorblock-ai/stargazers)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

**Live demo:** https://huggingface.co/spaces/chirag127/sponsorblock-ai

ModernBERT-base fine-tuned on the SponsorBlock database to detect sponsor, intro, outro, self-promo, interaction, and filler segments in YouTube videos — purely from transcript text, no audio needed.

## Pipeline

```mermaid
graph LR
    A[SponsorBlock DB<br/>sponsorTimes.csv] --> B[Filter<br/>votes ≥ 2]
    C[YouTube video ID] --> D[yt-dlp<br/>word-timed transcript]
    B --> E[Label alignment<br/>overlap ≥ 50%]
    D --> E
    E --> F[Sliding windows<br/>128 tokens / 64 stride]
    F --> G[ModernBERT-base<br/>+ classification head]
    G --> H[Merge adjacent<br/>same-class windows]
    H --> I[Silence boundary<br/>refinement]
    I --> J[Segments<br/>{start, end, category}]
    J --> K[SponsorBlock API<br/>POST /api/skipSegments]
```

## Why ModernBERT instead of T5

The original codebase used a T5-generation approach (seq2seq), which is heavyweight for a labelling task. ModernBERT-base is a 2024 encoder-only model that outperforms DeBERTa/BERT on NLP benchmarks while running significantly faster on CPU — ideal for per-window classification. Sequence classification over sliding transcript windows fits the task exactly: each window gets one category label, no generation needed.

## Model

[`chirag127/sponsorblock-modernbert`](https://huggingface.co/chirag127/sponsorblock-modernbert) — 7 classes: `sponsor`, `intro`, `outro`, `selfpromo`, `interaction`, `filler`, `none`.

## Quickstart

```bash
pip install 'sponsorblock-ai @ git+https://github.com/chirag127/sponsorblock-ai.git'

# Detect segments
sponsorblock-ai predict dQw4w9WgXcQ

# Detect + submit to SponsorBlock
SB_USER_ID=<your-private-id> sponsorblock-ai submit dQw4w9WgXcQ

# Download SponsorBlock DB (cached to data/raw/)
sponsorblock-ai fetch-db

# Launch local Streamlit demo
pip install 'sponsorblock-ai[app] @ ...'
sponsorblock-ai serve
```

## Training on Colab

1. Open [`notebooks/train_modernbert.ipynb`](notebooks/train_modernbert.ipynb) in [Google Colab](https://colab.research.google.com) (T4 GPU runtime).
2. Add `HF_TOKEN` to Colab Secrets.
3. Run all cells — fetches DB, builds windows, fine-tunes, evaluates, pushes to Hub.

```bash
# Fetch DB locally first (optional)
sponsorblock-ai fetch-db --dest data/raw --min-votes 2
```

## Eval results

_Fill after training._

| Category    | Precision | Recall | F1 |
|-------------|-----------|--------|----|
| sponsor     | —         | —      | —  |
| intro       | —         | —      | —  |
| outro       | —         | —      | —  |
| selfpromo   | —         | —      | —  |
| interaction | —         | —      | —  |
| filler      | —         | —      | —  |
| **macro**   | —         | —      | —  |

## Project layout

```
src/sponsorblock_ai/
  constants.py          — categories, label maps, defaults
  data/
    fetch_db.py         — SponsorBlock DB download + filter
    transcript.py       — yt-dlp transcript fetch (word-timed)
    windowing.py        — sliding window + label assignment
    build_dataset.py    — HF Dataset builder
  model/
    architecture.py     — ModernBERT load (train + inference)
    trainer.py          — HF Trainer wrapper + metrics
  inference/
    predict.py          — video → segments pipeline
    silence.py          — boundary refinement via silence gaps
  submit/
    api.py              — SponsorBlock API submission
  cli.py                — Typer CLI
app/
  app.py                — Streamlit HF Space
notebooks/
  train_modernbert.ipynb — Colab/Kaggle training notebook
tests/                  — pytest unit + integration tests
```

## License

MIT
