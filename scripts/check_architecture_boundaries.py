"""B0-6 deterministic canonical import-boundary guard."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from scripts.architecture_scan import (
    ALLOWLISTED_TRANSITION_EDGES,
    allowlisted_edges,
    frontend_compatibility_edges,
    forbidden_edges,
    scan_imports,
)


def build_guard_report() -> dict[str, object]:
    edges = scan_imports()
    findings = forbidden_edges(edges) + frontend_compatibility_edges()
    return {
        "schemaVersion": "ArchitectureGuard/1.0",
        "scope": (
            "apps/api/mdi_api/{application,domain,infrastructure,bootstrap,transport,compatibility};"
            "apps/web/{features,scientific-viewers,shared}"
        ),
        "rules": [
            "CANONICAL_TO_COMPATIBILITY",
            "DOMAIN_TO_TRANSPORT",
            "DOMAIN_TO_BOOTSTRAP",
            "DOMAIN_TO_CONCRETE_INFRASTRUCTURE",
            "APPLICATION_TO_TRANSPORT",
            "APPLICATION_TO_CONCRETE_INFRASTRUCTURE",
        ],
        "allowlist": [
            {"source": source, "target": target, "reason": reason}
            for (source, target), reason in sorted(ALLOWLISTED_TRANSITION_EDGES.items())
        ],
        "allowlistedEdges": allowlisted_edges(edges),
        "forbiddenEdges": findings,
        "status": "PASS" if not findings else "FAIL",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the deterministic report")
    args = parser.parse_args(argv)
    report = build_guard_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        print(f"{report['status']}: {len(report['forbiddenEdges'])} forbidden canonical import edge(s)")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
