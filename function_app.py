"""
function_app.py: Azure Function entrypoint for WSI to DZI processing.
"""

import asyncio
import logging
import os

import azure.functions as func
from azure.storage.blob import BlobServiceClient

from cleanup_temp_files import cleanup_temp_files
from convert_to_dzi import convert_to_dzi
from download_blob_to_temp import download_blob_to_temp
from parse_container_and_blob import parse_container_and_blob
from parse_event_blob_url import parse_event_blob_url
from upload_with_azcopy import upload_with_azcopy

app = func.FunctionApp()


@app.event_grid_trigger(arg_name="event")
async def blob_to_dzi_eventgrid_trigger(event: func.EventGridEvent):
    """
    Azure Function entrypoint for processing blob events:
    - Parses the event for the blob URL
    - Downloads the blob to a temp file
    - Converts the blob to DZI format
    - Uploads the DZI output to Azure Blob Storage using AzCopy
    - Cleans up temp files and directories
    """
    logger = logging.getLogger("blob_to_dzi_eventgrid_trigger")
    logger.info(
        "Received Event: id=%s, subject=%s",
        getattr(event, "id", None),
        getattr(event, "subject", None),
    )

    blob_url = parse_event_blob_url(event)
    if not blob_url:
        logger.error("No blob URL found in event data.")
        return

    parsed = parse_container_and_blob(blob_url)
    if not parsed:
        return
    container_name, blob_name = parsed
    logger.info("Container: %s, Blob: %s", container_name, blob_name)

    conn_str = os.environ.get("AzureWebJobsStorage")
    if not conn_str:
        logger.error("AzureWebJobsStorage not set in environment.")
        return

    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    try:
        temp_blob_path = await asyncio.to_thread(
            download_blob_to_temp, blob_service_client, container_name, blob_name
        )
        if not temp_blob_path:
            logger.error("Failed to download blob to temp file: %s/%s", container_name, blob_name)
            return
    except Exception as exc:
        logger.error("Exception during blob download: %s", exc, exc_info=True)
        return

    try:
        dzi_output_dir = await asyncio.to_thread(convert_to_dzi, temp_blob_path, blob_name)
        if not dzi_output_dir:
            logger.error("DZI conversion failed for blob: %s", blob_name)
            return
    except Exception as exc:
        logger.error("Exception during DZI conversion: %s", exc, exc_info=True)
        return

    dest_url = os.environ.get("DZI_UPLOAD_DEST_URL")
    if not dest_url:
        logger.error("DZI_UPLOAD_DEST_URL environment variable not set!")
        cleanup_temp_files(temp_blob_path, dzi_output_dir)
        return
    upload_with_azcopy(dzi_output_dir, dest_url, logger)
    cleanup_temp_files(temp_blob_path, dzi_output_dir)
