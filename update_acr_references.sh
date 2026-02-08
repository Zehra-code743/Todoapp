#!/bin/bash

# Script to update Azure deployment files with correct ACR name
# This script should be run after creating the ACR to update the image references

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

if [ $# -ne 1 ]; then
    echo "Usage: $0 <acr-name>"
    echo "Example: $0 todoappregistry12345"
    exit 1
fi

ACR_NAME="$1"

print_status "Updating deployment files with ACR name: $ACR_NAME"

# Update backend deployment
sed -i "s|todoappregistry.azurecr.io|$ACR_NAME.azurecr.io|g" azure-k8s-configs/backend-deployment.yaml

# Update frontend deployment
sed -i "s|todoappregistry.azurecr.io|$ACR_NAME.azurecr.io|g" azure-k8s-configs/frontend-deployment.yaml

print_status "Deployment files updated successfully!"

echo ""
echo "Updated files:"
echo "- azure-k8s-configs/backend-deployment.yaml"
echo "- azure-k8s-configs/frontend-deployment.yaml"