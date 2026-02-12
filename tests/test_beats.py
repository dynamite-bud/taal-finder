"""Tests for beat utility functions (non-madmom parts)."""

import numpy as np

from taal_finder.beats import compute_ioi, estimate_tempo


class TestComputeIOI:
    def test_regular_beats(self):
        beats = np.array([1.0, 1.5, 2.0, 2.5])
        iois = compute_ioi(beats)
        np.testing.assert_array_almost_equal(iois, [0.5, 0.5, 0.5])

    def test_irregular_beats(self):
        beats = np.array([0.0, 0.5, 1.5, 2.0])
        iois = compute_ioi(beats)
        np.testing.assert_array_almost_equal(iois, [0.5, 1.0, 0.5])

    def test_single_beat(self):
        beats = np.array([1.0])
        iois = compute_ioi(beats)
        assert len(iois) == 0


class TestEstimateTempo:
    def test_120_bpm(self):
        # 120 BPM = 0.5s per beat
        beats = np.arange(0.0, 10.0, 0.5)
        bpm = estimate_tempo(beats)
        assert abs(bpm - 120.0) < 1.0

    def test_60_bpm(self):
        # 60 BPM = 1.0s per beat
        beats = np.arange(0.0, 10.0, 1.0)
        bpm = estimate_tempo(beats)
        assert abs(bpm - 60.0) < 1.0

    def test_empty(self):
        assert estimate_tempo(np.array([])) == 0.0

    def test_single_beat(self):
        assert estimate_tempo(np.array([1.0])) == 0.0
