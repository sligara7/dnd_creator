"""S3/MinIO storage client for binary asset management."""

import hashlib
import io
import logging
from typing import Optional, Dict, Any, List, BinaryIO
from datetime import datetime, timedelta
import aioboto3
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from tenacity import retry, stop_after_attempt, wait_exponential

from storage.core.config import settings


logger = logging.getLogger(__name__)


class S3StorageClient:
    """S3/MinIO storage client for managing binary assets."""

    def __init__(self):
        """Initialize S3 storage client."""
        self.endpoint_url = settings.s3_endpoint_url
        self.access_key_id = settings.s3_access_key_id
        self.secret_access_key = settings.s3_secret_access_key
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.s3_region
        self.use_ssl = settings.s3_use_ssl
        
        # Session for async operations
        self.session = aioboto3.Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region,
        )

    async def ensure_bucket_exists(self) -> bool:
        """Ensure the bucket exists, create if not."""
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl,
            ) as s3:
                # Check if bucket exists
                try:
                    await s3.head_bucket(Bucket=self.bucket_name)
                    logger.info(f"Bucket {self.bucket_name} exists")
                    return True
                except ClientError as e:
                    error_code = e.response["Error"]["Code"]
                    if error_code == "404":
                        # Create bucket
                        await s3.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={"LocationConstraint": self.region}
                            if self.region != "us-east-1"
                            else {},
                        )
                        logger.info(f"Created bucket {self.bucket_name}")
                        
                        # Set bucket versioning
                        await s3.put_bucket_versioning(
                            Bucket=self.bucket_name,
                            VersioningConfiguration={"Status": "Enabled"},
                        )
                        return True
                    else:
                        raise
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def upload_file(
        self,
        file_data: BinaryIO,
        object_key: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        storage_class: str = "STANDARD",
    ) -> Dict[str, Any]:
        """Upload a file to S3.
        
        Args:
            file_data: File data to upload
            object_key: S3 object key (path)
            content_type: MIME type of the file
            metadata: Optional metadata for the object
            storage_class: S3 storage class
            
        Returns:
            Upload result with version ID and ETag
        """
        try:
            # Calculate checksum
            file_data.seek(0)
            file_bytes = file_data.read()
            checksum = hashlib.sha256(file_bytes).hexdigest()
            file_data.seek(0)
            
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl,
            ) as s3:
                # Upload file
                response = await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=file_bytes,
                    ContentType=content_type,
                    Metadata=metadata or {},
                    StorageClass=storage_class,
                    ChecksumAlgorithm="SHA256",
                    ChecksumSHA256=checksum,
                )
                
                return {
                    "bucket": self.bucket_name,
                    "key": object_key,
                    "version_id": response.get("VersionId"),
                    "etag": response.get("ETag", "").strip('"'),
                    "checksum": checksum,
                    "size": len(file_bytes),
                }
        except Exception as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def download_file(
        self,
        object_key: str,
        version_id: Optional[str] = None,
    ) -> bytes:
        """Download a file from S3.
        
        Args:
            object_key: S3 object key
            version_id: Optional version ID for versioned objects
            
        Returns:
            File data as bytes
        """
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl,
            ) as s3:
                params = {"Bucket": self.bucket_name, "Key": object_key}
                if version_id:
                    params["VersionId"] = version_id
                    
                response = await s3.get_object(**params)
                return await response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.error(f"Object not found: {object_key}")
                return None
            logger.error(f"Error downloading file from S3: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def delete_file(
        self,
        object_key: str,
        version_id: Optional[str] = None,
    ) -> bool:
        """Delete a file from S3.
        
        Args:
            object_key: S3 object key
            version_id: Optional version ID for versioned objects
            
        Returns:
            True if successful
        """
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl,
            ) as s3:
                params = {"Bucket": self.bucket_name, "Key": object_key}
                if version_id:
                    params["VersionId"] = version_id
                    
                await s3.delete_object(**params)
                return True
        except Exception as e:
            logger.error(f"Error deleting file from S3: {e}")
            raise

    async def list_objects(
        self,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
    ) -> List[Dict[str, Any]]:
        """List objects in the bucket.
        
        Args:
            prefix: Optional prefix to filter objects
            max_keys: Maximum number of keys to return
            
        Returns:
            List of object metadata
        """
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl,
            ) as s3:
                params = {"Bucket": self.bucket_name, "MaxKeys": max_keys}
                if prefix:
                    params["Prefix"] = prefix
                    
                response = await s3.list_objects_v2(**params)
                
                objects = []
                for obj in response.get("Contents", []):
                    objects.append({
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "etag": obj["ETag"].strip('"'),
                        "storage_class": obj.get("StorageClass", "STANDARD"),
                    })
                    
                return objects
        except Exception as e:
            logger.error(f"Error listing objects from S3: {e}")
            raise

    async def get_object_metadata(
        self,
        object_key: str,
        version_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get object metadata.
        
        Args:
            object_key: S3 object key
            version_id: Optional version ID
            
        Returns:
            Object metadata or None if not found
        """
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl,
            ) as s3:
                params = {"Bucket": self.bucket_name, "Key": object_key}
                if version_id:
                    params["VersionId"] = version_id
                    
                response = await s3.head_object(**params)
                
                return {
                    "size": response["ContentLength"],
                    "content_type": response.get("ContentType"),
                    "last_modified": response["LastModified"],
                    "etag": response["ETag"].strip('"'),
                    "metadata": response.get("Metadata", {}),
                    "version_id": response.get("VersionId"),
                    "storage_class": response.get("StorageClass", "STANDARD"),
                }
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return None
            logger.error(f"Error getting object metadata: {e}")
            raise

    async def generate_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600,
        version_id: Optional[str] = None,
    ) -> str:
        """Generate a presigned URL for downloading.
        
        Args:
            object_key: S3 object key
            expiration: URL expiration time in seconds
            version_id: Optional version ID
            
        Returns:
            Presigned URL
        """
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl,
            ) as s3:
                params = {"Bucket": self.bucket_name, "Key": object_key}
                if version_id:
                    params["VersionId"] = version_id
                    
                url = await s3.generate_presigned_url(
                    "get_object",
                    Params=params,
                    ExpiresIn=expiration,
                )
                return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise

    async def copy_object(
        self,
        source_key: str,
        dest_key: str,
        source_version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Copy an object within S3.
        
        Args:
            source_key: Source object key
            dest_key: Destination object key
            source_version_id: Optional source version ID
            
        Returns:
            Copy result
        """
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl,
            ) as s3:
                copy_source = {"Bucket": self.bucket_name, "Key": source_key}
                if source_version_id:
                    copy_source["VersionId"] = source_version_id
                    
                response = await s3.copy_object(
                    CopySource=copy_source,
                    Bucket=self.bucket_name,
                    Key=dest_key,
                )
                
                return {
                    "version_id": response.get("VersionId"),
                    "etag": response.get("CopyObjectResult", {}).get("ETag", "").strip('"'),
                }
        except Exception as e:
            logger.error(f"Error copying object: {e}")
            raise

    async def set_lifecycle_policy(self, rules: List[Dict[str, Any]]) -> bool:
        """Set lifecycle policy for the bucket.
        
        Args:
            rules: List of lifecycle rules
            
        Returns:
            True if successful
        """
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl,
            ) as s3:
                await s3.put_bucket_lifecycle_configuration(
                    Bucket=self.bucket_name,
                    LifecycleConfiguration={"Rules": rules},
                )
                return True
        except Exception as e:
            logger.error(f"Error setting lifecycle policy: {e}")
            raise


# Global storage client instance
storage_client = S3StorageClient()
