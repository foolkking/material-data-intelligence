from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/phase13/reproducibility/manifest.json"


def manifest_hash() -> str:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = value.pop("semanticHash")
    value.pop("generatedAt", None)
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    actual = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    if actual != expected:
        raise SystemExit(f"repro manifest semantic hash mismatch: {actual} != {expected}")
    return actual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=("linux", "windows"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare", nargs=2, type=Path)
    args = parser.parse_args()
    if args.compare:
        rows = [json.loads(path.read_text(encoding="utf-8")) for path in args.compare]
        if rows[0]["semanticHash"] != rows[1]["semanticHash"]:
            raise SystemExit("Linux and Windows Phase13-3 repro manifest hashes differ")
        print(f"PHASE13_3_REPRO_MANIFEST_PARITY_PASS {rows[0]['semanticHash']}")
        return
    if not args.platform or not args.output:
        parser.error("--platform and --output are required unless --compare is used")
    result = {"platform": args.platform, "semanticHash": manifest_hash(), "status": "PASS"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"PHASE13_3_REPRO_MANIFEST_{args.platform.upper()}_PASS {result['semanticHash']}")


if __name__ == "__main__":
    main()
