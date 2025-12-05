# Azure Functions Deployment Guide

## Overview

This guide ensures your security-hardened Docker image deploys successfully to Azure Functions.

## ✅ Compatibility Confirmation

Your Dockerfile is **fully compatible** with Azure Functions:

- ✅ Uses official Microsoft base image: `mcr.microsoft.com/azure-functions/python:4-python3.12`
- ✅ Built for `linux/amd64` platform (Azure's native architecture)
- ✅ Security patches only affect system packages, not Azure Functions runtime
- ✅ All Azure Functions features remain fully functional

## Platform Architecture

| Environment                  | Architecture | Notes                                           |
| ---------------------------- | ------------ | ----------------------------------------------- |
| **Your Mac (Apple Silicon)** | ARM64        | Build with `--platform=linux/amd64` for testing |
| **Azure Functions**          | AMD64/x86_64 | Native execution, no emulation needed           |

## Deployment Options

### Option 1: Azure Container Registry (Recommended)

**Step 1: Build and tag the image**

```bash
# Build for Azure's AMD64 platform
docker build --platform=linux/amd64 -t wsi-slides-processor:latest .

# Tag for Azure Container Registry
docker tag wsi-slides-processor:latest <your-acr-name>.azurecr.io/wsi-slides-processor:latest
```

**Step 2: Push to Azure Container Registry**

```bash
# Login to ACR
az acr login --name <your-acr-name>

# Push the image
docker push <your-acr-name>.azurecr.io/wsi-slides-processor:latest
```

**Step 3: Deploy to Azure Functions**

```bash
# Create or update Function App with custom container
az functionapp create \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --storage-account <your-storage-account> \
  --plan <your-app-service-plan> \
  --deployment-container-image-name <your-acr-name>.azurecr.io/wsi-slides-processor:latest \
  --functions-version 4

# Configure ACR credentials
az functionapp config container set \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --docker-custom-image-name <your-acr-name>.azurecr.io/wsi-slides-processor:latest \
  --docker-registry-server-url https://<your-acr-name>.azurecr.io \
  --docker-registry-server-user <acr-username> \
  --docker-registry-server-password <acr-password>
```

### Option 2: Docker Hub

**Step 1: Build and tag**

```bash
docker build --platform=linux/amd64 -t <your-dockerhub-username>/wsi-slides-processor:latest .
```

**Step 2: Push to Docker Hub**

```bash
docker login
docker push <your-dockerhub-username>/wsi-slides-processor:latest
```

**Step 3: Deploy to Azure Functions**

```bash
az functionapp create \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --storage-account <your-storage-account> \
  --plan <your-app-service-plan> \
  --deployment-container-image-name <your-dockerhub-username>/wsi-slides-processor:latest \
  --functions-version 4
```

## CI/CD Deployment

### GitHub Actions Workflow

Create `.github/workflows/deploy-azure.yml`:

```yaml
name: Deploy to Azure Functions

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  AZURE_FUNCTIONAPP_NAME: your-function-app-name
  ACR_NAME: your-acr-name
  IMAGE_NAME: wsi-slides-processor

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to Azure Container Registry
        uses: azure/docker-login@v1
        with:
          login-server: ${{ env.ACR_NAME }}.azurecr.io
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build and push Docker image
        run: |
          docker build --platform=linux/amd64 \
            -t ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -t ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:latest \
            .
          docker push ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${{ github.sha }}
          docker push ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:latest

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy to Azure Functions
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_FUNCTIONAPP_NAME }}
          images: ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${{ github.sha }}

      - name: Run security scan on deployed image
        run: |
          docker pull ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:latest
          docker scout cves ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:latest \
            --only-severity critical,high
```

## Verification After Deployment

### 1. Check Function App Status

```bash
az functionapp show \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --query state
```

### 2. View Logs

```bash
az functionapp log tail \
  --name <your-function-app-name> \
  --resource-group <your-resource-group>
```

### 3. Test Function Endpoint

```bash
curl https://<your-function-app-name>.azurewebsites.net/api/<your-function-name>
```

### 4. Verify Container is Running

```bash
az functionapp config container show \
  --name <your-function-app-name> \
  --resource-group <your-resource-group>
```

## Environment Variables

Set required environment variables in Azure:

```bash
az functionapp config appsettings set \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --settings \
    "AzureWebJobsStorage=<storage-connection-string>" \
    "FUNCTIONS_WORKER_RUNTIME=python" \
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE=false"
```

## Troubleshooting

### Issue: Container fails to start

**Check logs:**

```bash
az functionapp log tail --name <your-function-app-name> --resource-group <your-resource-group>
```

**Common causes:**

- Missing environment variables
- Incorrect storage account configuration
- Port configuration (Azure Functions expects port 80)

### Issue: Functions not responding

**Verify the runtime:**

```bash
az functionapp config show \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --query linuxFxVersion
```

Should show: `DOCKER|<your-image-url>`

### Issue: Security vulnerabilities after deployment

**Re-scan the deployed image:**

```bash
# Pull from ACR
az acr login --name <your-acr-name>
docker pull <your-acr-name>.azurecr.io/wsi-slides-processor:latest

# Scan
docker scout cves <your-acr-name>.azurecr.io/wsi-slides-processor:latest
```

## Security Best Practices

1. **Use Managed Identity** for ACR access instead of username/password
2. **Enable Application Insights** for monitoring
3. **Set up alerts** for security vulnerabilities
4. **Implement automated rebuilds** weekly to get latest patches
5. **Use Azure Key Vault** for sensitive configuration

## Automated Security Updates

Set up a weekly rebuild schedule using Azure DevOps or GitHub Actions:

```yaml
on:
  schedule:
    # Every Monday at 2 AM UTC
    - cron: "0 2 * * 1"
```

This ensures you always have the latest security patches from the base image.

## Platform-Specific Notes

### Building on Apple Silicon (ARM64)

Always use `--platform=linux/amd64`:

```bash
docker build --platform=linux/amd64 -t wsi-slides-processor:latest .
```

### Building on Linux/Windows AMD64

No platform flag needed:

```bash
docker build -t wsi-slides-processor:latest .
```

## Support

- **Azure Functions Documentation**: https://docs.microsoft.com/azure/azure-functions/
- **Container Deployment**: https://docs.microsoft.com/azure/azure-functions/functions-create-function-linux-custom-image
- **Security Best Practices**: https://docs.microsoft.com/azure/security/

---

**Last Updated**: 2025-12-04

**Compatibility**: Azure Functions v4, Python 3.12
