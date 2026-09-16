from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Mapping

from mdi_schemas.worker_queues import (
    configured_worker_queue_names,
    worker_queue_definition,
)


RuntimeProfile = Literal["local", "same-stack"]
RuntimeBackend = Literal["local", "postgresql"]
QueueBackend = Literal["local", "redis"]
ArtifactBackend = Literal["local", "minio"]
DATABASE_CONFIGURATION_ENV_KEYS = (
    "DATABASE_URL",
    "MDI_DATABASE_URL",
    "POSTGRES_HOST",
    "MDI_POSTGRES_HOST",
)


class RuntimeConfigurationError(ValueError):
    """Raised before serving when a declared runtime topology is inconsistent."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = tuple(sorted(set(errors)))
        super().__init__("; ".join(self.errors))


@dataclass(frozen=True)
class ApiSettings:
    app_name: str = "Material Data Intelligence API"
    environment: str = "local"
    runtime_profile: RuntimeProfile = "local"
    # Resolve the development SQLite authority independently of process cwd.
    # Fresh API/worker processes may start from either the repo root or apps/api.
    database_url: str = f"sqlite:///{(Path(__file__).resolve().parents[3] / 'mdi_phase5.db').as_posix()}"
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
    runtime_backend: RuntimeBackend = "local"
    queue_backend: QueueBackend = "local"
    agent2_orchestration_enabled: bool = False
    agent2_queue_name: str = worker_queue_definition("orchestration").default_name
    agent2_planning_queue_name: str = worker_queue_definition("planning").default_name
    agent2_execution_queue_name: str = worker_queue_definition("execution").default_name
    agent2_result_projection_enabled: bool = True
    agent2_result_queue_name: str = worker_queue_definition("result_projection").default_name
    agent2_interpretation_enabled: bool = True
    agent2_interpretation_queue_name: str = worker_queue_definition("interpretation").default_name
    agent2_report_enabled: bool = True
    agent2_report_queue_name: str = worker_queue_definition("report").default_name
    # Re-publish only existing durable identities after an API/queue restart.
    # The recovery service excludes explicit qualification actors and never
    # creates a replacement scientific Result.
    agent2_startup_recovery_enabled: bool = True
    agent2_startup_recovery_stale_minutes: int = 15
    agent2_startup_recovery_limit: int = 50
    # Product resource governance. This is enforced against durable
    # ResearchTurn state before a new Turn is admitted; it is not a
    # process-local semaphore and therefore remains authoritative across API
    # and worker restarts.
    agent2_max_active_turns_per_project: int = 4
    # M1 durable Job lease. PostgreSQL time is authoritative; workers renew
    # every 30 seconds and lose publication authority after 90 seconds.
    job_execution_lease_seconds: int = 90
    job_execution_renewal_seconds: int = 30
    artifact_backend: ArtifactBackend = "local"
    artifact_root: str = str(Path(__file__).resolve().parents[3] / ".artifacts" / "phase2")
    # -- Test database for integration tests --
    test_database_url: str | None = None
    auth_required: bool = True
    auth_cookie_name: str = "mdi_session"
    auth_session_hours: int = 168
    # -- Browser access for local/demo web workspaces --
    cors_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3017",
        "http://127.0.0.1:3017",
        "http://localhost:3022",
        "http://127.0.0.1:3022",
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
    elif database_configuration_declared():
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
    settings = ApiSettings(
        app_name=os.getenv("MDI_API_APP_NAME", ApiSettings.app_name),
        environment=os.getenv("MDI_ENV", ApiSettings.environment),
        runtime_profile=_choice(
            "MDI_RUNTIME_PROFILE",
            os.getenv("MDI_RUNTIME_PROFILE", ApiSettings.runtime_profile),
            {"local", "same-stack"},
        ),
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
        runtime_backend=_choice(
            "MDI_RUNTIME_BACKEND",
            os.getenv("MDI_RUNTIME_BACKEND", "local"),
            {"local", "postgresql"},
        ),
        queue_backend=_choice(
            "MDI_QUEUE_BACKEND",
            os.getenv("MDI_QUEUE_BACKEND", "local"),
            {"local", "redis"},
        ),
        agent2_orchestration_enabled=_parse_bool(os.getenv("MDI_AGENT2_ORCHESTRATION_ENABLED", "false")),
        agent2_queue_name=os.getenv("MDI_AGENT2_QUEUE_NAME", ApiSettings.agent2_queue_name),
        agent2_planning_queue_name=os.getenv(
            "MDI_AGENT2_PLANNING_QUEUE_NAME",
            ApiSettings.agent2_planning_queue_name,
        ),
        agent2_execution_queue_name=os.getenv(
            "MDI_AGENT2_EXECUTION_QUEUE_NAME",
            ApiSettings.agent2_execution_queue_name,
        ),
        agent2_result_projection_enabled=_parse_bool(os.getenv("MDI_AGENT2_RESULT_PROJECTION_ENABLED", "true")),
        agent2_result_queue_name=os.getenv("MDI_AGENT2_RESULT_QUEUE_NAME", ApiSettings.agent2_result_queue_name),
        agent2_interpretation_enabled=_parse_bool(os.getenv("MDI_AGENT2_INTERPRETATION_ENABLED", "true")),
        agent2_interpretation_queue_name=os.getenv("MDI_AGENT2_INTERPRETATION_QUEUE_NAME", ApiSettings.agent2_interpretation_queue_name),
        agent2_report_enabled=_parse_bool(os.getenv("MDI_AGENT2_REPORT_ENABLED", "true")),
        agent2_report_queue_name=os.getenv("MDI_AGENT2_REPORT_QUEUE_NAME", ApiSettings.agent2_report_queue_name),
        agent2_startup_recovery_enabled=_parse_bool(
            os.getenv("MDI_AGENT2_STARTUP_RECOVERY_ENABLED", "true")
        ),
        agent2_startup_recovery_stale_minutes=max(
            1,
            int(
                os.getenv(
                    "MDI_AGENT2_STARTUP_RECOVERY_STALE_MINUTES",
                    str(ApiSettings.agent2_startup_recovery_stale_minutes),
                )
            ),
        ),
        agent2_startup_recovery_limit=max(
            1,
            int(
                os.getenv(
                    "MDI_AGENT2_STARTUP_RECOVERY_LIMIT",
                    str(ApiSettings.agent2_startup_recovery_limit),
                )
            ),
        ),
        agent2_max_active_turns_per_project=max(
            1,
            int(
                os.getenv(
                    "MDI_AGENT2_MAX_ACTIVE_TURNS_PER_PROJECT",
                    str(ApiSettings.agent2_max_active_turns_per_project),
                )
            ),
        ),
        job_execution_lease_seconds=max(
            3,
            int(
                os.getenv(
                    "MDI_JOB_EXECUTION_LEASE_SECONDS",
                    str(ApiSettings.job_execution_lease_seconds),
                )
            ),
        ),
        job_execution_renewal_seconds=max(
            1,
            int(
                os.getenv(
                    "MDI_JOB_EXECUTION_RENEWAL_SECONDS",
                    str(ApiSettings.job_execution_renewal_seconds),
                )
            ),
        ),
        artifact_backend=_choice(
            "MDI_ARTIFACT_BACKEND",
            os.getenv("MDI_ARTIFACT_BACKEND", "local"),
            {"local", "minio"},
        ),
        artifact_root=os.getenv("MDI_ARTIFACT_ROOT", ApiSettings.artifact_root),
        test_database_url=test_database_url,
        auth_required=_parse_bool(os.getenv("MDI_AUTH_REQUIRED", "true")),
        auth_cookie_name=os.getenv("MDI_AUTH_COOKIE_NAME", ApiSettings.auth_cookie_name),
        auth_session_hours=int(os.getenv("MDI_AUTH_SESSION_HOURS", str(ApiSettings.auth_session_hours))),
        cors_origins=_parse_csv(_env("MDI_CORS_ORIGINS", "CORS_ORIGINS", default=",".join(ApiSettings.cors_origins))),
    )
    validate_runtime_settings(settings)
    return settings


def database_configuration_declared(
    environ: Mapping[str, str] | None = None,
) -> bool:
    """Return whether a runtime explicitly selected a database authority."""

    source = environ if environ is not None else os.environ
    return any(source.get(key) for key in DATABASE_CONFIGURATION_ENV_KEYS)


def validate_runtime_settings(
    settings: ApiSettings,
    *,
    environ: Mapping[str, str] | None = None,
    process_role: Literal["api", "worker"] = "api",
    worker_redis_url: str | None = None,
    worker_queue_names: tuple[str, ...] = (),
) -> None:
    """Validate a declared same-stack topology before API/worker startup.

    Local and isolated test runtimes retain their explicit local defaults.
    A same-stack declaration is a qualification contract and therefore may
    not silently fall back to SQLite, an implicit Redis URL, local Artifacts,
    or a worker connected to another Redis namespace.
    """

    if settings.runtime_profile != "same-stack":
        return
    source = environ if environ is not None else os.environ
    errors: list[str] = []

    _conflicting_aliases(
        source,
        ("DATABASE_URL", "MDI_DATABASE_URL"),
        "DATABASE_URL_CONFLICT",
        errors,
    )
    for names, error in (
        (("POSTGRES_HOST", "MDI_POSTGRES_HOST"), "POSTGRES_HOST_CONFLICT"),
        (("POSTGRES_PORT", "MDI_POSTGRES_PORT"), "POSTGRES_PORT_CONFLICT"),
        (("POSTGRES_DB", "MDI_POSTGRES_DB"), "POSTGRES_DB_CONFLICT"),
        (("POSTGRES_USER", "MDI_POSTGRES_USER"), "POSTGRES_USER_CONFLICT"),
        (
            ("POSTGRES_PASSWORD", "MDI_POSTGRES_PASSWORD"),
            "POSTGRES_PASSWORD_CONFLICT",
        ),
    ):
        _conflicting_aliases(source, names, error, errors)
    _conflicting_aliases(
        source,
        ("REDIS_URL", "MDI_REDIS_URL"),
        "REDIS_URL_CONFLICT",
        errors,
    )
    _conflicting_aliases(
        source,
        ("MINIO_ENDPOINT", "MDI_S3_ENDPOINT_URL", "S3_ENDPOINT_URL"),
        "MINIO_ENDPOINT_CONFLICT",
        errors,
    )
    _conflicting_aliases(
        source,
        ("MINIO_BUCKET", "MDI_S3_BUCKET", "S3_BUCKET"),
        "MINIO_BUCKET_CONFLICT",
        errors,
    )
    _conflicting_aliases(
        source,
        ("MINIO_ACCESS_KEY", "MINIO_ROOT_USER", "AWS_ACCESS_KEY_ID"),
        "MINIO_ACCESS_KEY_CONFLICT",
        errors,
    )
    _conflicting_aliases(
        source,
        ("MINIO_SECRET_KEY", "MINIO_ROOT_PASSWORD", "AWS_SECRET_ACCESS_KEY"),
        "MINIO_SECRET_KEY_CONFLICT",
        errors,
    )

    database_explicit = any(
        source.get(name)
        for name in (
            "DATABASE_URL",
            "MDI_DATABASE_URL",
            "POSTGRES_HOST",
            "MDI_POSTGRES_HOST",
        )
    )
    if not database_explicit:
        errors.append("SAME_STACK_POSTGRES_CONFIGURATION_REQUIRED")
    if settings.runtime_backend != "postgresql":
        errors.append("SAME_STACK_RUNTIME_BACKEND_MUST_BE_POSTGRESQL")
    if not settings.database_url.lower().startswith(
        ("postgresql://", "postgresql+psycopg://")
    ):
        errors.append("SAME_STACK_DATABASE_URL_MUST_BE_POSTGRESQL")

    redis_explicit = any(source.get(name) for name in ("REDIS_URL", "MDI_REDIS_URL"))
    if not redis_explicit:
        errors.append("SAME_STACK_REDIS_URL_REQUIRED")
    if settings.queue_backend != "redis":
        errors.append("SAME_STACK_QUEUE_BACKEND_MUST_BE_REDIS")
    if not settings.redis_url.lower().startswith(("redis://", "rediss://")):
        errors.append("SAME_STACK_REDIS_URL_INVALID")

    if settings.artifact_backend != "minio":
        errors.append("SAME_STACK_ARTIFACT_BACKEND_MUST_BE_MINIO")
    if not settings.minio_endpoint.lower().startswith(("http://", "https://")):
        errors.append("SAME_STACK_MINIO_ENDPOINT_INVALID")
    if not any(
        source.get(name)
        for name in ("MINIO_ENDPOINT", "MDI_S3_ENDPOINT_URL", "S3_ENDPOINT_URL")
    ):
        errors.append("SAME_STACK_MINIO_ENDPOINT_REQUIRED")
    if not settings.minio_access_key:
        errors.append("SAME_STACK_MINIO_ACCESS_KEY_REQUIRED")
    if not settings.minio_secret_key:
        errors.append("SAME_STACK_MINIO_SECRET_KEY_REQUIRED")
    if not any(
        source.get(name) for name in ("MINIO_BUCKET", "MDI_S3_BUCKET", "S3_BUCKET")
    ) or not settings.minio_bucket:
        errors.append("SAME_STACK_MINIO_BUCKET_REQUIRED")
    if settings.minio_secure and settings.minio_endpoint.lower().startswith("http://"):
        errors.append("SAME_STACK_MINIO_SECURE_ENDPOINT_CONFLICT")

    if not settings.agent2_orchestration_enabled:
        errors.append("SAME_STACK_AGENT2_ORCHESTRATION_REQUIRED")

    configured_queue_names = configured_worker_queue_names(settings)
    if any(not name for name in configured_queue_names):
        errors.append("SAME_STACK_WORKER_QUEUE_REQUIRED")
    if len(set(configured_queue_names)) != len(configured_queue_names):
        errors.append("SAME_STACK_WORKER_QUEUE_NAMES_MUST_BE_UNIQUE")

    if process_role == "worker":
        if not worker_queue_names or any(not item.strip() for item in worker_queue_names):
            errors.append("SAME_STACK_WORKER_QUEUE_REQUIRED")
        elif any(item not in configured_queue_names for item in worker_queue_names):
            errors.append("SAME_STACK_WORKER_QUEUE_NOT_IN_MANIFEST")
        if worker_redis_url is None:
            errors.append("SAME_STACK_WORKER_REDIS_URL_REQUIRED")
        elif worker_redis_url.rstrip("/") != settings.redis_url.rstrip("/"):
            errors.append("SAME_STACK_WORKER_REDIS_URL_CONFLICT")

    if errors:
        raise RuntimeConfigurationError(errors)


def _env(*names: str, default: str | None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    return default


def _choice(name: str, value: str, allowed: set[str]) -> str:
    normalized = str(value).strip().lower()
    if normalized not in allowed:
        raise RuntimeConfigurationError([f"{name}_INVALID"])
    return normalized


def _conflicting_aliases(
    environ: Mapping[str, str],
    names: tuple[str, ...],
    error: str,
    errors: list[str],
) -> None:
    values = {
        str(environ[name]).strip().rstrip("/")
        for name in names
        if environ.get(name) not in (None, "")
    }
    if len(values) > 1:
        errors.append(error)


def _build_postgres_url(*, host: str, port: int, database: str, user: str, password: str | None) -> str:
    credentials = user if not password else f"{user}:{password}"
    return f"postgresql+psycopg://{credentials}@{host}:{port}/{database}"


def _parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv(value: str | None) -> tuple[str, ...]:
    return tuple(item.strip() for item in str(value or "").split(",") if item.strip())
