from __future__ import annotations

import json
from pathlib import Path

import pytest
from pymatgen.core import Lattice


REFERENCE = Path("docs/phase10f/evidence/phase10f17_periodic_crystal_inspection/math/trusted_reference_comparison.json")


@pytest.mark.parametrize("case", json.loads(REFERENCE.read_text(encoding="utf-8"))["cases"])
def test_periodic_reference_fixture_matches_pymatgen(case: dict[str, object]) -> None:
    distance, image = Lattice(case["lattice"]).get_distance_and_image(
        case["source_fractional"], case["target_fractional"]
    )
    assert distance == pytest.approx(case["distance"], abs=1e-12)
    assert image.tolist() == case["image_offset"]
