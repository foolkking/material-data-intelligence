from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SEAL_ROOT = ROOT / "docs/phase13/evidence/phase13_0_release_scope_seal"
FIX_FORWARD_ROOT = ROOT / "docs/phase13/evidence/phase13_1_product_entry_fix_forward"


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def semantic_hash(path: Path) -> str:
    value = json.loads(path.read_text(encoding="utf-8"))
    expected = value.pop("semanticHash")
    actual = canonical_hash(value)
    if actual != expected:
        raise SystemExit(f"semantic hash mismatch: {path}: {actual} != {expected}")
    return actual


def current_result() -> dict[str, str]:
    fact_hash = semantic_hash(SEAL_ROOT / "initial_release_fact_model.json")
    scope_hash = semantic_hash(FIX_FORWARD_ROOT / "initial_release_scope_baseline.json")
    fact_impact = json.loads((FIX_FORWARD_ROOT / "fact_model_hash_impact.json").read_text(encoding="utf-8"))
    scope_impact = json.loads((FIX_FORWARD_ROOT / "scope_baseline_hash_impact.json").read_text(encoding="utf-8"))
    if fact_impact["impact"] != "NO" or fact_impact["old"] != fact_hash or fact_impact["current"] != fact_hash:
        raise SystemExit("Fact Model impact record does not preserve the sealed authority")
    if scope_impact["impact"] != "YES" or scope_impact["current"] != scope_hash:
        raise SystemExit("Scope Baseline impact record does not match the fix-forward authority")
    return {"factModelHash": fact_hash, "scopeBaselineHash": scope_hash}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare", nargs=2, type=Path, metavar=("LINUX", "WINDOWS"))
    args = parser.parse_args()
    if args.compare:
        linux = json.loads(args.compare[0].read_text(encoding="utf-8"))
        windows = json.loads(args.compare[1].read_text(encoding="utf-8"))
        if linux != windows:
            raise SystemExit(f"cross-platform semantic hash mismatch: {linux} != {windows}")
        print(f"PHASE13_1_FIX_FORWARD_HASH_CROSS_PLATFORM_PASS {linux['scopeBaselineHash']}")
        return
    result = current_result()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    print(f"PHASE13_1_FIX_FORWARD_HASH_PASS {result['scopeBaselineHash']}")


if __name__ == "__main__":
    main()
