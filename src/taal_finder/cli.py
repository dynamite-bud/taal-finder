"""CLI entry point for taal-finder."""

from __future__ import annotations

import json
import sys
from pathlib import Path  # noqa: TC003 — typer needs this at runtime
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console
from rich.text import Text

from taal_finder import __version__

if TYPE_CHECKING:
    from taal_finder.models import TaalDetectionResult

app = typer.Typer(
    name="taal-finder",
    help="Detect Indian classical taals from audio files.",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"taal-finder v{__version__}")
        raise typer.Exit


@app.command()
def detect(
    file: Annotated[
        Path,
        typer.Argument(
            help="Path to the audio file (MP3, WAV, FLAC).",
            exists=True,
            readable=True,
        ),
    ],
    output_json: Annotated[
        bool,
        typer.Option(
            "--json",
            "-j",
            help="Output result as JSON.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show detailed beat information.",
        ),
    ] = False,
    _version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = False,
) -> None:
    """Detect the taal (rhythmic cycle) in an audio file."""
    from taal_finder.taal import detect_taal
    from taal_finder.viz import render_result

    console.print(f"\nAnalyzing: [bold]{file.name}[/bold]...", style="dim")

    try:
        result = detect_taal(file)
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Error during analysis:[/red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from None

    if output_json:
        _print_json(result)
    else:
        render_result(result, console)

        if verbose and result.beats:
            _print_beat_details(result)


def _print_json(result: TaalDetectionResult) -> None:
    """Print result as JSON to stdout."""
    data = {
        "taal": result.taal.value,
        "confidence": round(result.confidence, 4),
        "tempo_bpm": result.tempo_bpm,
        "matra_duration": result.matra_duration,
        "cycle_duration": result.cycle_duration,
        "alternatives": [
            {"taal": t.value, "confidence": round(c, 4)} for t, c in result.alternative_taals
        ],
        "beat_count": len(result.beats),
    }
    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")


def _print_beat_details(result: TaalDetectionResult) -> None:
    """Print detailed beat-by-beat information."""
    from rich.table import Table

    from taal_finder.taals.definitions import TAAL_REGISTRY

    table = Table(title="Beat Details (first 2 cycles)")
    table.add_column("#", style="dim")
    table.add_column("Time (s)")
    table.add_column("Position")
    table.add_column("Type")
    table.add_column("Strength")

    taal_def = TAAL_REGISTRY.get(result.taal)
    max_beats = (taal_def.matras * 2) if taal_def else 32

    for i, beat in enumerate(result.beats[:max_beats]):
        beat_type = ""
        style = ""
        if beat.is_sam:
            beat_type = "Sam"
            style = "bold green"
        elif beat.is_khali:
            beat_type = "Khali"
            style = "red"
        else:
            beat_type = "Matra"

        table.add_row(
            str(i + 1),
            f"{beat.time:.3f}",
            str(beat.beat_position + 1),
            Text(beat_type, style=style) if style else beat_type,
            f"{beat.strength:.3f}",
        )

    console.print()
    console.print(table)
