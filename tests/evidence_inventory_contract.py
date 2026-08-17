from __future__ import annotations

import json
from pathlib import Path


def assert_readable_evidence_inventory(root: Path, manifest: dict) -> set[str]:
    """Validate historical evidence by readable content, not byte fingerprints."""
    entries = manifest["entries"]
    paths = [entry["path"] for entry in entries]
    assert paths
    assert len(paths) == len(set(paths))

    for relative in paths:
        parts = Path(relative).parts
        assert relative and ".." not in parts and not Path(relative).is_absolute()
        path = root / relative
        assert path.is_file() and path.stat().st_size > 0
        if path.suffix.lower() == ".json":
            json.loads(path.read_text(encoding="utf-8"))
        elif path.suffix.lower() in {".md", ".txt"}:
            assert path.read_text(encoding="utf-8").strip()

    return set(paths)
