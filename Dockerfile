# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.12-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.12

# Install AzCopy and add to PATH
RUN wget -O azcopy.tar.gz https://aka.ms/downloadazcopy-v10-linux \
    && tar -xzf azcopy.tar.gz \
    && cp ./azcopy_linux_amd64_*/azcopy /usr/local/bin/ \
    && chmod +x /usr/local/bin/azcopy \
    && rm -rf azcopy.tar.gz azcopy_linux_amd64_*

# Update and upgrade system packages to fix vulnerabilities
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libvips && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot

# ---
# Security Notice (2025-06-27):
#
# This image may contain vulnerabilities inherited from the base image or system libraries:
# - CRITICAL: stdlib (Go) CVE-2025-22871 (fixed in 1.23.8, not yet available in base image)
# - HIGH: pam CVE-2025-6020 (no fix available upstream)
#
# These cannot be mitigated at the Dockerfile level. Monitor upstream for updates and rebuild regularly.
# ---