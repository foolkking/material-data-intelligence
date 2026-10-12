"""First-run helpers for dev.ps1; never loads an env file during tests/imports."""
from __future__ import annotations

import argparse
import base64
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]


def initialize(local_root: Path) -> Path:
    local_root = local_root.resolve()
    if local_root.is_relative_to(REPO):
        raise ValueError("MDI_LOCAL_ROOT must be outside the repository")
    local_root.mkdir(parents=True, exist_ok=True)
    target = local_root / "local.env"
    # Exclusive creation: rerunning init never rotates credentials.
    if target.exists():
        return target
    template = (REPO / ".env.example").read_text(encoding="utf-8")
    path_values = {
        "MDI_LOCAL_ROOT": local_root,
        "MDI_DATA_ROOT": local_root / "data",
        "MDI_RUNTIME_ROOT": local_root / "run",
        "MDI_LOG_ROOT": local_root / "logs",
        "MDI_TEMP_ROOT": local_root / "tmp",
        "MDI_CACHE_ROOT": local_root / "cache",
        "MDI_NEXT_DIST_DIR": local_root / "cache" / "next",
        "MDI_ARTIFACT_ROOT": local_root / "data" / "artifacts",
    }
    replacements = {
        **{key: value.as_posix() for key, value in path_values.items()},
        "POSTGRES_PASSWORD": secrets.token_urlsafe(32),
        "MINIO_SECRET_KEY": secrets.token_urlsafe(32),
        "MDI_LOCAL_USER_PASSWORD": secrets.token_urlsafe(24),
        "MDI_PROVIDER_ENCRYPTION_KEY": base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
    }
    lines = []
    for line in template.splitlines():
        key = line.partition("=")[0]
        lines.append(f"{key}={replacements[key]}" if key in replacements else line)
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(lines) + "\n")
    return target


def checked_settings():
    from cryptography.fernet import Fernet
    from sqlalchemy.engine import make_url
    from mdi_api.config import load_settings

    settings = load_settings()
    if (settings.runtime_profile, settings.runtime_backend, settings.queue_backend,
            settings.artifact_backend) != ("same-stack", "postgresql", "redis", "minio"):
        raise ValueError("dev.ps1 requires same-stack PostgreSQL / Redis / MinIO")
    required = ("POSTGRES_PASSWORD", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY",
                "MDI_PROVIDER_ENCRYPTION_KEY", "MDI_LOCAL_USER_EMAIL", "MDI_LOCAL_USER_PASSWORD")
    for key in required:
        value = os.environ.get(key, "")
        if not value or "CHANGE_ME" in value:
            raise ValueError(f"Set {key} in the external local.env")
    if len(os.environ["MDI_LOCAL_USER_PASSWORD"]) < 12:
        raise ValueError("MDI_LOCAL_USER_PASSWORD must contain at least 12 characters")
    if len(os.environ["MINIO_SECRET_KEY"]) < 8:
        raise ValueError("MINIO_SECRET_KEY must contain at least 8 characters")
    try:
        Fernet(os.environ["MDI_PROVIDER_ENCRYPTION_KEY"].encode())
    except (ValueError, TypeError):
        raise ValueError("MDI_PROVIDER_ENCRYPTION_KEY must be a valid Fernet key") from None
    url = make_url(settings.database_url)
    if (url.host, url.port or 5432, url.database, url.username, url.password) != (
        settings.postgres_host, settings.postgres_port, settings.postgres_db,
        settings.postgres_user, settings.postgres_password
    ):
        raise ValueError("DATABASE_URL / MDI_DATABASE_URL must agree with POSTGRES_*; remove redundant URLs")
    if settings.postgres_host not in ("127.0.0.1", "localhost"):
        raise ValueError("dev.ps1 manages loopback services only")
    if not settings.auth_required:
        raise ValueError("dev.ps1 requires MDI_AUTH_REQUIRED=true")
    return settings


