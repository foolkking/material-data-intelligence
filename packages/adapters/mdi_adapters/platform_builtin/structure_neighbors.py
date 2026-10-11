"""Bounded display-neighbor geometry shared by source previews and tools.

These are distance candidates, not chemical bond assignments. No source is
modified and no external resources or executable payloads are consumed.
"""

from __future__ import annotations

from dataclasses import dataclass
import heapq
from itertools import product
from typing import Any, Sequence

from ase.data import atomic_numbers, covalent_radii
import numpy as np


COVALENT_RADIUS_SCALE = 1.15
COVALENT_RADIUS_REFERENCE = "Cordero et al. 2008 / ASE; DOI 10.1039/B801115J"
COVALENT_RADIUS_MAX_ATOMIC_NUMBER = 96
MAX_PREVIEW_SITES = 256
MAX_PREVIEW_BONDS = 2048
MAX_PAIR_EVALUATIONS = 2_000_000
MAX_IMAGE_OFFSET = 3


class NeighborPreviewLimit(ValueError):
    """The complete requested search cannot fit the bounded preview policy."""


@dataclass(frozen=True)
class DisplayNeighbors:
    bonds: list[dict[str, Any]]
    candidate_count: int
    missing_elements: tuple[str, ...]


def element_covalent_radius(element: str) -> float | None:
    number = atomic_numbers.get(element)
    # The Cordero table distributed by ASE covers H through Cm. Later
    # elements use ASE's `missing = 2.0`, whereas Pa's real tabulated radius
    # is also 2.0. Coverage, rather than the numeric value, distinguishes them.
    if number is None or not 1 <= number <= COVALENT_RADIUS_MAX_ATOMIC_NUMBER or number >= len(covalent_radii):
        return None
    radius = float(covalent_radii[number])
    return radius if np.isfinite(radius) and radius > 0 else None


def covalent_radius_neighbors(
    elements: Sequence[str],
    positions: Sequence[Sequence[float]],
    lattice: Sequence[Sequence[float]],
    pbc: Sequence[bool],
    *,
    max_bonds: int = MAX_PREVIEW_BONDS,
) -> DisplayNeighbors:
    """Enumerate all in-policy pairs before applying a stable display cap.

    Reciprocal-vector bounds cover triclinic cells and periodic self images.
    Searches needing larger offsets/work are refused instead of presenting an
    incomplete neighbor graph as complete. Peak temporary arrays are N by N.
    """
    count = len(elements)
    if not 0 < count <= MAX_PREVIEW_SITES:
        raise NeighborPreviewLimit("VIEWER_NEIGHBOR_SITE_LIMIT")
    if isinstance(max_bonds, bool) or not isinstance(max_bonds, int) or not 0 <= max_bonds <= MAX_PREVIEW_BONDS:
        raise ValueError("VIEWER_NEIGHBOR_BOND_LIMIT")
    if len(pbc) != 3 or any(type(value) is not bool for value in pbc):
        raise ValueError("VIEWER_NEIGHBOR_PBC_INVALID")
    xyz = np.asarray(positions, dtype=float)
    matrix = np.asarray(lattice, dtype=float)
    if xyz.shape != (count, 3) or matrix.shape != (3, 3) or not np.isfinite(xyz).all() or not np.isfinite(matrix).all():
        raise ValueError("VIEWER_NEIGHBOR_GEOMETRY_INVALID")
    radii = np.asarray([element_covalent_radius(element) or 0.0 for element in elements])
    missing = tuple(sorted({element for element, radius in zip(elements, radii, strict=True) if radius == 0}))
    if not np.any(radii):
        return DisplayNeighbors([], 0, missing)
    cutoffs = COVALENT_RADIUS_SCALE * (radii[:, None] + radii[None, :])
    valid_radii = (radii[:, None] > 0) & (radii[None, :] > 0)
    bounds = [0, 0, 0]
    if any(pbc):
        try:
            reciprocal = np.linalg.inv(matrix)
        except np.linalg.LinAlgError as exc:
            raise ValueError("VIEWER_NEIGHBOR_CELL_INVALID") from exc
        fractional = xyz @ reciprocal
        extents = np.ptp(fractional, axis=0)
        possible = extents + float(cutoffs.max()) * np.linalg.norm(reciprocal, axis=0)
        if not np.isfinite(possible).all():
            raise NeighborPreviewLimit("VIEWER_NEIGHBOR_OFFSET_LIMIT")
        for axis, periodic in enumerate(pbc):
            if periodic:
                bounds[axis] = int(np.floor(possible[axis] + 1e-9))
        if max(bounds) > MAX_IMAGE_OFFSET:
            raise NeighborPreviewLimit("VIEWER_NEIGHBOR_OFFSET_LIMIT")
    offset_count = int(np.prod([2 * bound + 1 for bound in bounds]))
    if offset_count * count * count > MAX_PAIR_EVALUATIONS:
        raise NeighborPreviewLimit("VIEWER_NEIGHBOR_WORK_LIMIT")

    # Negated topology keys make this a bounded max heap. Keeping at most K
    # pairs from each sorted offset slice still retains the global first K.
    kept: list[tuple[int, int, int, int, int]] = []
    candidate_count = 0
    pair_delta = xyz[None, :, :] - xyz[:, None, :]
    upper = np.triu(np.ones((count, count), dtype=bool), k=1)
    diagonal = np.eye(count, dtype=bool)
    cutoff_squared = cutoffs * cutoffs
    for offset in product(*(range(-bound, bound + 1) for bound in bounds)):
        displacement = pair_delta + np.asarray(offset) @ matrix
        distance_squared = np.einsum("ijk,ijk->ij", displacement, displacement)
        canonical_pairs = upper | diagonal if offset < (0, 0, 0) else upper
        candidates = valid_radii & canonical_pairs & (distance_squared > 1e-12) & (distance_squared <= cutoff_squared + 1e-12)
        candidate_count += int(np.count_nonzero(candidates))
        if not max_bonds:
            continue
        for first, second in np.argwhere(candidates)[:max_bonds]:
            key = (int(first), int(second), *offset)
            negative = tuple(-value for value in key)
            if len(kept) < max_bonds:
                heapq.heappush(kept, negative)
            elif negative > kept[0]:
                heapq.heapreplace(kept, negative)

    bonds: list[dict[str, Any]] = []
    for first, second, x, y, z in sorted(tuple(-value for value in key) for key in kept):
        offset = (x, y, z)
        delta = xyz[second] + np.asarray(offset) @ matrix - xyz[first]
        bonds.append({
            "id": f"bond:{first}:0,0,0->{second}:{x},{y},{z}",
            "from": {"site_index": first, "image_offset": [0, 0, 0]},
            "to": {"site_index": second, "image_offset": list(offset)},
            "displacement_cartesian": [round(float(value), 8) for value in delta],
            "distance_angstrom": round(float(np.linalg.norm(delta)), 8),
            "source": "distance_cutoff",
            "authoritative": False,
        })
    return DisplayNeighbors(bonds, candidate_count, missing)
