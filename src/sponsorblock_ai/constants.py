"""Shared constants and category definitions."""

from __future__ import annotations

# SponsorBlock API hosts (primary + mirrors)
SB_HOSTS: list[str] = [
    "https://sponsor.ajay.app",
    "https://sponsorblock.kavin.rocks",
    "https://sponsorblock.gleesh.net",
    "https://sb.theairplan.com",
    "https://sponsorblock.hankmccord.dev",
]

SB_PRIMARY_HOST = SB_HOSTS[0]

# SponsorBlock categories we model
CATEGORIES: list[str] = [
    "sponsor",
    "intro",
    "outro",
    "selfpromo",
    "interaction",
    "filler",
    "none",
]

# Map category label → integer id (used as HF label2id)
LABEL2ID: dict[str, int] = {cat: i for i, cat in enumerate(CATEGORIES)}
ID2LABEL: dict[int, str] = {i: cat for cat, i in LABEL2ID.items()}
NUM_LABELS = len(CATEGORIES)

# SponsorBlock action types accepted
SB_ACTION_TYPES: list[str] = ["skip", "mute", "full", "poi"]

# Windowing defaults
WINDOW_SIZE_TOKENS = 128
WINDOW_STRIDE_TOKENS = 64
MAX_WINDOW_DURATION = 120.0  # seconds; windows beyond this are split

# Model hub id
HF_MODEL_ID = "chirag127/sponsorblock-modernbert"
BASE_MODEL_ID = "answerdotai/ModernBERT-base"