def initialize_cluster(pg_bin: Path) -> None:
    settings = checked_settings()
    data = Path(os.environ["MDI_DATA_ROOT"]) / "postgres"
    if (data / "PG_VERSION").exists():
        return
    if data.exists() and any(data.iterdir()):
        raise ValueError("PostgreSQL directory is not empty and has no PG_VERSION; leaving it untouched")
    temporary = Path(os.environ["MDI_TEMP_ROOT"])
    temporary.mkdir(parents=True, exist_ok=True)
    descriptor, password_file = tempfile.mkstemp(prefix="mdi-initdb-", dir=temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(settings.postgres_password + "\n")
        result = subprocess.run([
            str(pg_bin / "initdb.exe"), "-D", str(data), "-U", settings.postgres_user,
            "--encoding=UTF8", "--locale=C", "--auth=scram-sha-256", f"--pwfile={password_file}",
        ], check=False)
        if result.returncode:
            raise ValueError("initdb failed; see its diagnostic above")
    finally:
        Path(password_file).unlink(missing_ok=True)


def alembic_config(settings):
    from alembic.config import Config
    config = Config(str(REPO / "apps/api/alembic.ini"))
    config.set_main_option("script_location", str(REPO / "apps/api/alembic"))
    config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
    return config


def prepare_database() -> None:
    import psycopg
    from psycopg import sql
    from alembic import command
    settings = checked_settings()
    with psycopg.connect(host=settings.postgres_host, port=settings.postgres_port,
            user=settings.postgres_user, password=settings.postgres_password,
            dbname="postgres", autocommit=True, connect_timeout=5) as conn:
        exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.postgres_db,)).fetchone()
        if not exists:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(settings.postgres_db)))
    command.upgrade(alembic_config(settings), "head")
    print("Database is at the current Alembic head.")


def check_database() -> None:
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory
    from sqlalchemy import create_engine
    settings = checked_settings()
    expected = set(ScriptDirectory.from_config(alembic_config(settings)).get_heads())
    engine = create_engine(settings.database_url)
    try:
        with engine.connect() as conn:
            current = set(MigrationContext.configure(conn).get_current_heads())
        if current != expected:
            raise ValueError("Database needs migration: stop the stack, run dev.ps1 migrate, then start")
    finally:
        engine.dispose()
    print("Database migration head verified.")


def prepare_bucket(*, create: bool) -> None:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
    settings = checked_settings()
    client = boto3.client("s3", endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_access_key, aws_secret_access_key=settings.minio_secret_key,
        region_name=settings.s3_region, config=Config(connect_timeout=5, read_timeout=5))
    try:
        client.head_bucket(Bucket=settings.minio_bucket)
    except ClientError as error:
        if not create or error.response["Error"]["Code"] not in ("404", "NoSuchBucket", "NotFound"):
            raise ValueError("MinIO bucket is unavailable; check local.env and run dev.ps1 migrate") from None
        client.create_bucket(Bucket=settings.minio_bucket)
    finally:
        client.close()
    print("MinIO bucket ready.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("init", "check", "cluster", "database", "bucket", "ready"))
    parser.add_argument("--local-root", type=Path)
    parser.add_argument("--pg-bin", type=Path)
    args = parser.parse_args()
    try:
        if args.action == "init":
            path = initialize(args.local_root or REPO.with_name(REPO.name + ".local"))
            print(f"Configuration ready: {path}\nExisting credentials are preserved. Read this file for first-login credentials.")
        elif args.action == "check":
            checked_settings()
            print("Runtime configuration and encryption key verified (values hidden).")
        elif args.action == "cluster":
            if args.pg_bin is None:
                raise ValueError("--pg-bin is required")
            initialize_cluster(args.pg_bin)
        elif args.action == "database":
            prepare_database()
        elif args.action == "bucket":
            prepare_bucket(create=True)
        else:
            check_database()
            prepare_bucket(create=False)
    except ValueError as error:
        print(f"Setup: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        # Driver exceptions can contain credential-bearing URLs or DSNs.
        print(f"Setup failed ({type(error).__name__}); check service logs and local.env. No credentials printed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
