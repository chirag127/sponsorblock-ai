---
title: SponsorBlock AI
emoji: 🎬
colorFrom: red
colorTo: gray
sdk: streamlit
sdk_version: "1.41.0"
app_file: app.py
pinned: false
license: mit
---

# SponsorBlock AI

ModernBERT-base fine-tuned on the SponsorBlock database to detect sponsor, intro, outro, selfpromo, interaction, and filler segments in YouTube videos — without watching them.

**Live demo:** https://huggingface.co/spaces/chirag127/sponsorblock-ai

## Usage

Paste a YouTube URL or video ID, set your confidence threshold, and click **Detect Segments**.

## Model

[`chirag127/sponsorblock-modernbert`](https://huggingface.co/chirag127/sponsorblock-modernbert) — ModernBERT-base + sequence-classification head, 7 classes, trained on the SponsorBlock database.

## Source

[`chirag127/sponsorblock-ai`](https://github.com/chirag127/sponsorblock-ai)
