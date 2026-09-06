"""Read-only disk-capacity gate for builds, tests, evidence and services."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable


GIB = 1024**3
DEFAULT_MINIMUM_FREE_BYTES = 5 * GIB
DEFAULT_WARNING_FREE_BYTES = 10 * GIB


def _positive_int(
    explicit: int | None,
    environment_name: str,
    default: int,
) -> int:
    raw: int | str | None = explicit
    if raw is None:
        raw = os.getenv(environment_name)
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(environment_name) from exc
    if value < 1:
        raise ValueError(environment_name)
    return value


def _configured_paths(explicit: Iterable[str]) -> list[str]:
    paths = [item for item in explicit if str(item).strip()]
    for name in (
        "MDI_POSTGRES_DATA_DIR",
        "MDI_MINIO_DATA_DIR",
        "MINIO_DATA_DIR",
        "MDI_ARTIFACT_ROOT",
    ):
        value = os.getenv(name)
        if value:
            paths.append(value)
    return paths


def _volume_snapshot(
    paths: Iterable[str],
    *,
    minimum: int,
    warning: int,
) -> list[dict[str, Any]]:
    volumes: dict[str, dict[str, Any]] = {}
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve(strict=True)
        anchor = path.anchor or str(path)
        if anchor in volumes:
            continue
        usage = shutil.disk_usage(path)
        state = (
            "critical"
            if usage.free < minimum
            else "warning"
            if usage.free < warning
            else "ok"
        )
        volumes[anchor] = {
            "root": anchor,
            "availableFreeBytes": usage.free,
            "totalBytes": usage.total,
            "state": state,
        }
    return list(volumes.values())


def evaluate(
    *,
    check_paths: Iterable[str],
    minimum_free_bytes: int | None = None,
    warning_free_bytes: int | None = None,
    fallback_path: str | None = None,
) -> tuple[dict[str, Any], int]:
    try:
        minimum = _positive_int(
            minimum_free_bytes,
            "MDI_DISK_MIN_FREE_BYTES",
            DEFAULT_MINIMUM_FREE_BYTES,
        )
        warning = _positive_int(
            warning_free_bytes,
            "MDI_DISK_WARN_FREE_BYTES",
            DEFAULT_WARNING_FREE_BYTES,
        )
        if warning < minimum:
            raise ValueError("MDI_DISK_WARN_FREE_BYTES")
    except ValueError:
        return _result(
            status="error",
            code="MDI_DISK_PREFLIGHT_CONFIGURATION_INVALID",
            minimum=0,
            warning=0,
            volumes=[],
        ), 64

    configured = _configured_paths(check_paths)
    if not configured:
        configured = [str(Path(__file__).resolve().parents[1])]
    try:
        volumes = _volume_snapshot(
            configured,
            minimum=minimum,
            warning=warning,
        )
        fallback = _fallback_snapshot(
            fallback_path or os.getenv("MDI_DISK_FALLBACK_PATH"),
            minimum=minimum,
            warning=warning,
        )
    except (OSError, RuntimeError):
        return _result(
            status="error",
            code="MDI_DISK_PATH_UNAVAILABLE",
            minimum=minimum,
            warning=warning,
            volumes=[],
        ), 66

    if any(item["state"] == "critical" for item in volumes):
        return _result(
            status="error",
            code="MDI_DISK_SPACE_CRITICAL",
            minimum=minimum,
            warning=warning,
            volumes=volumes,
            fallback=fallback,
        ), 78
    status = (
        "warning"
        if any(item["state"] == "warning" for item in volumes)
        else "ok"
    )
    return _result(
        status=status,
        code="MDI_DISK_PREFLIGHT_OK",
        minimum=minimum,
        warning=warning,
        volumes=volumes,
        fallback=fallback,
    ), 0


def _fallback_snapshot(
    raw_path: str | None,
    *,
    minimum: int,
    warning: int,
) -> dict[str, Any] | None:
    if not raw_path:
        return None
    path = Path(raw_path).expanduser().resolve(strict=True)
    volume = _volume_snapshot([str(path)], minimum=minimum, warning=warning)[0]
    return {
        "configured": True,
        "path": str(path),
        "availableFreeBytes": volume["availableFreeBytes"],
        "state": volume["state"],
    }


def _result(
    *,
    status: str,
    code: str,
    minimum: int,
    warning: int,
    volumes: list[dict[str, Any]],
    fallback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schemaVersion": "phase14r-disk-preflight/1.0",
        "status": status,
        "code": code,
        "readOnly": True,
        "minimumFreeBytes": minimum,
        "warningFreeBytes": warning,
        "volumes": volumes,
        "configuredFallback": fallback,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-path", action="append", default=[])
    parser.add_argument("--minimum-free-bytes", type=int)
    parser.add_argument("--warning-free-bytes", type=int)
    parser.add_argument("--fallback-path")
    args = parser.parse_args()
    payload, return_code = evaluate(
        check_paths=args.check_path,
        minimum_free_bytes=args.minimum_free_bytes,
        warning_free_bytes=args.warning_free_bytes,
        fallback_path=args.fallback_path,
    )
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return return_code


if __name__ == "__main__":
    sys.exit(main())
