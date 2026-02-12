"""Audio loading and preprocessing."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}
DEFAULT_SAMPLE_RATE = 44100


def load_audio(
    path: str | Path,
    target_sr: int = DEFAULT_SAMPLE_RATE,
    mono: bool = True,
) -> tuple[np.ndarray, int]:
    """Load an audio file and return (samples, sample_rate).

    Converts to mono by default and resamples to target_sr if needed.
    Supports MPEG, WAV, FLAC, and other formats via soundfile/libsndfile.
    """
    path = Path(path)
    if not path.exists():
        msg = f"Audio file not found: {path}"
        raise FileNotFoundError(msg)

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        msg = f"Unsupported audio format: {suffix}. Supported: {SUPPORTED_EXTENSIONS}"
        raise ValueError(msg)

    data, sr = sf.read(str(path), dtype="float32", always_2d=True)

    # Convert to mono by averaging channels
    if mono and data.shape[1] > 1:
        data = np.mean(data, axis=1)
    elif mono:
        data = data[:, 0]

    # Resample if needed
    if sr != target_sr:
        data = _resample(data, sr, target_sr)
        sr = target_sr

    return data, sr


def _resample(data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio using scipy."""
    from scipy.signal import resample

    duration = len(data) / orig_sr
    target_length = int(duration * target_sr)
    return resample(data, target_length).astype(np.float32)


def get_duration(path: str | Path) -> float:
    """Get audio file duration in seconds without loading entire file."""
    info = sf.info(str(path))
    return info.duration
