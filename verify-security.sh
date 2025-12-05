#!/bin/bash

# Security Vulnerability Verification Script
# This script helps verify that security patches have been applied

set -e

echo "🔍 WSI Slides Processor - Security Verification"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

echo "📦 Building Docker image..."
echo "   (Using linux/amd64 platform for Azure Functions compatibility)"
docker build --platform=linux/amd64 -t wsi-slides-processor:security-check . --no-cache

echo ""
echo "🔍 Checking installed package versions..."
echo ""

# Check libxml2 version
echo -n "Checking libxml2 version: "
LIBXML2_VERSION=$(docker run --rm wsi-slides-processor:security-check dpkg -l | grep libxml2 | awk '{print $3}')
echo -e "${GREEN}$LIBXML2_VERSION${NC}"

# Check glibc version
echo -n "Checking glibc version: "
GLIBC_VERSION=$(docker run --rm wsi-slides-processor:security-check dpkg -l | grep libc6 | head -1 | awk '{print $3}')
echo -e "${GREEN}$GLIBC_VERSION${NC}"

# Check perl version
echo -n "Checking perl version: "
PERL_VERSION=$(docker run --rm wsi-slides-processor:security-check dpkg -l | grep perl-base | awk '{print $3}')
echo -e "${GREEN}$PERL_VERSION${NC}"

# Check Python version
echo -n "Checking Python version: "
PYTHON_VERSION=$(docker run --rm wsi-slides-processor:security-check python --version)
echo -e "${GREEN}$PYTHON_VERSION${NC}"

echo ""
echo "🛡️ Running vulnerability scan..."
echo ""

# Check if Docker Scout is available
if docker scout version &> /dev/null; then
    echo "Using Docker Scout..."
    docker scout cves wsi-slides-processor:security-check --only-severity critical,high
else
    echo -e "${YELLOW}⚠️  Docker Scout not available. Install it for vulnerability scanning.${NC}"
    echo "   Visit: https://docs.docker.com/scout/install/"
fi

# Check if Trivy is available
if command -v trivy &> /dev/null; then
    echo ""
    echo "Using Trivy..."
    trivy image --severity CRITICAL,HIGH wsi-slides-processor:security-check
else
    echo -e "${YELLOW}⚠️  Trivy not available. Install it for additional scanning.${NC}"
    echo "   Install: brew install trivy (macOS) or see https://aquasecurity.github.io/trivy/"
fi

echo ""
echo "✅ Verification complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Review the vulnerability scan results above"
echo "   2. Check SECURITY.md for detailed CVE tracking"
echo "   3. If CVE-2025-22871 still appears, it's expected (base image dependency)"
echo "   4. Schedule weekly rebuilds to get latest security patches"
