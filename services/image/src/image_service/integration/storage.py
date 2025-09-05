from typing import BinaryIO, Optional
from urllib.parse import urlparse

import httpx
from minio import Minio
from minio.error import S3Error

from image_service.core.config import settings
from image_service.core.exceptions import StorageError


class ImageStorage:
    """Storage service for images using MinIO"""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        secure: bool = False,
    ):
        self.endpoint = endpoint or f"{settings.MINIO_HOST}:{settings.MINIO_PORT}"
        self.access_key = access_key or settings.MINIO_ACCESS_KEY
        self.secret_key = secret_key or settings.MINIO_SECRET_KEY
        self.bucket_name = settings.MINIO_BUCKET_NAME
        
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=secure,
        )
        
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()

    async def setup(self):
        """Ensure bucket exists"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise StorageError(f"Failed to setup storage: {str(e)}")

    async def store_from_url(self, url: str, object_name: str) -> str:
        """Download image from URL and store it"""
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            content = response.content
            
            # Store the image
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=content,
                length=len(content),
                content_type=response.headers.get("content-type", "image/jpeg"),
            )
            
            return self.get_url(object_name)
        except (httpx.HTTPError, S3Error) as e:
            raise StorageError(f"Failed to store image from URL: {str(e)}")

    async def store_from_bytes(
        self,
        data: bytes,
        object_name: str,
        content_type: str = "image/jpeg",
    ) -> str:
        """Store image from bytes"""
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data,
                length=len(data),
                content_type=content_type,
            )
            return self.get_url(object_name)
        except S3Error as e:
            raise StorageError(f"Failed to store image: {str(e)}")

    async def store_from_file(
        self,
        file: BinaryIO,
        object_name: str,
        content_type: str = "image/jpeg",
    ) -> str:
        """Store image from file object"""
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file,
                length=file.seek(0, 2),
                content_type=content_type,
            )
            file.seek(0)
            return self.get_url(object_name)
        except S3Error as e:
            raise StorageError(f"Failed to store image: {str(e)}")

    async def get(self, object_name: str) -> bytes:
        """Get image data"""
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
            )
            return response.read()
        except S3Error as e:
            raise StorageError(f"Failed to get image: {str(e)}")

    def get_url(self, object_name: str) -> str:
        """Get URL for stored object"""
        try:
            return self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=settings.MINIO_URL_EXPIRES,
            )
        except S3Error as e:
            raise StorageError(f"Failed to get image URL: {str(e)}")

    async def delete(self, object_name: str):
        """Delete image"""
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
            )
        except S3Error as e:
            raise StorageError(f"Failed to delete image: {str(e)}")

    async def copy(self, source_name: str, dest_name: str):
        """Copy image within storage"""
        try:
            self.client.copy_object(
                bucket_name=self.bucket_name,
                object_name=dest_name,
                source_object=f"{self.bucket_name}/{source_name}",
            )
        except S3Error as e:
            raise StorageError(f"Failed to copy image: {str(e)}")

    def get_object_name(self, url: str) -> str:
        """Extract object name from URL"""
        try:
            path = urlparse(url).path
            return path.split("/")[-1]
        except Exception as e:
            raise StorageError(f"Failed to parse URL: {str(e)}")

    async def exists(self, object_name: str) -> bool:
        """Check if image exists"""
        try:
            self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
            )
            return True
        except S3Error:
            return False
