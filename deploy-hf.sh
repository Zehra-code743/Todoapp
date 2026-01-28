#!/bin/bash
# Hugging Face Spaces Deployment Script
# This script prepares your repository for deployment on Hugging Face Spaces

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Preparing Todoapp for Hugging Face Spaces deployment...${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "git is not installed. Please install git first."
    exit 1
fi

# Pull the latest changes from GitHub
print_status "Pulling latest changes from GitHub..."
git pull origin main || git pull origin master

if [ $? -ne 0 ]; then
    print_error "Failed to pull from GitHub"
    exit 1
fi

print_status "Successfully pulled latest changes"

# Ensure required files exist
REQUIRED_FILES=(
    "Dockerfile.huggingface"
    "app.yml"
    "README.hf.md"
    "backend/requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file $file does not exist!"
        exit 1
    fi
done

print_status "All required files are present"

# Copy the Hugging Face Dockerfile to the root as Dockerfile
print_status "Copying Hugging Face Dockerfile to root..."
cp Dockerfile.huggingface Dockerfile

# If using a specific branch for Hugging Face deployment, you might want to push to a specific remote
print_status "Repository is ready for Hugging Face Spaces deployment!"

echo ""
echo -e "${GREEN}=== HUGGING FACE DEPLOYMENT INSTRUCTIONS ===${NC}"
echo "1. Go to https://huggingface.co/spaces"
echo "2. Click 'Create New Space'"
echo "3. Choose 'Docker' as the SDK"
echo "4. Connect to your repository"
echo "5. The app will automatically build and deploy"
echo ""
echo "Note: Make sure your repository contains:"
echo "- Dockerfile.huggingface (copied as Dockerfile)"
echo "- app.yml (configuration file)"
echo "- All application code"
echo "- requirements.txt with dependencies"
echo ""

print_status "Your repository is now prepared for Hugging Face Spaces deployment!"