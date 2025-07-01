"""
cleanup_temp_files.py: Removes temporary files and directories.
"""
import os
import shutil
import logging

def cleanup_temp_files(*paths):
    """
    Removes temporary files and directories.
    Args:
        *paths: Paths to files or directories to remove.
    """
    logger = logging.getLogger("helpers.cleanup_temp_files")
    for path in paths:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                logger.info("Cleaned up temp directory: %s", path)
            elif os.path.isfile(path):
                os.remove(path)
                logger.info("Cleaned up temp file: %s", path)
        except (OSError, shutil.Error) as exc:
            logger.warning("Failed to clean up %s: %s", path, exc)
