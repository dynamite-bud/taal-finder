"""Tests for data models."""

from taal_finder.models import BeatInfo, TaalDetectionResult, TaalName


class TestTaalName:
    def test_all_taals_have_string_values(self):
        for taal in TaalName:
            assert isinstance(taal.value, str)
            assert taal.value == taal.value.lower()

    def test_known_taals(self):
        assert TaalName.RUPAK == "rupak"
        assert TaalName.TEENTAAL == "teentaal"
        assert TaalName.DADRA == "dadra"


class TestBeatInfo:
    def test_create_beat(self):
        beat = BeatInfo(time=1.5, beat_position=3, is_sam=False, is_khali=True, strength=0.7)
        assert beat.time == 1.5
        assert beat.beat_position == 3
        assert beat.is_khali is True
        assert beat.is_sam is False


class TestTaalDetectionResult:
    def test_create_result(self):
        result = TaalDetectionResult(
            taal=TaalName.RUPAK,
            confidence=0.87,
            tempo_bpm=72.0,
            matra_duration=0.833,
            cycle_duration=5.833,
        )
        assert result.taal == TaalName.RUPAK
        assert result.confidence == 0.87
        assert result.beats == []
        assert result.alternative_taals == []
