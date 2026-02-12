"""Shared test fixtures."""

from __future__ import annotations

import numpy as np
import pytest

from taal_finder.models import TaalName
from taal_finder.taals.definitions import TAAL_REGISTRY


@pytest.fixture
def rupak_definition():
    return TAAL_REGISTRY[TaalName.RUPAK]


@pytest.fixture
def teentaal_definition():
    return TAAL_REGISTRY[TaalName.TEENTAAL]


@pytest.fixture
def sample_beats() -> np.ndarray:
    """Simulated beat times at ~120 BPM (0.5s intervals)."""
    return np.arange(0.5, 20.0, 0.5)


@pytest.fixture
def sample_downbeats_rupak() -> np.ndarray:
    """Simulated downbeat output for Rupak (7-beat cycles)."""
    rows = []
    time = 0.5
    for _ in range(4):  # 4 cycles
        for pos in range(7):
            rows.append([time, pos])
            time += 0.5
    return np.array(rows)


@pytest.fixture
def sample_downbeats_teentaal() -> np.ndarray:
    """Simulated downbeat output for Teentaal (16-beat cycles)."""
    rows = []
    time = 0.5
    for _ in range(3):  # 3 cycles
        for pos in range(16):
            rows.append([time, pos])
            time += 0.5
    return np.array(rows)
