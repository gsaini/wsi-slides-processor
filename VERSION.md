# Version History

## v1.0.1 (2025-12-04)

### Security Fixes

- ✅ Fixed CVE-2025-49794 (CRITICAL 9.1) - libxml2 use-after-free vulnerability
- ✅ Fixed CVE-2025-49796 (CRITICAL 9.1) - libxml2 memory corruption vulnerability
- ✅ Fixed CVE-2022-49043 (HIGH 8.1) - libxml2 vulnerability
- ✅ Fixed CVE-2023-31484 (HIGH 8.1) - perl vulnerability
- ✅ Fixed CVE-2024-56171 (HIGH 7.8) - libxml2 vulnerability
- ✅ Fixed CVE-2025-24928 (HIGH 7.8) - libxml2 vulnerability
- ✅ Fixed CVE-2025-49180 (HIGH 7.8) - xorg-server vulnerability
- ✅ Fixed CVE-2025-4802 (HIGH 7.8) - glibc vulnerability
- ✅ Fixed CVE-2024-25062 (HIGH 7.5) - libxml2 vulnerability

### Changes

- Upgraded system packages (libxml2, glibc, perl, xorg-server) to latest patched versions
- Optimized Dockerfile with combined RUN commands for smaller image size
- Added `--no-cache-dir` to pip for reduced image size
- Enhanced `.dockerignore` for faster builds
- Added platform specification for Apple Silicon compatibility

### Package Versions

- Python: 3.12.12
- libxml2: 2.9.14+dfsg-1.3~deb12u4
- libc6: 2.36-9+deb12u13
- perl-base: 5.36.0-7+deb12u3

### Docker Image

- **Registry**: Docker Hub
- **Image**: `docker.io/gopalsaini/wsi-slides-processor:1.0.1`
- **Size**: 755MB (compressed)
- **Platform**: linux/amd64
- **Digest**: sha256:80b6e0260cd71b7de1a707d740e369564aa53a6998c9724c61d85179e5333c64

### Known Issues

- ⚠️ CVE-2025-22871 (CRITICAL 9.1) - golang stdlib 1.23.1
  - Status: Fixed in Go 1.23.8, waiting for base image update from Microsoft
  - Mitigation: Using latest available Python 3.12 base image

### Deployment

```bash
# Pull the image
docker pull gopalsaini/wsi-slides-processor:1.0.1

# Run locally (for testing)
docker run --platform=linux/amd64 -p 8080:80 gopalsaini/wsi-slides-processor:1.0.1

# Deploy to Azure Functions
az functionapp create \
  --name <your-app> \
  --resource-group <your-rg> \
  --storage-account <your-storage> \
  --plan <your-plan> \
  --deployment-container-image-name gopalsaini/wsi-slides-processor:1.0.1 \
  --functions-version 4
```

### Documentation

- [SECURITY.md](./SECURITY.md) - Security vulnerability tracking
- [AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md) - Azure deployment guide
- [Dockerfile](./Dockerfile) - Image build configuration

---

## Previous Versions

### v1.0.0 (Initial Release)

- Base Azure Functions Python 3.12 image
- Initial application code
