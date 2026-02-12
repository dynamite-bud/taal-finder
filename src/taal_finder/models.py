"""Core data models for taal detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class TaalName(StrEnum):
    """Known Indian classical taals."""

    TEENTAAL = "teentaal"  # 16 matras: 4+4+4+4
    RUPAK = "rupak"  # 7 matras: 3+2+2
    DADRA = "dadra"  # 6 matras: 3+3
    JHAPTAAL = "jhaptaal"  # 10 matras: 2+3+2+3
    EKTAAL = "ektaal"  # 12 matras: 2+2+2+2+2+2
    DEEPCHANDI = "deepchandi"  # 14 matras: 3+4+3+4
    KEHERWA = "keherwa"  # 8 matras: 4+4


@dataclass(frozen=True)
class TaalDefinition:
    """Defines the structure of a taal (rhythmic cycle)."""

    name: TaalName
    matras: int  # total matras in cycle
    vibhags: tuple[int, ...]  # grouping pattern
    sam_position: int  # usually 0 (first beat)
    khali_positions: tuple[int, ...]  # open/unstressed positions
    tali_positions: tuple[int, ...]  # clap/stressed positions
    common_layas: tuple[str, ...]  # vilambit, madhya, drut
    hindi_name: str = ""  # e.g. "ताल रूपक"

    @property
    def vibhag_boundaries(self) -> tuple[int, ...]:
        """Cumulative matra positions where vibhags start."""
        boundaries: list[int] = [0]
        for v in self.vibhags[:-1]:
            boundaries.append(boundaries[-1] + v)
        return tuple(boundaries)


@dataclass
class BeatInfo:
    """Information about a single detected beat."""

    time: float  # seconds
    beat_position: int  # position within the taal cycle (0-indexed)
    is_sam: bool
    is_khali: bool
    strength: float  # onset strength at this beat


@dataclass
class TaalDetectionResult:
    """Complete result of taal detection on an audio file."""

    taal: TaalName
    confidence: float  # 0.0 to 1.0
    tempo_bpm: float
    matra_duration: float  # seconds per matra
    cycle_duration: float  # seconds per full cycle
    beats: list[BeatInfo] = field(default_factory=list)
    alternative_taals: list[tuple[TaalName, float]] = field(default_factory=list)
