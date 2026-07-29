# SponsorBlock AI

[![Stars](https://img.shields.io/github/stars/chirag127/sponsorblock-ai?style=flat-square)](https://github.com/chirag127/sponsorblock-ai/stargazers)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

**Live:** https://sponsorblock-ai.oriz.in

ML-powered automation: detect sponsor/intro/outro/self-promo segments in YouTube videos and submit them to the [SponsorBlock](https://sponsor.ajay.app) API.

## How it works

1. Fetches transcript from YouTube (auto or manual captions)
2. ML classifier (OpenAI + local model) tags each segment by category
3. Silence detection refines segment boundaries
4. Submits to SponsorBlock API under your user ID

## Setup

```bash
git clone https://github.com/chirag127/sponsorblock-ai
cd sponsorblock-ai
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add your API keys
```

## Environment

```
OPENAI_API_KEY=...           # OpenAI API key
YOUTUBE_API_KEY=...          # YouTube Data API v3 key
SPONSORBLOCK_USER_ID=...     # Your SponsorBlock user ID
```

## Usage

```bash
python -m sponsorblock_ai.cli.main <video_id_or_channel_id>
```

## Structure

```
src/sponsorblock_ai/
  classifier/   — ML model, training, evaluation
  transcript/   — YouTube transcript fetching + processing
  api/          — SponsorBlock, YouTube, OpenAI, Gist clients
  audio/        — silence detection, segment refinement
  cli/          — entry points (main.py, auto.py)
  utils/        — shared helpers, HTTP, config
notebooks/      — Jupyter experiments
```

## License

MIT
