"""Tests for taal classification logic."""

import numpy as np

from taal_finder.models import TaalName
from taal_finder.taal import (
    _average_cyclic_pattern,
    _normalize,
    estimate_cycle_length,
    match_accent_pattern,
)


class TestEstimateCycleLength:
    def test_rupak_cycle(self, sample_downbeats_rupak):
        length = estimate_cycle_length(sample_downbeats_rupak)
        assert length == 7

    def test_teentaal_cycle(self, sample_downbeats_teentaal):
        length = estimate_cycle_length(sample_downbeats_teentaal)
        assert length == 16

    def test_empty_input(self):
        length = estimate_cycle_length(np.array([]).reshape(0, 2))
        assert length == 0


class TestAccentPatternMatching:
    def test_rupak_strong_pattern(self):
        """A pattern matching Rupak's accent structure should rank Rupak highest."""
        # Rupak: 7 matras, sam=khali at 0, tali at 3, 5
        # Build a pattern that emphasizes positions 3 and 5 (tali) and de-emphasizes 0 (khali)
        pattern = np.array([0.2, 0.5, 0.5, 0.8, 0.5, 0.8, 0.5])
        # Repeat for multiple cycles
        multi_cycle = np.tile(pattern, 5)

        rankings = match_accent_pattern(multi_cycle, 7)
        assert len(rankings) == 1  # Only Rupak has 7 matras
        assert rankings[0][0] == TaalName.RUPAK

    def test_no_candidates(self):
        """Cycle length with no matching taals returns empty."""
        pattern = np.ones(99)
        rankings = match_accent_pattern(pattern, 99)
        assert rankings == []


class TestAverageCyclicPattern:
    def test_averaging(self):
        # 3 cycles of length 4
        strengths = np.array([1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0], dtype=float)
        avg = _average_cyclic_pattern(strengths, 4)
        np.testing.assert_array_almost_equal(avg, [1.0, 0.0, 0.0, 0.0])

    def test_short_input(self):
        strengths = np.array([0.5, 0.3])
        avg = _average_cyclic_pattern(strengths, 4)
        assert len(avg) == 4
        assert avg[0] == 0.5
        assert avg[1] == 0.3

    def test_empty(self):
        avg = _average_cyclic_pattern(np.array([]), 4)
        assert len(avg) == 4


class TestNormalize:
    def test_unit_vector(self):
        arr = np.array([3.0, 4.0])
        normed = _normalize(arr)
        np.testing.assert_almost_equal(np.linalg.norm(normed), 1.0)

    def test_zero_vector(self):
        arr = np.zeros(5)
        normed = _normalize(arr)
        np.testing.assert_array_equal(normed, arr)
