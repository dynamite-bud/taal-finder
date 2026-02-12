"""Terminal visualization of taal detection results."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from taal_finder.taals.definitions import TAAL_REGISTRY

if TYPE_CHECKING:
    from taal_finder.models import TaalDetectionResult, TaalName


def render_result(result: TaalDetectionResult, console: Console | None = None) -> None:
    """Render taal detection result to the terminal using Rich."""
    if console is None:
        console = Console()

    taal_def = TAAL_REGISTRY.get(result.taal)
    hindi = taal_def.hindi_name if taal_def else ""
    title = f"{result.taal.value.title()}"
    if hindi:
        title += f" ({hindi})"

    laya = _classify_laya_label(result.tempo_bpm)
    vibhag_str = "+".join(str(v) for v in taal_def.vibhags) if taal_def else "?"

    # Main info table
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="bold cyan")
    info_table.add_column("Value")

    info_table.add_row("Detected Taal", title)
    info_table.add_row("Confidence", f"{result.confidence:.0%}")
    info_table.add_row("Tempo", f"{result.tempo_bpm:.1f} BPM ({laya})")
    if taal_def:
        info_table.add_row("Matras/Cycle", f"{taal_def.matras} ({vibhag_str})")
    info_table.add_row("Cycle Duration", f"{result.cycle_duration:.2f}s")
    info_table.add_row("Matra Duration", f"{result.matra_duration:.3f}s")

    console.print()
    console.print(Panel(info_table, title="Taal Detection Result", border_style="green"))

    # Beat pattern visualization
    if taal_def:
        pattern = _render_beat_pattern(taal_def.name)
        if pattern:
            console.print()
            console.print(Panel(pattern, title="Beat Pattern", border_style="blue"))

    # Alternatives
    if result.alternative_taals:
        console.print()
        alt_table = Table(title="Alternative Taals", box=None)
        alt_table.add_column("Taal", style="yellow")
        alt_table.add_column("Matras")
        alt_table.add_column("Confidence")

        for taal_name, conf in result.alternative_taals[:3]:
            alt_def = TAAL_REGISTRY.get(taal_name)
            matras = str(alt_def.matras) if alt_def else "?"
            alt_table.add_row(taal_name.value.title(), matras, f"{conf:.0%}")

        console.print(alt_table)
    console.print()


def _render_beat_pattern(taal_name: TaalName) -> Text | None:
    """Render the taal's beat pattern as a visual grid."""
    taal_def = TAAL_REGISTRY.get(taal_name)
    if taal_def is None:
        return None

    text = Text()
    matra_idx = 0

    for vi, vibhag_len in enumerate(taal_def.vibhags):
        if vi > 0:
            text.append("  |  ", style="dim")

        for j in range(vibhag_len):
            if j > 0:
                text.append("  ")

            pos = matra_idx
            if pos == taal_def.sam_position and pos in taal_def.khali_positions:
                # Rupak special case: sam is khali
                text.append("X", style="bold red")
            elif pos == taal_def.sam_position:
                text.append("X", style="bold green")
            elif pos in taal_def.khali_positions:
                text.append("0", style="bold red")
            elif pos in taal_def.tali_positions:
                text.append(str(vi + 1), style="bold yellow")
            else:
                text.append(".", style="dim")

            matra_idx += 1

    # Add legend
    text.append("\n\n")
    text.append("X", style="bold green")
    text.append("=Sam  ")
    text.append("0", style="bold red")
    text.append("=Khali  ")
    text.append("2", style="bold yellow")
    text.append("=Tali  ")
    text.append(".", style="dim")
    text.append("=Matra")

    return text


def _classify_laya_label(bpm: float) -> str:
    """Return a human-readable laya classification."""
    if bpm < 60:
        return "Vilambit Laya"
    if bpm < 160:
        return "Madhya Laya"
    return "Drut Laya"
