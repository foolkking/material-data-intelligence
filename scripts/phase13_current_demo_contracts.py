"""Current Phase 13 canonical demo contracts.

Historical generators keep their sealed inputs immutable. Current rerun
authorities apply reviewer-approved contract corrections here.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from scripts.generate_phase13_1_product_entry_fix_forward import DEMO_SPECS as HISTORICAL_DEMO_SPECS


DEMO1_CANONICAL_PROMPT = (
    "Explore this materials dataset, summarize its quality, and map its "
    "compositions in composition space."
)


def _current_specs() -> tuple[dict[str, Any], ...]:
    specs = deepcopy(HISTORICAL_DEMO_SPECS)
    specs[0]["prompt"] = DEMO1_CANONICAL_PROMPT
    specs[0]["alternatePrompt"] = (
        "Summarize this materials dataset and show its composition-space "
        "embedding and bounded clusters."
    )
    specs[0]["expectedTools"] = (
        "dataset.composition_space",
        "dataset.materials_explorer",
    )
    specs[4]["fixtures"] = (
        (
            "P13-DEMO-05-FIX-01",
            "docs/phase10h/fixtures/phonon_contract/stable_band.json",
            "typed_phonon_band_import",
        ),
        (
            "P13-DEMO-05-FIX-02",
            "docs/phase10h/fixtures/phonon_contract/total_dos.json",
            "typed_phonon_dos_import",
        ),
        ("P13-DEMO-05-FIX-03", "tests/fixtures/structures/POSCAR", "parse"),
    )
    return tuple(specs)


CURRENT_DEMO_SPECS = _current_specs()
