# PowerShell Script for Hugging Face Spaces Deployment Preparation
# This script prepares your repository for deployment on Hugging Face Spaces

$ErrorActionPreference = "Stop"

# Colors for output
$green = "`e[32m"
$yellow = "`e[33m"
$red = "`e[31m"
$blue = "`e[34m"
$reset = "`e[0m"

Write-Host "${blue}Preparing Todoapp for Hugging Face Spaces deployment...${reset}" -ForegroundColor Blue

# Function to print colored output
function Write-Status([string]$message) {
    Write-Host "[INFO] $message" -ForegroundColor Green
}

function Write-Warning([string]$message) {
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-Error([string]$message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Check if git is installed
try {
    git --version 2>$null | Out-Null
    Write-Status "git is installed"
} catch {
    Write-Error "git is not installed. Please install git first."
    exit 1
}

# Pull the latest changes from GitHub
Write-Status "Pulling latest changes from GitHub..."
try {
    git pull origin main 2>&1 | Out-Null
} catch {
    # If main fails, try master
    try {
        git pull origin master 2>&1 | Out-Null
    } catch {
        Write-Error "Failed to pull from GitHub"
        exit 1
    }
}

Write-Status "Successfully pulled latest changes"

# Ensure required files exist
$REQUIRED_FILES = @(
    "Dockerfile.huggingface",
    "app.yml",
    "README.hf.md",
    "backend\requirements.txt"
)

foreach ($file in $REQUIRED_FILES) {
    if (!(Test-Path $file)) {
        Write-Error "Required file $file does not exist!"
        exit 1
    }
}

Write-Status "All required files are present"

# Copy the Hugging Face Dockerfile to the root as Dockerfile
Write-Status "Copying Hugging Face Dockerfile to root..."
Copy-Item "Dockerfile.huggingface" -Destination "Dockerfile" -Force

Write-Status "Repository is ready for Hugging Face Spaces deployment!"

Write-Host ""
Write-Host "${green}=== HUGGING FACE DEPLOYMENT INSTRUCTIONS ===${reset}" -ForegroundColor Green
Write-Host "1. Go to https://huggingface.co/spaces"
Write-Host "2. Click 'Create New Space'"
Write-Host "3. Choose 'Docker' as the SDK"
Write-Host "4. Connect to your repository"
Write-Host "5. The app will automatically build and deploy"
Write-Host ""
Write-Host "Note: Make sure your repository contains:"
Write-Host "- Dockerfile.huggingface (copied as Dockerfile)"
Write-Host "- app.yml (configuration file)"
Write-Host "- All application code"
Write-Host "- requirements.txt with dependencies"
Write-Host ""

Write-Status "Your repository is now prepared for Hugging Face Spaces deployment!"