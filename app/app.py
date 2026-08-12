"""Streamlit demo for SponsorBlock-AI.

Deployed as a HuggingFace Space (Streamlit SDK).
"""

from __future__ import annotations

import os
import re

import streamlit as st

st.set_page_config(
    page_title="SponsorBlock AI",
    page_icon="🎬",
    layout="centered",
)

st.title("SponsorBlock AI")
st.caption("ModernBERT sponsor-segment detector for YouTube videos")

# Sidebar
with st.sidebar:
    st.header("Settings")
    confidence = st.slider("Confidence threshold", 0.1, 0.99, 0.5, 0.01)
    refine = st.checkbox("Silence-boundary refinement", value=True)
    model_id = st.text_input("Model (HF Hub id or leave blank for default)", value="")
    st.markdown("---")
    st.markdown(
        "Model: [`chirag127/sponsorblock-modernbert`](https://huggingface.co/chirag127/sponsorblock-modernbert)"
    )
    st.markdown(
        "Source: [`chirag127/sponsorblock-ai`](https://github.com/chirag127/sponsorblock-ai)"
    )


@st.cache_resource(show_spinner="Loading model…")
def _load_model(mid: str):
    from sponsorblock_ai.model.architecture import load_model_for_inference

    return load_model_for_inference(mid or None)


def _extract_video_id(url_or_id: str) -> str:
    url_or_id = url_or_id.strip()
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url_or_id)
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
        return url_or_id
    return url_or_id


CATEGORY_COLORS = {
    "sponsor": "#FF4B4B",
    "intro": "#F0A500",
    "outro": "#4CAF50",
    "selfpromo": "#9B59B6",
    "interaction": "#3498DB",
    "filler": "#95A5A6",
    "none": "#7F8C8D",
}

# Input
url_input = st.text_input(
    "YouTube URL or Video ID",
    placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
)

col1, col2 = st.columns([3, 1])
predict_btn = col1.button("Detect Segments", type="primary", use_container_width=True)
submit_btn = col2.button("Submit to SB", use_container_width=True)

if predict_btn and url_input:
    video_id = _extract_video_id(url_input)
    if not video_id:
        st.error("Could not parse video ID from input.")
    else:
        with st.spinner(f"Analysing {video_id}…"):
            try:
                model, tokenizer = _load_model(model_id)
                from sponsorblock_ai.inference.predict import predict_video

                segments = predict_video(
                    video_id,
                    model=model,
                    tokenizer=tokenizer,
                    confidence_threshold=confidence,
                    refine=refine,
                )
                st.session_state["segments"] = segments
                st.session_state["video_id"] = video_id
            except Exception as exc:
                st.error(f"Prediction failed: {exc}")

if "segments" in st.session_state:
    segments = st.session_state["segments"]
    video_id = st.session_state.get("video_id", "")

    if not segments:
        st.info("No sponsor segments detected above threshold.")
    else:
        st.success(f"Found {len(segments)} segment(s) in `{video_id}`")

        for seg in segments:
            color = CATEGORY_COLORS.get(seg["category"], "#888")
            st.markdown(
                f"""<div style="border-left:4px solid {color};padding:8px 12px;margin:6px 0;
                background:#f9f9f9;border-radius:4px">
                <b style="color:{color}">{seg['category'].upper()}</b> &nbsp;
                {seg['start']:.1f}s – {seg['end']:.1f}s &nbsp;
                <small>({seg['end']-seg['start']:.1f}s, {seg['confidence']:.0%} confidence)</small>
                </div>""",
                unsafe_allow_html=True,
            )

        if submit_btn:
            sb_user = os.environ.get("SB_USER_ID", "")
            if not sb_user:
                st.warning("Set `SB_USER_ID` environment variable to submit anonymously.")
            else:
                with st.spinner("Submitting to SponsorBlock…"):
                    from sponsorblock_ai.submit.api import submit_segments

                    result = submit_segments(video_id, segments, user_id=sb_user)
                    if result["submitted"] > 0:
                        st.success(f"Submitted {result['submitted']} segment(s).")
                    else:
                        st.error(f"Submit failed: {result['errors']}")

st.markdown("---")
st.caption(
    "Predictions are from a fine-tuned ModernBERT model. "
    "Always review before submitting to SponsorBlock."
)
