from __future__ import annotations

from pathlib import Path

from .models import DetectedFormat


def detect_format(path: str | Path) -> DetectedFormat:
    file_path = Path(path)
    name = file_path.name.lower()
    suffix = file_path.suffix.lower()

    if suffix == ".zip":
        return DetectedFormat.archive
    if suffix == ".cif":
        return DetectedFormat.cif
    if suffix == ".csv":
        return DetectedFormat.csv
    if suffix == ".json":
        return DetectedFormat.json_limited
    if suffix == ".extxyz":
        return DetectedFormat.extxyz
    if suffix == ".xyz":
        return _detect_xyz_kind(file_path)
    if name in {"poscar", "contcar"} or name.startswith(("poscar.", "contcar.")):
        return DetectedFormat.poscar

    try:
        head = file_path.read_text(encoding="utf-8", errors="ignore")[:4096]
    except OSError:
        return DetectedFormat.unknown

    if "_cell_length_a" in head and "_atom_site" in head:
        return DetectedFormat.cif
    if _looks_like_poscar(head):
        return DetectedFormat.poscar
    return DetectedFormat.unknown


def _detect_xyz_kind(path: Path) -> DetectedFormat:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return DetectedFormat.unknown
    if len(lines) >= 2 and "Lattice=" in lines[1]:
        return DetectedFormat.extxyz
    if lines and lines[0].strip().isdigit():
        return DetectedFormat.xyz
    return DetectedFormat.unknown


def _looks_like_poscar(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 7:
        return False
    try:
        float(lines[1].split()[0])
        for idx in range(2, 5):
            parts = lines[idx].split()
            if len(parts) < 3:
                return False
            [float(part) for part in parts[:3]]
    except ValueError:
        return False
    return True
