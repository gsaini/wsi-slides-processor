import azure.functions as func
import logging
import os
import asyncio
from azure.storage.blob import BlobServiceClient
from azure.storage.blob.aio import BlobServiceClient as AioBlobServiceClient
import pyvips
import subprocess

app = func.FunctionApp()

@app.event_grid_trigger(arg_name="event")
async def blob_to_dzi_eventgrid_trigger(event: func.EventGridEvent):
    logger = logging.getLogger("blob_to_dzi_eventgrid_trigger")
    logger.info(f"Received Event: id={getattr(event, 'id', None)}, subject={getattr(event, 'subject', None)}")
    try:
        event_data = event.get_json()
        blob_url = event_data.get('url')
        logger.info(f"Parsed blob URL: {blob_url}")
    except Exception as e:
        logger.error(f"Error accessing event.get_json(): {e}")
        blob_url = None
    if not blob_url:
        logger.error('No blob URL found in event data.')
        return

    # Parse storage account, container, and blob name from URL
    from urllib.parse import urlparse
    parsed = urlparse(blob_url)
    path_parts = parsed.path.lstrip('/').split('/', 1)
    if len(path_parts) != 2:
        logger.error(f'Could not parse container and blob name from URL: {blob_url}')
        return
    container_name, blob_name = path_parts
    logger.info(f"Container: {container_name}, Blob: {blob_name}")

    # Get connection string from environment
    conn_str = os.environ.get('AzureWebJobsStorage')
    if not conn_str:
        logger.error('AzureWebJobsStorage not set in environment.')
        return

    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Download blob to temp file (streaming, suitable for very large files)
    import tempfile
    logger.info(f"Attempting to download from container: '{container_name}', blob: '{blob_name}' (streaming mode)")
    try:
        # Check if container exists
        container_client = blob_service_client.get_container_client(container_name)
        exists = await asyncio.to_thread(container_client.exists)
        if not exists:
            logger.error(f"Container '{container_name}' does not exist in the storage account.")
            return
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(blob_name)[1]) as temp_blob:
            logger.info(f"Streaming blob to temp file: {temp_blob.name}")
            download_stream = await asyncio.to_thread(blob_client.download_blob)
            # Stream the blob in chunks to avoid high memory usage
            chunk_size = 8 * 1024 * 1024  # 8 MB
            offset = 0
            while True:
                chunk = await asyncio.to_thread(download_stream.read, chunk_size)
                if not chunk:
                    break
                temp_blob.write(chunk)
                offset += len(chunk)
            temp_blob_path = temp_blob.name
            logger.info(f"Completed streaming blob to: {temp_blob_path}, total bytes: {offset}")
    except Exception as e:
        logger.error(f"Failed to download blob (streaming): {e}")
        return

    # Convert to DZI using pyvips
    try:
        dzi_output_dir = tempfile.mkdtemp()
        dzi_basename = os.path.splitext(os.path.basename(blob_name))[0]
        dzi_output_path = os.path.join(dzi_output_dir, dzi_basename)
        logger.info(f"Converting to DZI: {dzi_output_path}")
        image = await asyncio.to_thread(pyvips.Image.new_from_file, temp_blob_path, access='sequential')
        await asyncio.to_thread(
            image.dzsave,
            dzi_output_path,
            tile_size=512  # Recommended for OpenSeadragon, fewer files, good performance
        )
    except Exception as e:
        logger.error(f"DZI conversion failed: {e}")
        return

    # Upload DZI files and all subdirectory files to 'web-slides-dzi-output' in the same container using AzCopy
    def upload_with_azcopy(local_dir):
        sas_url = os.environ.get('DZI_UPLOAD_SAS_URL')
        if not sas_url:
            logger.error('DZI_UPLOAD_SAS_URL environment variable not set!')
            return
        cmd = [
            "azcopy", "copy",
            f"{local_dir}/*",
            sas_url,
            "--recursive=true"
        ]
        logger.info(f"AzCopy command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        logger.info(f"AzCopy stdout: {result.stdout}")
        logger.info(f"AzCopy stderr: {result.stderr}")
        logger.info(f"AzCopy returncode: {result.returncode}")
        logger.info(f"AzCopy result object: {result}")
        if result.returncode == 0:
            logger.info("AzCopy upload successful")
        else:
            logger.error(f"AzCopy failed with exit code {result.returncode}")

    upload_with_azcopy(dzi_output_dir)

    # If you want to skip the Python async upload, comment out the following block:
    # aio_blob_service_client = AioBlobServiceClient.from_connection_string(conn_str)
    # semaphore = asyncio.Semaphore(8)
    # async def upload_file(local_path, relative_path):
    #     async with semaphore:
    #         if original_blob_dir:
    #             dzi_blob_name = os.path.join(dzi_output_container_dir, original_blob_dir, relative_path)
    #         else:
    #             dzi_blob_name = os.path.join(dzi_output_container_dir, relative_path)
    #         try:
    #             async with aio_blob_service_client.get_blob_client(container=container_name, blob=dzi_blob_name) as blob_client:
    #                 with open(local_path, 'rb') as data:
    #                     await blob_client.upload_blob(data, overwrite=True)
    #             logger.info(f"Uploaded: {dzi_blob_name}")
    #         except Exception as e:
    #             logger.error(f"Failed to upload {dzi_blob_name}: {e}")

    # upload_tasks = []
    # for root, dirs, files in os.walk(dzi_output_dir):
    #     for file in files:
    #         local_file_path = os.path.join(root, file)
    #         rel_path = os.path.relpath(local_file_path, dzi_output_dir)
    #         upload_tasks.append(upload_file(local_file_path, rel_path))
    # await asyncio.gather(*upload_tasks)
    # await aio_blob_service_client.close()
    # logger.info(f'DZI conversion and upload complete for blob: {blob_name}')

    # Clean up temp files and directories
    import shutil
    try:
        if os.path.exists(temp_blob_path):
            os.remove(temp_blob_path)
            logger.info(f"Cleaned up temp file: {temp_blob_path}")
        if os.path.exists(dzi_output_dir):
            shutil.rmtree(dzi_output_dir)
            logger.info(f"Cleaned up temp directory: {dzi_output_dir}")
    except Exception as e:
        logger.warning(f"Failed to clean up temp files or directories: {e}")