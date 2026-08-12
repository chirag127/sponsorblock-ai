"""Typer CLI for sponsorblock-ai."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="sponsorblock-ai", help="ModernBERT sponsor-segment detector for YouTube.")
console = Console()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


@app.command("fetch-db")
def fetch_db(
    dest: Path = typer.Option(Path("data/raw"), help="Directory to save sponsorTimes.csv"),
    min_votes: int = typer.Option(1, help="Minimum votes to include a segment"),
    force: bool = typer.Option(False, "--force", help="Re-download even if cached"),
) -> None:
    """Download and filter the SponsorBlock database dump."""
    from sponsorblock_ai.data.fetch_db import fetch_sponsor_times

    console.print(f"Fetching SponsorBlock DB → {dest}")
    df = fetch_sponsor_times(dest_dir=dest, min_votes=min_votes, force=force)
    console.print(f"[green]Done.[/green] {len(df):,} rows saved to {dest}/sponsorTimes.csv")


@app.command("predict")
def predict(
    video: str = typer.Argument(..., help="YouTube video ID or URL"),
    model_id: str | None = typer.Option(None, help="HF Hub model id or local path"),
    threshold: float = typer.Option(0.5, help="Confidence threshold"),
    no_refine: bool = typer.Option(False, "--no-refine", help="Skip silence boundary refinement"),
) -> None:
    """Detect sponsor segments in a YouTube video."""
    from sponsorblock_ai.inference.predict import predict_video

    # Accept full URLs
    if "youtube.com" in video or "youtu.be" in video:
        video = video.split("v=")[-1].split("&")[0].split("/")[-1][:11]

    console.print(f"Predicting segments for [bold]{video}[/bold]")
    segments = predict_video(
        video,
        model_id=model_id,
        confidence_threshold=threshold,
        refine=not no_refine,
    )

    if not segments:
        console.print("[yellow]No segments detected.[/yellow]")
        return

    table = Table("Start", "End", "Category", "Confidence")
    for seg in segments:
        table.add_row(
            f"{seg['start']:.1f}s",
            f"{seg['end']:.1f}s",
            seg["category"],
            f"{seg['confidence']:.2%}",
        )
    console.print(table)


@app.command("submit")
def submit(
    video: str = typer.Argument(..., help="YouTube video ID or URL"),
    model_id: str | None = typer.Option(None, help="HF Hub model id"),
    threshold: float = typer.Option(0.5, help="Confidence threshold"),
    user_id: str | None = typer.Option(None, envvar="SB_USER_ID", help="SponsorBlock user ID"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Predict only, do not submit"),
) -> None:
    """Detect and submit segments to SponsorBlock."""
    from sponsorblock_ai.inference.predict import predict_video
    from sponsorblock_ai.submit.api import submit_segments

    if "youtube.com" in video or "youtu.be" in video:
        video = video.split("v=")[-1].split("&")[0].split("/")[-1][:11]

    console.print(f"Detecting segments for [bold]{video}[/bold]")
    segments = predict_video(video, model_id=model_id, confidence_threshold=threshold)

    if not segments:
        console.print("[yellow]No segments detected.[/yellow]")
        return

    console.print(f"Found {len(segments)} segment(s)")
    if dry_run:
        console.print("[yellow]Dry-run: not submitting.[/yellow]")
        for seg in segments:
            cat = seg["category"]
            conf = seg["confidence"]
            console.print(f"  {seg['start']:.1f}–{seg['end']:.1f}s  {cat}  {conf:.2%}")
        return

    result = submit_segments(video, segments, user_id=user_id)
    if result["submitted"] > 0:
        console.print(f"[green]Submitted {result['submitted']} segment(s).[/green]")
    else:
        console.print(f"[red]Submit failed or duplicate:[/red] {result['errors']}")


@app.command("train")
def train(
    _: bool = typer.Option(False),  # dummy to trigger help
) -> None:
    """Training runs on Colab/Kaggle GPU — open notebooks/train_modernbert.ipynb."""
    console.print(
        "[bold yellow]Training requires a GPU runtime.[/bold yellow]\n"
        "Open [cyan]notebooks/train_modernbert.ipynb[/cyan] in Google Colab or Kaggle."
    )


@app.command("serve")
def serve(
    port: int = typer.Option(8501, help="Streamlit port"),
) -> None:
    """Launch the local Streamlit demo."""
    app_path = Path(__file__).parent.parent.parent.parent / "app" / "app.py"
    if not app_path.exists():
        app_path = Path("app/app.py")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(port)],
        check=True,
    )


if __name__ == "__main__":
    app()
