"""
upload_with_azcopy.py: Uploads a directory's contents to Azure Blob Storage using AzCopy.

Performance Optimizations:
- Concurrency control via AZCOPY_CONCURRENCY_VALUE environment variable
- Block size optimization for DZI tile files
- Reduced logging overhead for large file sets (>50k files)
- Skip length checking for faster transfers
- Smart overwrite strategy for incremental uploads
"""
import subprocess
import logging
import os
import time

def upload_with_azcopy(local_dir: str, dest_url: str, logger: logging.Logger) -> bool:
    """
    Uploads all files and subdirectories from the specified local directory to the Azure Blob Storage destination
    using AzCopy with performance optimizations for large file sets (>50k files).
    
    Performance Features:
    - Configurable concurrency (default: 1000 for very large file sets)
    - Optimized block size (8MB for DZI tiles)
    - Minimal logging overhead (ERROR level)
    - Disabled length checking for speed
    - Efficient incremental uploads (ifSourceNewer)
    
    Environment Variables (optional):
    - AZCOPY_CONCURRENCY_VALUE: Number of concurrent operations (default: 1000)
    - AZCOPY_BUFFER_GB: Memory buffer in GB (default: 1)
    - AZCOPY_LOG_LEVEL: Logging verbosity (default: ERROR)
    
    Args:
        local_dir: The path to the local directory whose contents should be uploaded.
        dest_url: The destination Azure Blob Storage container or virtual directory URL.
        logger: Logger instance for logging.
        
    Returns:
        True if upload is successful, False otherwise.
    """
    # Set performance-optimized environment variables if not already set
    env = os.environ.copy()
    
    # Default to 1000 concurrent operations for very large file sets (100k+ files)
    # Optimized for server-to-server transfers in Azure Functions
    if 'AZCOPY_CONCURRENCY_VALUE' not in env:
        env['AZCOPY_CONCURRENCY_VALUE'] = '1000'
    
    # Set buffer size to 1GB if not specified
    if 'AZCOPY_BUFFER_GB' not in env:
        env['AZCOPY_BUFFER_GB'] = '1'
    
    # Build optimized AzCopy command
    cmd = [
        "azcopy", "copy",
        f"{local_dir}/*",
        dest_url,
        "--recursive=true",
        "--block-size-mb=8",           # Optimized for DZI tile files (typically 256KB-2MB)
        "--log-level=ERROR",            # Reduce logging overhead for large file sets
        "--check-length=false",         # Skip post-transfer verification for speed
        "--overwrite=ifSourceNewer",    # Efficient incremental uploads
        "--cap-mbps=0"                  # No bandwidth throttling
    ]
    
    logger.info(
        "AzCopy upload starting for %s with optimized settings (concurrency=%s, block-size=8MB)",
        local_dir,
        env.get('AZCOPY_CONCURRENCY_VALUE', 'default')
    )
    
    # Track upload performance
    start_time = time.time()
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    
    elapsed_time = time.time() - start_time
    
    # Log performance metrics
    logger.info("AzCopy upload completed in %.2f seconds", elapsed_time)
    logger.info("AzCopy stdout: %s", result.stdout)
    
    if result.stderr:
        logger.warning("AzCopy stderr: %s", result.stderr)
    
    logger.info("AzCopy returncode: %d", result.returncode)
    
    if result.returncode == 0:
        logger.info(
            "AzCopy upload successful for %s (%.2f seconds)",
            local_dir,
            elapsed_time
        )
        return True
    
    logger.error(
        "AzCopy failed with exit code %d for %s after %.2f seconds",
        result.returncode,
        local_dir,
        elapsed_time
    )
    return False
