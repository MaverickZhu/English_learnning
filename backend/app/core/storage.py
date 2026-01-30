import io
import os
import uuid
from datetime import timedelta

from minio import Minio

from app.core.config import settings


def get_minio_client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
        region=settings.minio_region,
    )


def get_minio_public_client() -> Minio:
    return Minio(
        settings.minio_public_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
        region=settings.minio_region,
    )


def _bucket_for_kind(kind: str) -> str:
    if kind == "image":
        return settings.minio_image_bucket
    if kind == "audio":
        return settings.minio_audio_bucket
    raise ValueError("Unsupported media kind")


def ensure_buckets() -> None:
    client = get_minio_client()
    for bucket in (settings.minio_image_bucket, settings.minio_audio_bucket):
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)


def build_object_name(filename: str | None) -> str:
    ext = ""
    if filename:
        _, ext = os.path.splitext(filename)
    return f"{uuid.uuid4().hex}{ext}"


def upload_bytes(kind: str, data: bytes, content_type: str | None, filename: str | None) -> tuple[str, str]:
    bucket = _bucket_for_kind(kind)
    object_name = build_object_name(filename)
    client = get_minio_client()
    client.put_object(
        bucket,
        object_name,
        io.BytesIO(data),
        length=len(data),
        content_type=content_type or "application/octet-stream",
    )
    return bucket, object_name


def presign_get_url(kind: str, object_name: str, expires: timedelta | None = None) -> str:
    bucket = _bucket_for_kind(kind)
    client = get_minio_public_client()
    return client.presigned_get_object(bucket, object_name, expires=expires or timedelta(hours=1))
