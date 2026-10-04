import asyncio
import io
import uuid
from pathlib import Path

from minio import Minio
from src.app.core.config import settings


class ObjectStorage:
    def __init__(self) -> None:
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
            region=settings.MINIO_REGION,
        )
        self.bucket = settings.MINIO_BUCKET

    def _ensure_bucket_sync(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    async def ensure_bucket(self) -> None:
        await asyncio.to_thread(self._ensure_bucket_sync)

    async def upload(
        self,
        data: bytes,
        filename: str,
        content_type: str,
        prefix: str = "tasks",
    ) -> str:
        await self.ensure_bucket()
        suffix = Path(filename).suffix.lower()
        object_name = f"{prefix}/{uuid.uuid4()}{suffix}"
        await asyncio.to_thread(
            self.client.put_object,
            self.bucket,
            object_name,
            io.BytesIO(data),
            len(data),
            content_type,
        )
        return object_name

    def _download_sync(self, object_name: str) -> tuple[bytes, str]:
        response = self.client.get_object(self.bucket, object_name)
        try:
            return response.read(), response.headers.get("Content-Type", "application/octet-stream")
        finally:
            response.close()
            response.release_conn()

    async def download(self, object_name: str) -> tuple[bytes, str]:
        await self.ensure_bucket()
        return await asyncio.to_thread(self._download_sync, object_name)


object_storage = ObjectStorage()
