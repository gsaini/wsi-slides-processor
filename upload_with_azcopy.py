"""
upload_with_azcopy.py: Uploads a directory's contents to Azure Blob Storage using AzCopy.
"""
import subprocess
import logging

def upload_with_azcopy(local_dir: str, dest_url: str, logger: logging.Logger) -> bool:
    """
    Uploads all files and subdirectories from the specified local directory to the Azure Blob Storage destination
    using AzCopy. The upload is recursive and logs the command, output, and result for troubleshooting.
    Args:
        local_dir: The path to the local directory whose contents should be uploaded.
        dest_url: The destination Azure Blob Storage container or virtual directory URL.
        logger: Logger instance for logging.
    Returns:
        True if upload is successful, False otherwise.
    """
    cmd = [
        "azcopy", "copy",
        f"{local_dir}/*",
        dest_url,
        "--recursive=true"
    ]
    logger.info(
        "AzCopy command: azcopy copy %s %s --recursive=true", cmd[2], dest_url
    )
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    logger.info("AzCopy stdout: %s", result.stdout)
    logger.info("AzCopy stderr: %s", result.stderr)
    logger.info("AzCopy returncode: %d", result.returncode)
    if result.returncode == 0:
        logger.info("AzCopy upload successful for %s", cmd[2])
        return True
    logger.error(
        "AzCopy failed with exit code %d for %s", result.returncode, cmd[2]
    )
    return False
