# Security Vulnerability Management

## Last Updated: 2025-12-04

## Summary

This document tracks security vulnerabilities in the WSI Slides Processor Docker image and the actions taken to address them.

## Vulnerability Status

### ✅ Resolved (9 vulnerabilities)

| CVE ID         | Severity | Score | Package     | Fix Applied          |
| -------------- | -------- | ----- | ----------- | -------------------- |
| CVE-2025-49794 | CRITICAL | 9.1   | libxml2     | Upgraded via apt-get |
| CVE-2025-49796 | CRITICAL | 9.1   | libxml2     | Upgraded via apt-get |
| CVE-2022-49043 | HIGH     | 8.1   | libxml2     | Upgraded via apt-get |
| CVE-2023-31484 | HIGH     | 8.1   | perl        | Upgraded via apt-get |
| CVE-2024-56171 | HIGH     | 7.8   | libxml2     | Upgraded via apt-get |
| CVE-2025-24928 | HIGH     | 7.8   | libxml2     | Upgraded via apt-get |
| CVE-2025-49180 | HIGH     | 7.8   | xorg-server | Upgraded via apt-get |
| CVE-2025-4802  | HIGH     | 7.8   | glibc       | Upgraded via apt-get |
| CVE-2024-25062 | HIGH     | 7.5   | libxml2     | Upgraded via apt-get |

### ⚠️ Pending (1 vulnerability)

| CVE ID         | Severity | Score | Package              | Status             | Action Required                      |
| -------------- | -------- | ----- | -------------------- | ------------------ | ------------------------------------ |
| CVE-2025-22871 | CRITICAL | 9.1   | golang stdlib 1.23.1 | Fixed in Go 1.23.8 | Wait for Microsoft base image update |

**Details:**

- **Issue**: Request smuggling vulnerability in `net/http` package
- **Fix Available**: Go 1.23.8
- **Current Base Image**: Uses Go 1.23.1 (embedded in Azure Functions runtime)
- **Mitigation**: Upgraded to Python 3.13 base image (latest available)
- **Monitoring**: Check [mcr.microsoft.com/azure-functions/python](https://mcr.microsoft.com/v2/azure-functions/python/tags/list) weekly

## Actions Taken

### 1. Base Image Upgrade

- **Current**: `mcr.microsoft.com/azure-functions/python:4-python3.12`
- **Status**: Latest stable version available (Python 3.13+ only available in `-appservice` variant)
- **Reason**: Most recent security patches for standard Azure Functions runtime

### 2. Explicit Package Upgrades

Added explicit installation of vulnerable packages to ensure latest versions:

```dockerfile
apt-get install -y --no-install-recommends \
    libxml2 \
    libc6 \
    libc-bin \
    perl-base \
    xserver-common
```

### 3. Build Optimizations

- Combined RUN commands to reduce layers
- Added `--no-cache-dir` to pip for smaller image size
- Removed build dependencies after use
- Added comprehensive `.dockerignore`

## Maintenance Recommendations

### Weekly Tasks

1. **Check for base image updates**:

   ```bash
   docker pull mcr.microsoft.com/azure-functions/python:4-python3.13
   docker image inspect mcr.microsoft.com/azure-functions/python:4-python3.13
   ```

2. **Rebuild the image**:

   ```bash
   docker build -t wsi-slides-processor:latest .
   ```

3. **Scan for vulnerabilities**:

   ```bash
   # Using Docker Scout
   docker scout cves wsi-slides-processor:latest

   # Or using Trivy
   trivy image wsi-slides-processor:latest
   ```

### Monthly Tasks

1. Review CVE databases for new vulnerabilities
2. Update this document with new findings
3. Test application compatibility with latest base images

## Vulnerability Scanning Tools

### Recommended Tools

- **Docker Scout**: Built into Docker Desktop
- **Trivy**: Open-source vulnerability scanner
- **Snyk**: Commercial solution with free tier
- **Azure Defender for Containers**: If deploying to Azure

### Example Scan Commands

**Docker Scout**:

```bash
docker scout cves wsi-slides-processor:latest --only-severity critical,high
```

**Trivy**:

```bash
trivy image --severity CRITICAL,HIGH wsi-slides-processor:latest
```

## Incident Response

If a new critical vulnerability is discovered:

1. **Assess Impact**: Determine if the vulnerability affects your deployment
2. **Check for Fixes**: Look for updated packages or base images
3. **Test Updates**: Build and test with updated dependencies
4. **Deploy**: Roll out the patched image
5. **Document**: Update this file with the CVE and resolution

## References

- [Azure Functions Base Images](https://mcr.microsoft.com/v2/azure-functions/python/tags/list)
- [Debian Security Tracker](https://security-tracker.debian.org/tracker/)
- [CVE Database](https://cve.mitre.org/)
- [National Vulnerability Database](https://nvd.nist.gov/)

## Contact

For security concerns, contact: [Your Security Team Email]

---

**Note**: This is a living document. Update it whenever security changes are made to the Docker image.
