"""
parse_container_and_blob.py: Parses the container and blob name from a blob URL.
"""
from typing import Optional, Tuple
import logging
from urllib.parse import urlparse

def parse_container_and_blob(blob_url: str) -> Optional[Tuple[str, str]]:
    """
    Parses the container and blob name from a blob URL.
    Args:
        blob_url: The full blob URL.
    Returns:
        (container_name, blob_name) tuple, or None if parsing fails.
    """
    logger = logging.getLogger("helpers.parse_container_and_blob")
    parsed = urlparse(blob_url)
    path_parts = parsed.path.lstrip('/').split('/', 1)
    if len(path_parts) != 2:
        logger.error(
            "Could not parse container and blob name from URL: %s", blob_url
        )
        return None
    return path_parts[0], path_parts[1]
