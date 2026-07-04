from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ApiSettings:
    app_name: str = "Material Data Intelligence API"
    environment: str = "local"
    database_url: str = "sqlite:///./mdi_phase5.db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "mdi"
    postgres_user: str = "mdi"
    postgres_password: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket: str = "mdi-artifacts"
    s3_region: str = "us-east-1"
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str | None = None
    minio_secret_key: str | None = None
    minio_bucket: str = "mdi-artifacts"
    minio_secure: bool = False
    # -- Phase 5: runtime backend selection --
    runtime_backend: str = "local"  # "local" | "postgresql"
    queue_backend: str = "local"    # "local" | "redis"
    artifact_backend: str = "local"  # "local" | "minio"
    # -- Test database for integration tests --
    test_database_url: str | None = None
    # -- Browser access for local/demo web workspaces --
    cors_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )


def load_settings() -> ApiSettings:
    postgres_host = _env("POSTGRES_HOST", "MDI_POSTGRES_HOST", default=ApiSettings.postgres_host)
    postgres_port = int(_env("POSTGRES_PORT", "MDI_POSTGRES_PORT", default=str(ApiSettings.postgres_port)))
    postgres_db = _env("POSTGRES_DB", "MDI_POSTGRES_DB", default=ApiSettings.postgres_db)
    postgres_user = _env("POSTGRES_USER", "MDI_POSTGRES_USER", default=ApiSettings.postgres_user)
    postgres_password = _env("POSTGRES_PASSWORD", "MDI_POSTGRES_PASSWORD", default=None)

    # DATABASE_URL takes precedence; if PostgreSQL env vars are present but no
    # explicit URL, build one. Otherwise default to SQLite for local dev/tests.
    explicit_url = _env("DATABASE_URL", "MDI_DATABASE_URL", default=None)
    if explicit_url:
        database_url = explicit_url
    elif any(os.getenv(k) for k in ("POSTGRES_HOST", "MDI_POSTGRES_HOST")):
        database_url = _build_postgres_url(
            host=postgres_host,
            port=postgres_port,
            database=postgres_db,
            user=postgres_user,
            password=postgres_password,
        )
    else:
        database_url = ApiSettings.database_url

    test_database_url = os.getenv("MDI_TEST_DATABASE_URL") or None

    minio_endpoint = _env("MINIO_ENDPOINT", "MDI_S3_ENDPOINT_URL", default=ApiSettings.minio_endpoint)
    minio_bucket = _env("MINIO_BUCKET", "MDI_S3_BUCKET", default=ApiSettings.minio_bucket)
    return ApiSettings(
        app_name=os.getenv("MDI_API_APP_NAME", ApiSettings.app_name),
        environment=os.getenv("MDI_ENV", ApiSettings.environment),
        database_url=database_url,
        postgres_host=postgres_host,
        postgres_port=postgres_port,
        postgres_db=postgres_db,
        postgres_user=postgres_user,
        postgres_password=postgres_password,
        redis_url=_env("REDIS_URL", "MDI_REDIS_URL", default=ApiSettings.redis_url),
        s3_endpoint_url=_env("S3_ENDPOINT_URL", "MDI_S3_ENDPOINT_URL", "MINIO_ENDPOINT", default=ApiSettings.s3_endpoint_url),
        s3_bucket=_env("S3_BUCKET", "MDI_S3_BUCKET", "MINIO_BUCKET", default=ApiSettings.s3_bucket),
        s3_region=_env("S3_REGION", "MDI_S3_REGION", "AWS_REGION", default=ApiSettings.s3_region),
        minio_endpoint=minio_endpoint,
        minio_access_key=_env("MINIO_ACCESS_KEY", "MINIO_ROOT_USER", "AWS_ACCESS_KEY_ID", default=None),
        minio_secret_key=_env("MINIO_SECRET_KEY", "MINIO_ROOT_PASSWORD", "AWS_SECRET_ACCESS_KEY", default=None),
        minio_bucket=minio_bucket,
        minio_secure=_parse_bool(_env("MINIO_SECURE", "MDI_MINIO_SECURE", default="false")),
        runtime_backend=os.getenv("MDI_RUNTIME_BACKEND", "local").lower(),
        queue_backend=os.getenv("MDI_QUEUE_BACKEND", "local").lower(),
        artifact_backend=os.getenv("MDI_ARTIFACT_BACKEND", "local").lower(),
        test_database_url=test_database_url,
        cors_origins=_parse_csv(_env("MDI_CORS_ORIGINS", "CORS_ORIGINS", default=",".join(ApiSettings.cors_origins))),
    )


def _env(*names: str, default: str | None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    return default


def _build_postgres_url(*, host: str, port: int, database: str, user: str, password: str | None) -> str:
    credentials = user if not password else f"{user}:{password}"
    return f"postgresql+psycopg://{credentials}@{host}:{port}/{database}"


def _parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv(value: str | None) -> tuple[str, ...]:
    return tuple(item.strip() for item in str(value or "").split(",") if item.strip())
