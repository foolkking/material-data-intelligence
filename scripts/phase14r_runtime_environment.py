from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class SameStackRuntimeTopology:
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 55434
    postgres_database: str = "mdi"
    postgres_user: str = "mdi"
    redis_url: str = "redis://127.0.0.1:6379/13"
    minio_endpoint: str = "http://127.0.0.1:9000"
    minio_access_key: str = "mdi-local"
    minio_secret_key: str = "mdi-local-dev"
    minio_bucket: str = "mdi-artifacts"


def resolve_same_stack_topology(
    environ: Mapping[str, str] | None = None,
) -> SameStackRuntimeTopology:
    """Resolve the one local qualification topology used by every process role.

    Dedicated ``MDI_PHASE14R_*`` inputs allow an operator or isolated test to
    move one service without inheriting stale generic runtime aliases. The
    returned environment sets all supported aliases consistently.
    """

    source = environ if environ is not None else os.environ
    return SameStackRuntimeTopology(
        postgres_host=_value(
            source,
            "MDI_PHASE14R_POSTGRES_HOST",
            SameStackRuntimeTopology.postgres_host,
        ),
        postgres_port=_port(
            source,
            "MDI_PHASE14R_POSTGRES_PORT",
            SameStackRuntimeTopology.postgres_port,
        ),
        postgres_database=_value(
            source,
            "MDI_PHASE14R_POSTGRES_DB",
            SameStackRuntimeTopology.postgres_database,
        ),
        postgres_user=_value(
            source,
            "MDI_PHASE14R_POSTGRES_USER",
            SameStackRuntimeTopology.postgres_user,
        ),
        redis_url=_value(
            source,
            "MDI_PHASE14R_REDIS_URL",
            SameStackRuntimeTopology.redis_url,
        ),
        minio_endpoint=_value(
            source,
            "MDI_PHASE14R_MINIO_ENDPOINT",
            SameStackRuntimeTopology.minio_endpoint,
        ),
        minio_access_key=_value(
            source,
            "MDI_PHASE14R_MINIO_ACCESS_KEY",
            SameStackRuntimeTopology.minio_access_key,
        ),
        minio_secret_key=_value(
            source,
            "MDI_PHASE14R_MINIO_SECRET_KEY",
            SameStackRuntimeTopology.minio_secret_key,
        ),
        minio_bucket=_value(
            source,
            "MDI_PHASE14R_MINIO_BUCKET",
            SameStackRuntimeTopology.minio_bucket,
        ),
    )


def build_same_stack_environment(
    topology: SameStackRuntimeTopology | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    active = topology or resolve_same_stack_topology(environ)
    database_url = (
        "postgresql+psycopg://"
        f"{active.postgres_user}@{active.postgres_host}:"
        f"{active.postgres_port}/{active.postgres_database}"
    )
    return {
        "MDI_ENV": "local",
        "MDI_RUNTIME_PROFILE": "same-stack",
        "MDI_RUNTIME_BACKEND": "postgresql",
        "MDI_QUEUE_BACKEND": "redis",
        "MDI_ARTIFACT_BACKEND": "minio",
        "MDI_AGENT2_ORCHESTRATION_ENABLED": "true",
        "DATABASE_URL": database_url,
        "MDI_DATABASE_URL": database_url,
        "POSTGRES_HOST": active.postgres_host,
        "MDI_POSTGRES_HOST": active.postgres_host,
        "POSTGRES_PORT": str(active.postgres_port),
        "MDI_POSTGRES_PORT": str(active.postgres_port),
        "POSTGRES_DB": active.postgres_database,
        "MDI_POSTGRES_DB": active.postgres_database,
        "POSTGRES_USER": active.postgres_user,
        "MDI_POSTGRES_USER": active.postgres_user,
        "REDIS_URL": active.redis_url,
        "MDI_REDIS_URL": active.redis_url,
        "MINIO_ENDPOINT": active.minio_endpoint,
        "MDI_S3_ENDPOINT_URL": active.minio_endpoint,
        "MINIO_ACCESS_KEY": active.minio_access_key,
        "MINIO_SECRET_KEY": active.minio_secret_key,
        "MINIO_BUCKET": active.minio_bucket,
        "MDI_S3_BUCKET": active.minio_bucket,
    }


def apply_same_stack_environment(
    target: dict[str, str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    destination = target if target is not None else os.environ
    values = build_same_stack_environment(environ=environ)
    destination.update(values)
    return values


def _value(source: Mapping[str, str], name: str, default: str) -> str:
    value = str(source.get(name, "")).strip()
    return value or default


def _port(source: Mapping[str, str], name: str, default: int) -> int:
    raw = _value(source, name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name}_INVALID") from exc
    if not 1 <= value <= 65535:
        raise ValueError(f"{name}_INVALID")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit the canonical Phase 14-R same-stack runtime environment."
    )
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    values = build_same_stack_environment()
    print(
        json.dumps(
            values,
            ensure_ascii=False,
            indent=None if args.compact else 2,
            separators=(",", ":") if args.compact else None,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
