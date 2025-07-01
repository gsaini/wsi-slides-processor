"""
parse_event_blob_url.py: Extracts the blob URL from an EventGridEvent.
"""
import logging
from typing import Optional

def parse_event_blob_url(event) -> Optional[str]:
    """
    Extracts the blob URL from an EventGridEvent.
    Args:
        event: The EventGridEvent object.
    Returns:
        The blob URL as a string, or None if not found.
    """
    logger = logging.getLogger("helpers.parse_event_blob_url")
    try:
        event_data = event.get_json()
        blob_url = event_data.get('url')
        logger.info("Parsed blob URL: %s", blob_url)
        return blob_url
    except (KeyError, AttributeError) as exc:
        logger.error("Error accessing event.get_json(): %s", exc)
        return None
