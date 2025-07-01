"""
download_blob_to_temp.py: Downloads a blob to a temporary file using streaming.
"""
import tempfile
import os
import logging
from typing import Optional
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError

def download_blob_to_temp(blob_service_client: BlobServiceClient, container_name: str, blob_name: str) -> Optional[str]:
    """
    Downloads a blob to a temporary file using streaming (suitable for large files).
    Args:
        blob_service_client: The BlobServiceClient instance.
        container_name: The name of the container.
        blob_name: The name of the blob.
    Returns:
        The path to the temporary file, or None if download fails.
    """
    logger = logging.getLogger("helpers.download_blob_to_temp")
    try:
        container_client = blob_service_client.get_container_client(container_name)
        exists = container_client.exists()
        if not exists:
            logger.error(
                "Container '%s' does not exist in the storage account.", container_name
            )
            return None
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(blob_name)[1]) as temp_blob:
            logger.info("Streaming blob to temp file: %s", temp_blob.name)
            download_stream = blob_client.download_blob()
            chunk_size = 8 * 1024 * 1024  # 8 MB
            offset = 0
            while True:
                chunk = download_stream.read(chunk_size)
                if not chunk:
                    break
                temp_blob.write(chunk)
                offset += len(chunk)
            logger.info(
                "Completed streaming blob to: %s, total bytes: %d", temp_blob.name, offset
            )
            return temp_blob.name
    except (OSError, AzureError) as exc:
        logger.error("Failed to download blob (streaming): %s", exc)
        return None
