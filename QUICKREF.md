# WSI Slides Processor - Quick Reference

## 🐳 Docker Image Information

**Current Version**: `1.0.1`  
**Registry**: Docker Hub  
**Image Name**: `gopalsaini/wsi-slides-processor`  
**Platform**: linux/amd64  
**Size**: 755MB

## 📦 Pull & Run

```bash
# Pull the latest version
docker pull gopalsaini/wsi-slides-processor:1.0.1

# Pull latest tag
docker pull gopalsaini/wsi-slides-processor:latest

# Run locally (Apple Silicon)
docker run --platform=linux/amd64 -p 8080:80 gopalsaini/wsi-slides-processor:1.0.1

# Run locally (Linux/Windows AMD64)
docker run -p 8080:80 gopalsaini/wsi-slides-processor:1.0.1
```

## 🚀 Azure Deployment

### Quick Deploy

```bash
az functionapp create \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --storage-account <your-storage-account> \
  --plan <your-app-service-plan> \
  --deployment-container-image-name gopalsaini/wsi-slides-processor:1.0.1 \
  --functions-version 4
```

### Update Existing App

```bash
az functionapp config container set \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --docker-custom-image-name gopalsaini/wsi-slides-processor:1.0.1
```

## 🔨 Build & Push (For Updates)

```bash
# Build for AMD64 (Azure's platform)
docker build --platform=linux/amd64 \
  -t gopalsaini/wsi-slides-processor:1.0.2 \
  -t gopalsaini/wsi-slides-processor:latest \
  .

# Push both tags
docker push gopalsaini/wsi-slides-processor:1.0.2
docker push gopalsaini/wsi-slides-processor:latest
```

## 🛡️ Security Status (v1.0.1)

| Status     | Count  | Details                     |
| ---------- | ------ | --------------------------- |
| ✅ Fixed   | 9 CVEs | 2 Critical, 7 High          |
| ⚠️ Pending | 1 CVE  | CVE-2025-22871 (base image) |

## 📋 Quick Commands

### Verify Image

```bash
# Check version
docker run --rm gopalsaini/wsi-slides-processor:1.0.1 python --version

# Check security patches
docker run --rm gopalsaini/wsi-slides-processor:1.0.1 \
  dpkg -l | grep -E "libxml2|libc6|perl-base"

# Run security scan
docker scout cves gopalsaini/wsi-slides-processor:1.0.1 --only-severity critical,high
```

### Azure Functions Commands

```bash
# Check app status
az functionapp show --name <app-name> --resource-group <rg-name> --query state

# View logs
az functionapp log tail --name <app-name> --resource-group <rg-name>

# Restart app
az functionapp restart --name <app-name> --resource-group <rg-name>
```

## 📚 Documentation

- **[VERSION.md](./VERSION.md)** - Version history and changelog
- **[SECURITY.md](./SECURITY.md)** - Security vulnerability tracking
- **[AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md)** - Complete deployment guide
- **[Dockerfile](./Dockerfile)** - Image build configuration

## 🔄 Maintenance Schedule

- **Weekly**: Automated security scans (GitHub Actions)
- **Monthly**: Rebuild image for latest patches
- **As Needed**: Update when critical CVEs announced

## 📞 Support

**Docker Hub**: https://hub.docker.com/r/gopalsaini/wsi-slides-processor  
**Azure Functions Docs**: https://docs.microsoft.com/azure/azure-functions/

---

**Last Updated**: 2025-12-04  
**Image Digest**: sha256:80b6e0260cd71b7de1a707d740e369564aa53a6998c9724c61d85179e5333c64
