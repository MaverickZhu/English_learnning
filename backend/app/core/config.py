import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "English Learning API"
    app_version: str = "0.1.0"
    admin_token: str = os.getenv("ADMIN_TOKEN", "change-me")
    max_import_bytes: int = int(os.getenv("MAX_IMPORT_BYTES", "5242880"))
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    minio_public_endpoint: str = os.getenv("MINIO_PUBLIC_ENDPOINT", "localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_secure: bool = os.getenv("MINIO_SECURE", "false").lower() in {"1", "true", "yes"}
    minio_region: str = os.getenv("MINIO_REGION", "us-east-1")
    minio_image_bucket: str = os.getenv("MINIO_IMAGE_BUCKET", "images")
    minio_audio_bucket: str = os.getenv("MINIO_AUDIO_BUCKET", "audio")
    kimi_api_key: str = os.getenv("KIMI_API_KEY", "sk-G5SaV8HJQC6tIs7Q0Dcf6nDYR0Y0QEvgK5tqnh9carkqqE9r")
    kimi_base_url: str = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
    kimi_model: str = os.getenv("KIMI_MODEL", "kimi-k2.5")
    news_ingest_enabled: bool = os.getenv("NEWS_INGEST_ENABLED", "true").lower() in {"1", "true", "yes"}
    news_ingest_hour: int = int(os.getenv("NEWS_INGEST_HOUR", "2"))
    news_ingest_minute: int = int(os.getenv("NEWS_INGEST_MINUTE", "0"))


settings = Settings()
