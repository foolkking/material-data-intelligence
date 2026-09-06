"""Create and retain isolated PostgreSQL/MinIO qualification run directories.

Only runs created under the checked-in policy's run root are managed. Legacy
service directories, active runs, release evidence, symlinks, and malformed
manifests are never retention candidates. Retention is a read-only plan unless
``--apply`` is explicit, and apply moves candidates into a recoverable archive
instead of deleting them.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "config" / "qualification-run-retention.json"
POLICY_SCHEMA = "mdi.qualification-run-retention/1.0"
MANIFEST_SCHEMA = "mdi.qualification-run/1.0"
RUN_ID_PATTERN = re.compile(r"^qual-[0-9]{8}T[0-9]{6}Z-[a-f0-9]{8}$")
TerminalStatus = Literal["COMPLETED", "FAILED"]


@dataclass(frozen=True)
class RetentionCandidate:
    runId: str
    status: TerminalStatus
    ageDays: float
    source: str
    destination: str


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    policy = json.loads(path.read_text(encoding="utf-8"))
    if policy.get("schemaVersion") != POLICY_SCHEMA:
        raise ValueError("Unsupported qualification run retention policy.")
    if policy.get("services") != ["postgresql", "minio"]:
        raise ValueError("Qualification run services must be PostgreSQL and MinIO.")
    if not isinstance(policy.get("ttlDays"), int) or policy["ttlDays"] < 1:
        raise ValueError("Qualification run ttlDays must be a positive integer.")
    for key in ("runRoot", "archiveRoot", "activeMarker", "manifestName"):
        value = policy.get(key)
        if not isinstance(value, str) or not value or Path(value).is_absolute():
            raise ValueError(f"Qualification run policy {key} must be relative.")
    if policy.get("archiveMode") != "MOVE_RECOVERABLE":
        raise ValueError("Qualification retention must use recoverable moves.")
    return policy


def create_run(
    root: Path,
    *,
    policy: dict[str, Any],
    run_id: str | None = None,
    release_evidence: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    repo = _repository_root(root)
    observed_at = _as_utc(now or datetime.now(timezone.utc))
    identity = run_id or _new_run_id(observed_at)
    _validate_run_id(identity)
    run_root = _managed_root(repo, policy["runRoot"])
    run_directory = run_root / identity
    if run_directory.exists():
        raise FileExistsError(f"Qualification run already exists: {identity}")
    run_directory.mkdir(parents=True)
    service_paths = {
        service: run_directory / service for service in policy["services"]
    }
    for service_path in service_paths.values():
        service_path.mkdir()
    manifest = {
        "schemaVersion": MANIFEST_SCHEMA,
        "runId": identity,
        "status": "ACTIVE",
        "createdAt": observed_at.isoformat(),
        "completedAt": None,
        "releaseEvidence": bool(release_evidence),
        "services": {
            service: service_paths[service].relative_to(repo).as_posix()
            for service in policy["services"]
        },
    }
    _write_json(run_directory / policy["manifestName"], manifest)
    _write_json(
        run_directory / policy["activeMarker"],
        {
            "schemaVersion": MANIFEST_SCHEMA,
            "runId": identity,
            "ownerPid": os.getpid(),
            "startedAt": observed_at.isoformat(),
        },
    )
    return _run_projection(repo, run_directory, manifest)


def finish_run(
    root: Path,
    *,
    policy: dict[str, Any],
    run_id: str,
    status: TerminalStatus,
    now: datetime | None = None,
) -> dict[str, Any]:
    repo = _repository_root(root)
    run_directory = _run_directory(repo, policy, run_id)
    manifest = _load_valid_manifest(run_directory, policy)
    if manifest["status"] != "ACTIVE":
        raise ValueError("Only an active qualification run can be finished.")
    active_marker = run_directory / policy["activeMarker"]
    if not active_marker.is_file() or active_marker.is_symlink():
        raise ValueError("Active qualification run marker is missing or unsafe.")
    completed_at = _as_utc(now or datetime.now(timezone.utc))
    manifest["status"] = status
    manifest["completedAt"] = completed_at.isoformat()
    _write_json(run_directory / policy["manifestName"], manifest)
    active_marker.unlink()
    return _run_projection(repo, run_directory, manifest)


def retention_plan(
    root: Path,
    *,
    policy: dict[str, Any],
    now: datetime | None = None,
    ttl_days: int | None = None,
) -> dict[str, Any]:
    repo = _repository_root(root)
    observed_at = _as_utc(now or datetime.now(timezone.utc))
    effective_ttl = policy["ttlDays"] if ttl_days is None else ttl_days
    if not isinstance(effective_ttl, int) or effective_ttl < 1:
        raise ValueError("Qualification run retention TTL must be at least one day.")
    run_root = _managed_root(repo, policy["runRoot"])
    archive_root = _managed_root(repo, policy["archiveRoot"])
    candidates: list[RetentionCandidate] = []
    protected: dict[str, list[str]] = {
        "active": [],
        "releaseEvidence": [],
        "withinTtl": [],
        "invalid": [],
    }
    if run_root.exists():
        for run_directory in sorted(run_root.iterdir(), key=lambda item: item.name):
            if not run_directory.is_dir() or run_directory.is_symlink():
                protected["invalid"].append(run_directory.name)
                continue
            try:
                manifest = _load_valid_manifest(run_directory, policy)
            except (OSError, ValueError, json.JSONDecodeError):
                protected["invalid"].append(run_directory.name)
                continue
            run_id = manifest["runId"]
            if (
                manifest["status"] == "ACTIVE"
                or (run_directory / policy["activeMarker"]).exists()
            ):
                protected["active"].append(run_id)
                continue
            if manifest["releaseEvidence"]:
                protected["releaseEvidence"].append(run_id)
                continue
            completed_at = _parse_timestamp(manifest["completedAt"])
            age_days = (observed_at - completed_at).total_seconds() / 86400
            if age_days < effective_ttl:
                protected["withinTtl"].append(run_id)
                continue
            destination = archive_root / run_id
            candidates.append(
                RetentionCandidate(
                    runId=run_id,
                    status=manifest["status"],
                    ageDays=round(age_days, 3),
                    source=run_directory.relative_to(repo).as_posix(),
                    destination=destination.relative_to(repo).as_posix(),
                )
            )
    return {
        "schemaVersion": POLICY_SCHEMA,
        "mode": "dry-run",
        "observedAt": observed_at.isoformat(),
        "ttlDays": effective_ttl,
        "candidateCount": len(candidates),
        "candidates": [asdict(candidate) for candidate in candidates],
        "protected": protected,
        "legacyDirectoriesManaged": False,
        "archiveMode": "MOVE_RECOVERABLE",
    }


def apply_retention(
    root: Path,
    *,
    policy: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    repo = _repository_root(root)
    archive_root = _managed_root(repo, policy["archiveRoot"])
    observed_at = _parse_timestamp(plan.get("observedAt"))
    effective_ttl = plan.get("ttlDays")
    current_plan = retention_plan(
        repo,
        policy=policy,
        now=observed_at,
        ttl_days=effective_ttl,
    )
    current_candidates = {
        candidate["runId"] for candidate in current_plan["candidates"]
    }
    validated: list[tuple[str, Path, Path]] = []
    seen: set[str] = set()
    for candidate in plan.get("candidates", []):
        run_id = str(candidate.get("runId") or "")
        if run_id in seen:
            raise ValueError(f"Duplicate qualification run candidate: {run_id}")
        seen.add(run_id)
        if run_id not in current_candidates:
            raise ValueError(
                f"Qualification run is no longer retention eligible: {run_id}"
            )
        source = _run_directory(repo, policy, run_id)
        destination = archive_root / run_id
        manifest = _load_valid_manifest(source, policy)
        if manifest["status"] == "ACTIVE":
            raise ValueError(f"Active qualification run cannot be archived: {run_id}")
        if manifest["releaseEvidence"]:
            raise ValueError(f"Release evidence cannot be archived: {run_id}")
        if (source / policy["activeMarker"]).exists():
            raise ValueError(f"Active marker still exists for qualification run: {run_id}")
        if destination.exists():
            raise FileExistsError(destination)
        validated.append((run_id, source, destination))

    moved: list[dict[str, str]] = []
    for run_id, source, destination in validated:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        moved.append(
            {
                "runId": run_id,
                "source": source.relative_to(repo).as_posix(),
                "destination": destination.relative_to(repo).as_posix(),
            }
        )
    result = dict(plan)
    result["mode"] = "apply"
    result["movedCount"] = len(moved)
    result["moved"] = moved
    return result


def _run_projection(
    repo: Path,
    run_directory: Path,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        **manifest,
        "directory": run_directory.relative_to(repo).as_posix(),
        "serviceDirectories": manifest["services"],
    }


def _new_run_id(now: datetime) -> str:
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    return f"qual-{timestamp}-{secrets.token_hex(4)}"


def _validate_run_id(run_id: str) -> None:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError(
            "Qualification run ID must match qual-YYYYMMDDTHHMMSSZ-<8 hex>."
        )


def _repository_root(path: Path) -> Path:
    root = path.resolve()
    if not (root / ".git").exists():
        raise ValueError(f"Qualification root must contain .git: {root}")
    return root


def _managed_root(repo: Path, relative: str) -> Path:
    target = (repo / relative).resolve()
    try:
        target.relative_to(repo)
    except ValueError as exc:
        raise ValueError("Qualification policy path escapes repository.") from exc
    return target


def _run_directory(
    repo: Path,
    policy: dict[str, Any],
    run_id: str,
) -> Path:
    _validate_run_id(run_id)
    target = _managed_root(repo, policy["runRoot"]) / run_id
    if target.is_symlink():
        raise ValueError("Qualification run directory cannot be a symlink.")
    return target


def _load_valid_manifest(
    run_directory: Path,
    policy: dict[str, Any],
) -> dict[str, Any]:
    manifest_path = run_directory / policy["manifestName"]
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ValueError("Qualification run manifest is missing or unsafe.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schemaVersion") != MANIFEST_SCHEMA:
        raise ValueError("Unsupported qualification run manifest.")
    if manifest.get("runId") != run_directory.name:
        raise ValueError("Qualification manifest identity does not match its directory.")
    _validate_run_id(manifest["runId"])
    if manifest.get("status") not in {"ACTIVE", "COMPLETED", "FAILED"}:
        raise ValueError("Qualification run status is invalid.")
    if not isinstance(manifest.get("releaseEvidence"), bool):
        raise ValueError("Qualification releaseEvidence must be boolean.")
    expected_services = {
        service: (run_directory / service).resolve()
        for service in policy["services"]
    }
    service_payload = manifest.get("services")
    if not isinstance(service_payload, dict):
        raise ValueError("Qualification service directory map is required.")
    repo = _repository_root_from_run(run_directory, policy)
    for service, expected_path in expected_services.items():
        recorded = service_payload.get(service)
        if not isinstance(recorded, str):
            raise ValueError("Qualification service directory is missing.")
        recorded_path = (repo / recorded).resolve()
        if recorded_path != expected_path or not expected_path.is_dir():
            raise ValueError("Qualification service directory identity is invalid.")
    if manifest["status"] == "ACTIVE":
        _parse_timestamp(manifest.get("createdAt"))
        if manifest.get("completedAt") is not None:
            raise ValueError("Active qualification run cannot have completedAt.")
    else:
        _parse_timestamp(manifest.get("completedAt"))
    return manifest


def _repository_root_from_run(
    run_directory: Path,
    policy: dict[str, Any],
) -> Path:
    run_root_parts = len(Path(policy["runRoot"]).parts)
    repo = run_directory
    for _ in range(run_root_parts + 1):
        repo = repo.parent
    return _repository_root(repo)


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("Qualification run timestamp is required.")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Qualification run timestamp must include timezone.")
    return parsed.astimezone(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("Qualification run timestamps must be timezone-aware.")
    return value.astimezone(timezone.utc)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--ttl-days", type=int)
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--create-run",
        nargs="?",
        const="AUTO",
        metavar="RUN_ID",
        help="create an isolated active qualification run",
    )
    action.add_argument(
        "--finish-run",
        metavar="RUN_ID",
        help="mark an active qualification run completed or failed",
    )
    parser.add_argument(
        "--status",
        choices=("COMPLETED", "FAILED"),
        default="COMPLETED",
    )
    parser.add_argument("--release-evidence", action="store_true")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="move expired terminal runs to the recoverable archive",
    )
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy.resolve())
        if args.create_run is not None:
            if args.apply or args.ttl_days is not None:
                raise ValueError("Create-run does not accept retention options.")
            payload = create_run(
                args.root,
                policy=policy,
                run_id=None if args.create_run == "AUTO" else args.create_run,
                release_evidence=args.release_evidence,
            )
        elif args.finish_run is not None:
            if args.apply or args.release_evidence or args.ttl_days is not None:
                raise ValueError("Finish-run does not accept retention options.")
            payload = finish_run(
                args.root,
                policy=policy,
                run_id=args.finish_run,
                status=args.status,
            )
        else:
            if args.release_evidence:
                raise ValueError("--release-evidence is valid only with --create-run.")
            payload = retention_plan(
                args.root,
                policy=policy,
                ttl_days=args.ttl_days,
            )
            if args.apply:
                payload = apply_retention(
                    args.root,
                    policy=policy,
                    plan=payload,
                )
        print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: qualification run retention failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
