from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED = "2f255942d4557569f7f01d6d1118a5cec1bc209f03bf1cf92b21d65fb65be844"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare", nargs=2, type=Path)
    args = parser.parse_args()
    if args.compare:
        left, right = (load(path) for path in args.compare)
        if left["semanticHash"] != right["semanticHash"]:
            raise SystemExit("Phase13-6 Linux/Windows manifest parity failed")
        print("PHASE13_6_LINUX_WINDOWS_MANIFEST_PARITY_PASS")
        return
    if not args.platform or not args.manifest or not args.output:
        parser.error("--platform, --manifest, and --output are required")
    manifest = load(args.manifest)
    semantic = {key: value for key, value in manifest.items() if key not in {"semanticHash", "generatedAt"}}
    actual = hashlib.sha256(
        json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if manifest["semanticHash"] != actual or actual != EXPECTED:
        raise SystemExit("Phase13-6 InitialReleaseManifest authority drift")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"schemaVersion": "Phase13_6ManifestReplay/1.0", "platform": args.platform, "semanticHash": actual, "status": "PASS"}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(f"PHASE13_6_{args.platform.upper()}_MANIFEST_PASS")


if __name__ == "__main__":
    main()
