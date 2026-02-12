"""Tests for taal definitions."""

import pytest

from taal_finder.models import TaalName
from taal_finder.taals.definitions import (
    TAAL_REGISTRY,
    get_candidate_matra_counts,
    get_taals_by_matras,
)


class TestTaalRegistry:
    def test_all_enum_members_registered(self):
        for taal_name in TaalName:
            assert taal_name in TAAL_REGISTRY, f"{taal_name} not in registry"

    def test_matras_match_vibhags(self):
        for taal_def in TAAL_REGISTRY.values():
            assert taal_def.matras == sum(taal_def.vibhags), (
                f"{taal_def.name}: matras={taal_def.matras} != sum(vibhags)={sum(taal_def.vibhags)}"
            )

    def test_sam_position_valid(self):
        for taal_def in TAAL_REGISTRY.values():
            assert 0 <= taal_def.sam_position < taal_def.matras

    def test_khali_positions_valid(self):
        for taal_def in TAAL_REGISTRY.values():
            for pos in taal_def.khali_positions:
                assert 0 <= pos < taal_def.matras, (
                    f"{taal_def.name}: khali position {pos} out of range"
                )

    def test_tali_positions_valid(self):
        for taal_def in TAAL_REGISTRY.values():
            for pos in taal_def.tali_positions:
                assert 0 <= pos < taal_def.matras, (
                    f"{taal_def.name}: tali position {pos} out of range"
                )

    @pytest.mark.parametrize(
        ("taal", "expected_matras"),
        [
            (TaalName.DADRA, 6),
            (TaalName.RUPAK, 7),
            (TaalName.KEHERWA, 8),
            (TaalName.JHAPTAAL, 10),
            (TaalName.EKTAAL, 12),
            (TaalName.DEEPCHANDI, 14),
            (TaalName.TEENTAAL, 16),
        ],
    )
    def test_matra_counts(self, taal: TaalName, expected_matras: int):
        assert TAAL_REGISTRY[taal].matras == expected_matras

    def test_rupak_sam_is_khali(self):
        """Rupak is special: sam position is also khali."""
        rupak = TAAL_REGISTRY[TaalName.RUPAK]
        assert rupak.sam_position in rupak.khali_positions


class TestVibhagBoundaries:
    def test_rupak_boundaries(self):
        rupak = TAAL_REGISTRY[TaalName.RUPAK]
        assert rupak.vibhag_boundaries == (0, 3, 5)

    def test_teentaal_boundaries(self):
        teentaal = TAAL_REGISTRY[TaalName.TEENTAAL]
        assert teentaal.vibhag_boundaries == (0, 4, 8, 12)


class TestLookupFunctions:
    def test_get_taals_by_matras(self):
        taals_16 = get_taals_by_matras(16)
        assert len(taals_16) == 1
        assert taals_16[0].name == TaalName.TEENTAAL

    def test_get_taals_by_matras_none(self):
        assert get_taals_by_matras(99) == []

    def test_candidate_matra_counts(self):
        counts = get_candidate_matra_counts()
        assert counts == [6, 7, 8, 10, 12, 14, 16]
