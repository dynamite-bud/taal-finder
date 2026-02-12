"""Registry of known taal definitions."""

from taal_finder.models import TaalDefinition, TaalName

TAAL_REGISTRY: dict[TaalName, TaalDefinition] = {
    TaalName.DADRA: TaalDefinition(
        name=TaalName.DADRA,
        matras=6,
        vibhags=(3, 3),
        sam_position=0,
        khali_positions=(3,),
        tali_positions=(0,),
        common_layas=("madhya", "drut"),
        hindi_name="ताल दादरा",
    ),
    TaalName.RUPAK: TaalDefinition(
        name=TaalName.RUPAK,
        matras=7,
        vibhags=(3, 2, 2),
        sam_position=0,
        khali_positions=(0,),  # Rupak is unusual: sam IS khali
        tali_positions=(3, 5),
        common_layas=("madhya", "drut"),
        hindi_name="ताल रूपक",
    ),
    TaalName.KEHERWA: TaalDefinition(
        name=TaalName.KEHERWA,
        matras=8,
        vibhags=(4, 4),
        sam_position=0,
        khali_positions=(4,),
        tali_positions=(0,),
        common_layas=("madhya", "drut"),
        hindi_name="ताल कहरवा",
    ),
    TaalName.JHAPTAAL: TaalDefinition(
        name=TaalName.JHAPTAAL,
        matras=10,
        vibhags=(2, 3, 2, 3),
        sam_position=0,
        khali_positions=(5,),
        tali_positions=(0, 2, 7),
        common_layas=("vilambit", "madhya", "drut"),
        hindi_name="ताल झपताल",
    ),
    TaalName.EKTAAL: TaalDefinition(
        name=TaalName.EKTAAL,
        matras=12,
        vibhags=(2, 2, 2, 2, 2, 2),
        sam_position=0,
        khali_positions=(2, 8),
        tali_positions=(0, 4, 6, 10),
        common_layas=("vilambit", "madhya", "drut"),
        hindi_name="ताल एकताल",
    ),
    TaalName.DEEPCHANDI: TaalDefinition(
        name=TaalName.DEEPCHANDI,
        matras=14,
        vibhags=(3, 4, 3, 4),
        sam_position=0,
        khali_positions=(7,),
        tali_positions=(0, 3, 10),
        common_layas=("vilambit", "madhya"),
        hindi_name="ताल दीपचंदी",
    ),
    TaalName.TEENTAAL: TaalDefinition(
        name=TaalName.TEENTAAL,
        matras=16,
        vibhags=(4, 4, 4, 4),
        sam_position=0,
        khali_positions=(8,),
        tali_positions=(0, 4, 12),
        common_layas=("vilambit", "madhya", "drut"),
        hindi_name="ताल तीनताल",
    ),
}


def get_taals_by_matras(matras: int) -> list[TaalDefinition]:
    """Return all taal definitions with the given matra count."""
    return [t for t in TAAL_REGISTRY.values() if t.matras == matras]


def get_candidate_matra_counts() -> list[int]:
    """Return sorted list of all known taal matra counts."""
    return sorted({t.matras for t in TAAL_REGISTRY.values()})
