"""
convert_to_dzi.py: Converts an image file to Deep Zoom Image (DZI) format using pyvips.
"""
import tempfile
import os
import logging
from typing import Optional
import pyvips

def convert_to_dzi(input_path: str, blob_name: str) -> Optional[str]:
    """
    Converts an image file to Deep Zoom Image (DZI) format using pyvips.
    Args:
        input_path: Path to the input image file.
        blob_name: The original blob name (used for output naming).
    Returns:
        The path to the DZI output directory, or None if conversion fails.
    """
    logger = logging.getLogger("helpers.convert_to_dzi")
    try:
        dzi_output_dir = tempfile.mkdtemp()
        dzi_basename = os.path.splitext(os.path.basename(blob_name))[0]
        dzi_output_path = os.path.join(dzi_output_dir, dzi_basename)
        logger.info("Converting to DZI: %s", dzi_output_path)
        image = pyvips.Image.new_from_file(input_path, access='sequential')
        image.dzsave(dzi_output_path, tile_size=512)
        return dzi_output_dir
    except (pyvips.Error, OSError) as exc:
        logger.error("DZI conversion failed: %s", exc)
        return None
