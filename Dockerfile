# Azure Functions Python Base Image
# Note: This image only supports linux/amd64 platform
# On Apple Silicon (ARM64), build with: docker build --platform=linux/amd64 -t <image-name> .
# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.12-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.12

# Install system dependencies, security updates, AzCopy, and perform cleanup in a single layer
RUN apt-get update && \
    apt-get upgrade -y && \
    # Install security updates for specific vulnerable packages
    apt-get install -y --no-install-recommends \
    libvips \
    wget \
    ca-certificates \
    # Upgrade libxml2 to fix CVE-2025-49794, CVE-2025-49796, CVE-2022-49043, CVE-2024-56171, CVE-2025-24928, CVE-2024-25062
    libxml2 \
    # Upgrade glibc to fix CVE-2025-4802
    libc6 \
    libc-bin \
    # Upgrade perl to fix CVE-2023-31484
    perl-base \
    # Upgrade xorg-server to fix CVE-2025-49180
    xserver-common && \
    # Download and install AzCopy
    wget -O azcopy.tar.gz https://aka.ms/downloadazcopy-v10-linux && \
    tar -xzf azcopy.tar.gz && \
    cp ./azcopy_linux_amd64_*/azcopy /usr/local/bin/ && \
    chmod +x /usr/local/bin/azcopy && \
    rm -rf azcopy.tar.gz azcopy_linux_amd64_* && \
    # Cleanup to reduce image size
    apt-get remove -y wget && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Install Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Copy application code
COPY . /home/site/wwwroot

# ---
# Security Notice (2025-12-04):
#
# Addressed vulnerabilities:
# ✓ CVE-2025-49794 (CRITICAL 9.1) - libxml2: Fixed via apt-get upgrade
# ✓ CVE-2025-49796 (CRITICAL 9.1) - libxml2: Fixed via apt-get upgrade
# ✓ CVE-2022-49043 (HIGH 8.1) - libxml2: Fixed via apt-get upgrade
# ✓ CVE-2024-56171 (HIGH 7.8) - libxml2: Fixed via apt-get upgrade
# ✓ CVE-2025-24928 (HIGH 7.8) - libxml2: Fixed via apt-get upgrade
# ✓ CVE-2024-25062 (HIGH 7.5) - libxml2: Fixed via apt-get upgrade
# ✓ CVE-2023-31484 (HIGH 8.1) - perl: Fixed via apt-get upgrade
# ✓ CVE-2025-49180 (HIGH 7.8) - xorg-server: Fixed via apt-get upgrade
# ✓ CVE-2025-4802 (HIGH 7.8) - glibc: Fixed via apt-get upgrade
#
# Remaining vulnerabilities (base image dependency):
# ⚠ CVE-2025-22871 (CRITICAL 9.1) - golang stdlib 1.23.1
#   Status: Fixed in Go 1.23.8, waiting for base image update from Microsoft
#   Mitigation: Using Python 3.12 base image (latest available standard version)
#   Note: Python 3.13+ only available in -appservice variant
#   Action: Monitor mcr.microsoft.com/azure-functions/python for updates
#
# Recommendation: Rebuild this image weekly to incorporate latest security patches
# ---