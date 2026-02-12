"""Taal classification logic."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import numpy as np

from taal_finder.beats import (
    detect_beats,
    detect_downbeats,
    estimate_tempo,
    extract_accent_pattern,
)
from taal_finder.models import BeatInfo, TaalDefinition, TaalDetectionResult, TaalName
from taal_finder.taals.definitions import TAAL_REGISTRY, get_taals_by_matras


def estimate_cycle_length(downbeats: np.ndarray) -> int:
    """Determine the most likely number of beats per cycle.

    Looks at the beat_position column from madmom's downbeat output
    and votes across multiple cycles for robustness.
    """
    if len(downbeats) == 0:
        return 0

    beat_positions = downbeats[:, 1].astype(int)

    # Find where beat_position resets (indicating cycle boundaries)
    # The max beat_position before each reset tells us the cycle length
    cycle_lengths: list[int] = []
    current_max = 0

    for i in range(1, len(beat_positions)):
        if beat_positions[i] <= beat_positions[i - 1]:
            # Reset detected — previous max + 1 = cycle length
            cycle_lengths.append(current_max + 1)
            current_max = beat_positions[i]
        else:
            current_max = max(current_max, beat_positions[i])

    # Add the last partial cycle if we have data
    if current_max > 0:
        cycle_lengths.append(current_max + 1)

    if not cycle_lengths:
        # Fallback: use max beat position + 1
        return int(np.max(beat_positions)) + 1

    # Vote: most common cycle length wins
    counter = Counter(cycle_lengths)
    return counter.most_common(1)[0][0]


def _build_expected_accent_pattern(
    taal_name: TaalName,
    cycle_length: int,
) -> np.ndarray:
    """Build the expected accent pattern for a taal.

    Sam and tali positions get high weights, khali gets low weight.
    """
    taal_def = TAAL_REGISTRY[taal_name]
    pattern = np.ones(cycle_length) * 0.5  # baseline

    # Sam is always strongest
    pattern[taal_def.sam_position] = 1.0

    # Tali positions are strong
    for pos in taal_def.tali_positions:
        if pos < cycle_length:
            pattern[pos] = 0.8

    # Khali positions are weak
    for pos in taal_def.khali_positions:
        if pos < cycle_length:
            pattern[pos] = 0.2

    # Vibhag boundaries get slight emphasis
    for boundary in taal_def.vibhag_boundaries:
        if boundary < cycle_length and pattern[boundary] == 0.5:
            pattern[boundary] = 0.65

    return pattern


def match_accent_pattern(
    observed_pattern: np.ndarray,
    cycle_length: int,
) -> list[tuple[TaalName, float]]:
    """Compare observed accent pattern against known taals with this cycle length.

    Returns ranked list of (taal_name, confidence) sorted by descending confidence.
    """
    candidates = get_taals_by_matras(cycle_length)
    if not candidates:
        return []

    results: list[tuple[TaalName, float]] = []

    for taal_def in candidates:
        expected = _build_expected_accent_pattern(taal_def.name, cycle_length)

        # Average the observed pattern across cycles
        avg_pattern = _average_cyclic_pattern(observed_pattern, cycle_length)

        # Normalize both patterns
        obs_norm = _normalize(avg_pattern)
        exp_norm = _normalize(expected)

        # Cosine similarity
        similarity = float(np.dot(obs_norm, exp_norm))
        # Clamp to [0, 1]
        confidence = max(0.0, min(1.0, similarity))

        results.append((taal_def.name, confidence))

    return sorted(results, key=lambda x: x[1], reverse=True)


def _average_cyclic_pattern(strengths: np.ndarray, cycle_length: int) -> np.ndarray:
    """Average the observed strengths across multiple cycles."""
    if len(strengths) == 0 or cycle_length <= 0:
        return np.zeros(cycle_length)

    n_full_cycles = len(strengths) // cycle_length
    if n_full_cycles == 0:
        # Pad with zeros if less than one full cycle
        padded = np.zeros(cycle_length)
        padded[: len(strengths)] = strengths
        return padded

    # Reshape into cycles and average
    trimmed = strengths[: n_full_cycles * cycle_length]
    cycles = trimmed.reshape(n_full_cycles, cycle_length)
    return np.mean(cycles, axis=0)


def _normalize(arr: np.ndarray) -> np.ndarray:
    """Normalize array to unit length."""
    norm = np.linalg.norm(arr)
    if norm == 0:
        return arr
    return arr / norm


def _classify_laya(bpm: float, taal_name: TaalName) -> str:
    """Classify the tempo as vilambit/madhya/drut based on taal context."""
    taal_def = TAAL_REGISTRY.get(taal_name)
    if taal_def is None:
        return "madhya"

    # Matra rate (matras per minute) is more meaningful than BPM for Indian music
    matra_rate = bpm  # Each beat ≈ one matra in this context

    if matra_rate < 60:
        return "vilambit"
    elif matra_rate < 160:
        return "madhya"
    else:
        return "drut"


def detect_taal(audio_path: str | Path) -> TaalDetectionResult:
    """Full taal detection pipeline.

    1. Detect beats and downbeats
    2. Estimate cycle length
    3. Extract accent pattern
    4. Match against known taals
    5. Build result with beat annotations
    """
    audio_path = Path(audio_path)

    # Step 1: Beat and downbeat detection
    beats = detect_beats(audio_path)
    downbeats = detect_downbeats(audio_path)

    # Step 2: Estimate cycle length
    cycle_length = estimate_cycle_length(downbeats)

    # Step 3: Extract accent pattern at beat positions
    accent_strengths = extract_accent_pattern(audio_path, beats)

    # Step 4: Match against known taals
    rankings = match_accent_pattern(accent_strengths, cycle_length)

    if not rankings:
        # No matching taal found — try nearby cycle lengths
        rankings = _try_nearby_cycle_lengths(accent_strengths, cycle_length)

    if not rankings:
        # Still nothing — return low-confidence best guess
        return _build_fallback_result(beats, cycle_length)

    best_taal, best_confidence = rankings[0]
    alternatives = rankings[1:]

    # Step 5: Compute tempo and build beat info
    tempo = estimate_tempo(beats)
    taal_def = TAAL_REGISTRY[best_taal]
    matra_duration = 60.0 / tempo if tempo > 0 else 0.0
    cycle_duration = matra_duration * taal_def.matras

    beat_infos = _build_beat_infos(beats, accent_strengths, taal_def)

    return TaalDetectionResult(
        taal=best_taal,
        confidence=best_confidence,
        tempo_bpm=round(tempo, 1),
        matra_duration=round(matra_duration, 4),
        cycle_duration=round(cycle_duration, 4),
        beats=beat_infos,
        alternative_taals=alternatives,
    )


def _try_nearby_cycle_lengths(
    accent_strengths: np.ndarray,
    cycle_length: int,
) -> list[tuple[TaalName, float]]:
    """Try cycle lengths +-1 from the estimated one."""
    all_rankings: list[tuple[TaalName, float]] = []
    for offset in [-1, 1, -2, 2]:
        nearby = cycle_length + offset
        if nearby > 0:
            rankings = match_accent_pattern(accent_strengths, nearby)
            # Penalize non-exact matches
            all_rankings.extend((name, conf * 0.8) for name, conf in rankings)
    return sorted(all_rankings, key=lambda x: x[1], reverse=True)


def _build_fallback_result(
    beats: np.ndarray,
    cycle_length: int,
) -> TaalDetectionResult:
    """Build a low-confidence result when no taal matches."""
    tempo = estimate_tempo(beats)
    # Pick the closest known taal by matra count
    closest_taal = min(
        TAAL_REGISTRY.values(),
        key=lambda t: abs(t.matras - cycle_length),
    )
    matra_duration = 60.0 / tempo if tempo > 0 else 0.0

    return TaalDetectionResult(
        taal=closest_taal.name,
        confidence=0.1,
        tempo_bpm=round(tempo, 1),
        matra_duration=round(matra_duration, 4),
        cycle_duration=round(matra_duration * closest_taal.matras, 4),
        beats=[],
        alternative_taals=[],
    )


def _build_beat_infos(
    beats: np.ndarray,
    strengths: np.ndarray,
    taal_def: TaalDefinition,
) -> list[BeatInfo]:
    """Annotate beats with their position in the taal cycle."""
    beat_infos: list[BeatInfo] = []
    for i, beat_time in enumerate(beats):
        pos = i % taal_def.matras
        beat_infos.append(
            BeatInfo(
                time=round(float(beat_time), 4),
                beat_position=pos,
                is_sam=pos == taal_def.sam_position,
                is_khali=pos in taal_def.khali_positions,
                strength=round(float(strengths[i]), 4) if i < len(strengths) else 0.0,
            )
        )
    return beat_infos
