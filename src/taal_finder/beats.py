"""Beat and downbeat detection using madmom."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from pathlib import Path

from taal_finder.taals.definitions import get_candidate_matra_counts


def detect_beats(audio_path: str | Path) -> np.ndarray:
    """Detect beat positions in audio.

    Returns array of beat times in seconds.
    """
    import madmom

    beat_proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)
    beat_act = madmom.features.beats.RNNBeatProcessor()(str(audio_path))
    return beat_proc(beat_act)


def detect_downbeats(audio_path: str | Path) -> np.ndarray:
    """Detect downbeats (bar/cycle boundaries) in audio.

    Uses madmom's DBNDownBeatTrackingProcessor configured with
    beats-per-bar values matching known taal matra counts.

    Returns array of shape (N, 2) where columns are [time, beat_position].
    beat_position resets at each bar, indicating the cycle length.
    """
    import madmom

    candidate_counts = get_candidate_matra_counts()

    downbeat_proc = madmom.features.downbeats.DBNDownBeatTrackingProcessor(
        beats_per_bar=candidate_counts,
        fps=100,
    )
    downbeat_act = madmom.features.downbeats.RNNDownBeatProcessor()(str(audio_path))
    return downbeat_proc(downbeat_act)


def extract_accent_pattern(
    audio_path: str | Path,
    beat_times: np.ndarray,
) -> np.ndarray:
    """Extract relative onset strength at each beat position.

    Returns an array of onset strengths corresponding to each beat time.
    """
    import madmom

    # Get beat activation function (onset strength over time)
    act = madmom.features.beats.RNNBeatProcessor()(str(audio_path))

    fps = 100
    strengths = np.zeros(len(beat_times))

    for i, t in enumerate(beat_times):
        frame_idx = int(t * fps)
        # Average a small window around the beat time for robustness
        start = max(0, frame_idx - 2)
        end = min(len(act), frame_idx + 3)
        if start < end:
            strengths[i] = float(np.mean(act[start:end]))

    return strengths


def compute_ioi(beat_times: np.ndarray) -> np.ndarray:
    """Compute inter-onset intervals (IOIs) between consecutive beats."""
    return np.diff(beat_times)


def estimate_tempo(beat_times: np.ndarray) -> float:
    """Estimate tempo in BPM from beat times."""
    if len(beat_times) < 2:
        return 0.0
    iois = compute_ioi(beat_times)
    median_ioi = float(np.median(iois))
    if median_ioi <= 0:
        return 0.0
    return 60.0 / median_ioi
