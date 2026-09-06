from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Keep the diagnostic entrypoint runnable from a clean shell as documented.
# The API package lives below apps/api in the monorepo and is not installed as
# a site package in the local qualification environment.
REPO_ROOT = Path(__file__).resolve().parents[1]
for package_root in (
    REPO_ROOT,
    REPO_ROOT / "apps" / "api",
    # Operations snapshots resolve the configured provider to classify runtime
    # health. Keep the standalone diagnostic entrypoint usable from a clean
    # shell, just like the API package itself.
    REPO_ROOT / "services" / "llm",
    REPO_ROOT / "services" / "workers",
    REPO_ROOT / "packages" / "schemas",
    REPO_ROOT / "packages" / "tool-registry",
    REPO_ROOT / "packages" / "adapters",
    REPO_ROOT / "packages" / "artifact-core",
    REPO_ROOT / "packages" / "material-parsers",
):
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))

def main(argv: list[str] | None = None) -> int:
    from mdi_api.operations import OperationsThresholds, build_operations_snapshot

    parser = argparse.ArgumentParser(
        description="Emit a redacted Phase 14-R PostgreSQL/Redis/MinIO operations snapshot."
    )
    parser.add_argument(
        "--same-stack",
        action="store_true",
        help="Use the repository's local PostgreSQL/Redis/MinIO qualification stack.",
    )
    parser.add_argument("--stale-minutes", type=int, default=15)
    parser.add_argument("--queue-depth", type=int, default=100)
    parser.add_argument("--minimum-workers", type=int, default=5)
    parser.add_argument(
        "--fail-on-attention",
        action="store_true",
        help=(
            "Return exit code 2 when typed alerts are present. Without this "
            "flag the command is diagnostic-only and returns 0 after emitting JSON."
        ),
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit the same machine-readable JSON contract on a single line.",
    )
    args = parser.parse_args(argv)
    if args.same_stack:
        _configure_same_stack()
    snapshot = build_operations_snapshot(
        thresholds=OperationsThresholds(
            stale_minutes=max(1, args.stale_minutes),
            queue_depth=max(0, args.queue_depth),
            minimum_workers=max(0, args.minimum_workers),
        )
    )
    print(
        json.dumps(
            snapshot,
            ensure_ascii=False,
            indent=None if args.compact else 2,
            separators=(",", ":") if args.compact else None,
            sort_keys=True,
        )
    )
    return _exit_code(
        snapshot,
        fail_on_attention=args.fail_on_attention,
    )


def _exit_code(
    snapshot: dict[str, object],
    *,
    fail_on_attention: bool,
) -> int:
    if not fail_on_attention:
        return 0
    return 0 if snapshot.get("status") == "ok" else 2


def _configure_same_stack() -> None:
    """Select the same local service topology used by the qualification workers.

    The API and worker launch scripts inject these values into their process
    environments.  A standalone diagnostic command starts with no inherited
    runtime variables on Windows, so make that selection explicit rather than
    silently reporting the SQLite/local fallback.
    """
    from scripts.phase14r_runtime_environment import apply_same_stack_environment

    # The shared builder overwrites all supported aliases together, so a stale
    # parent shell cannot send only diagnostics to a different service.
    apply_same_stack_environment()


if __name__ == "__main__":
    raise SystemExit(main())
