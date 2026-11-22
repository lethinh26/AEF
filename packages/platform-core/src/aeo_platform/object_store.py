import asyncio
from functools import lru_cache
from pathlib import PurePosixPath

import boto3
from botocore.config import Config

from aeo_platform.config import get_settings


def validate_object_key(key: str) -> str:
    path = PurePosixPath(key)
    if not key or path.is_absolute() or ".." in path.parts or "\\" in key:
        raise ValueError("Object key must be a non-empty relative path without traversal")
    return key


@lru_cache
def get_s3_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name="us-east-1",
        config=Config(signature_version="s3v4", retries={"max_attempts": 3, "mode": "standard"}),
    )


class ArtifactStore:
    """S3-compatible artifact storage; metadata and digests live in PostgreSQL."""

    def __init__(self, bucket: str | None = None) -> None:
        self.bucket = bucket or get_settings().s3_bucket

    async def put_bytes(
        self,
        key: str,
        body: bytes,
        *,
        content_type: str,
        sha256: str,
    ) -> str:
        safe_key = validate_object_key(key)
        await asyncio.to_thread(
            get_s3_client().put_object,
            Bucket=self.bucket,
            Key=safe_key,
            Body=body,
            ContentType=content_type,
            Metadata={"sha256": sha256},
        )
        return safe_key

    async def get_bytes(self, key: str) -> bytes:
        safe_key = validate_object_key(key)

        def download() -> bytes:
            response = get_s3_client().get_object(Bucket=self.bucket, Key=safe_key)
            return response["Body"].read()

        return await asyncio.to_thread(download)
