# wsi-slides-dzi-processor Azure Function

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)


## Overview

This Azure Function automatically processes Whole Slide Images (WSI) uploaded to Azure Blob Storage, converting them into Deep Zoom Image (DZI) format using `pyvips`. It is designed to handle very large files (up to several GB) efficiently and is suitable for digital pathology, microscopy, and similar domains.

- **Trigger:** Event Grid (on blob upload)
- **Input:** Image blob (e.g., `.jpg`, `.tif`) in a monitored container
- **Output:** DZI tiles and metadata uploaded to a designated output container
- **Tech Stack:** Python, Azure Functions, Azure Blob Storage, pyvips

> **Note:**
> This function is built and deployed using Docker because the `libvips` library (required by `pyvips`) is not supported on standard Azure Functions hosting options such as Flex Consumption, Consumption, or App Service plans. Docker allows you to include all necessary native dependencies for reliable execution on the Premium plan or in a custom container environment.

## Features
- Event-driven, serverless image processing
- Streams large blobs to disk to minimize memory usage
- Converts images to DZI format for web-based deep zoom viewing
- Robust error handling and logging
- Dockerized for easy deployment

## Folder Structure
```
├── Dockerfile
├── function_app.py
├── host.json
├── local.settings.json
├── requirements.txt
└── README.md
```

## How It Works
1. **Trigger:**
   - The function is triggered by an Event Grid event when a new blob is uploaded.
2. **Blob Download:**
   - The function parses the event, streams the blob to a temporary file (efficient for files >4GB).
3. **DZI Conversion:**
   - Uses `pyvips` to convert the image to DZI format.
4. **Upload Output:**
   - Uploads all DZI output files to the `web-slides-dzi-output` directory in the same container.
5. **Cleanup:**
   - Temporary files are deleted after processing.

## Setup & Deployment

### Prerequisites
- Azure Subscription
- Azure Storage Account with Event Grid enabled
- Docker (for local build/test)
- Python 3.12 (for local development)

### Local Development
1. Clone the repo and navigate to the project directory.
2. Set up a Python virtual environment (optional but recommended):
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure `local.settings.json` with your Azure Storage connection string.
4. Run locally with the Azure Functions Core Tools:
   ```sh
   func start
   ```

### Docker Build & Deploy
1. Build the Docker image:
   ```sh
   docker build -t <your-image-name> .
   ```
2. Run locally:
   ```sh
   docker run -p 8080:80 -e AzureWebJobsStorage='<your-connection-string>' <your-image-name>
   ```
3. Push to a container registry and deploy to Azure Functions Premium Plan.

### Azure Deployment
- Deploy using Azure Portal, Azure CLI, or GitHub Actions.
- Ensure the function app has access to the storage account (use Managed Identity for production).

## Configuration
- `AzureWebJobsStorage`: Connection string for Azure Blob Storage (set in environment or `local.settings.json`).
- Event Grid subscription must be configured to send blob creation events to this function.

## Requirements
See `requirements.txt`:
- azure-functions
- azure-storage-blob
- pyvips

## Security & Best Practices
- Use Managed Identity for production deployments (avoid connection strings when possible).
- Monitor logs and set up alerts for failures.
- Clean up temp files to avoid storage leaks.
- For very large files or long processing, consider Azure Durable Functions.

## References
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [pyvips Documentation](https://libvips.github.io/pyvips/)
- [Deep Zoom Image Format](https://learn.microsoft.com/en-us/previous-versions/iiif/deep-zoom-image/dzi-file-format)

---

*This project is maintained by [gsaini](https://github.com/gsaini).*

## Local Validation Guide

This guide explains how to validate the `blob_to_dzi_eventgrid_trigger` Azure Function locally.

### Prerequisites
- Azure Functions Core Tools v4+
- Python 3.12
- Docker (optional, for container-based validation)
- [Azurite](https://learn.microsoft.com/azure/storage/common/storage-use-azurite?tabs=visual-studio) (optional, for local storage emulation)
- All Python dependencies installed: `pip install -r requirements.txt`

### 1. Configure Local Settings
Edit or create `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true"
  }
}
```
- Use your real Azure Storage connection string if you want to test against a real account.

### 2. Start the Function Locally
#### Option A: Python Environment
```sh
func start
```
- The function will listen for Event Grid events.

#### Option B: Docker
```sh
docker build -t wsi-slides-dzi-processor:local .
docker run -p 8080:80 -e AzureWebJobsStorage='UseDevelopmentStorage=true' wsi-slides-dzi-processor:local
```

### 3. Simulate an Event Grid Event
Create a file named `event.json` with the following content:
```json
[
  {
    "id": "test-id",
    "eventType": "Microsoft.Storage.BlobCreated",
    "subject": "/blobServices/default/containers/your-container/blobs/your-image.jpg",
    "eventTime": "2025-06-27T00:00:00.000Z",
    "data": {
      "url": "https://<your-storage-account>.blob.core.windows.net/your-container/your-image.jpg"
    },
    "dataVersion": "",
    "metadataVersion": "1"
  }
]
```
- Replace `<your-storage-account>`, `your-container`, and `your-image.jpg` with your actual values.

Send the event to your local function:
```sh
curl -X POST "http://localhost:7071/runtime/webhooks/EventGrid?functionName=blob_to_dzi_eventgrid_trigger" \
  -H "Content-Type: application/json" \
  -d @event.json
```

### 4. Check Logs and Output
- Monitor the terminal for logs and errors.
- Check your storage account or Azurite for the output in the `web-slides-dzi-output` container.

### Troubleshooting
- Ensure the blob and container exist in your storage account.
- Check for errors in the logs.
- Make sure all dependencies are installed and the correct Python version is used.

---
*For more, see the Azure Functions [local development docs](https://learn.microsoft.com/azure/azure-functions/functions-develop-local).*