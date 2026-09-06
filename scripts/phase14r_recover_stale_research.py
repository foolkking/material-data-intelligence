from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
for package_root in (
    REPO_ROOT / "apps" / "api",
    REPO_ROOT / "services" / "workers",
    REPO_ROOT / "services" / "llm",
    REPO_ROOT / "packages" / "schemas",
    REPO_ROOT / "packages" / "tool-registry",
    REPO_ROOT / "packages" / "adapters",
    REPO_ROOT / "packages" / "artifact-core",
    REPO_ROOT / "packages" / "material-parsers",
):
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))


def main() -> int:
    from mdi_api.research_agent.recovery import StaleResearchRecoveryService

    parser = argparse.ArgumentParser(
        description="Diagnose or safely republish stale product ResearchTurns."
    )
    parser.add_argument("--stale-minutes", type=int, default=15)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Wake recoverable durable identities. Omit for a read-only diagnosis.",
    )
    args = parser.parse_args()
    service = StaleResearchRecoveryService()
    if args.apply:
        payload = service.reconcile_stale(
            stale_minutes=max(1, args.stale_minutes),
            limit=max(1, args.limit),
        )
    else:
        product, qualification = service.list_stale(
            stale_minutes=max(1, args.stale_minutes),
            limit=max(1, args.limit),
        )
        payload = {
            "mode": "dry-run",
            "productCandidates": [
                {
                    "turnId": str(item["id"]),
                    "projectId": str(item["project_id"]),
                    "status": str(item["status"]),
                    "action": item.get("action_type"),
                    "updatedAt": item["updated_at"].isoformat(),
                }
                for item in product
            ],
            "qualificationRetained": len(qualification),
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
