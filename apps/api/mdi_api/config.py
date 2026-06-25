from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ApiSettings:
    app_name: str = "Material Data Intelligence API"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://mdi@localhost:5432/mdi"
    redis_url: str = "redis://localhost:6379/0"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket: str = "mdi-artifacts"
    s3_region: str = "us-east-1"


def load_settings() -> ApiSettings:
    return ApiSettings(
        app_name=os.getenv("MDI_API_APP_NAME", ApiSettings.app_name),
        environment=os.getenv("MDI_ENV", ApiSettings.environment),
        database_url=os.getenv("MDI_DATABASE_URL", ApiSettings.database_url),
        redis_url=os.getenv("MDI_REDIS_URL", ApiSettings.redis_url),
        s3_endpoint_url=os.getenv("MDI_S3_ENDPOINT_URL", ApiSettings.s3_endpoint_url),
        s3_bucket=os.getenv("MDI_S3_BUCKET", ApiSettings.s3_bucket),
        s3_region=os.getenv("MDI_S3_REGION", ApiSettings.s3_region),
    )
