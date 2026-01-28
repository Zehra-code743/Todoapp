# PowerShell Deployment Script for Todoapp to Kubernetes
# This script pulls the latest changes from GitHub and deploys to Kubernetes

# Set error handling
$ErrorActionPreference = "Stop"

# Colors for output
$green = "`e[32m"
$yellow = "`e[33m"
$red = "`e[31m"
$blue = "`e[34m"
$reset = "`e[0m"

Write-Host "${blue}Starting deployment process...${reset}" -ForegroundColor Blue

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

# Check if kubectl is installed
try {
    kubectl version --client 2>$null | Out-Null
    Write-Status "kubectl is installed"
} catch {
    Write-Error "kubectl is not installed. Please install kubectl first."
    exit 1
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

# Set Docker environment to Minikube (only if using Minikube)
Write-Status "Setting Docker environment to Minikube..."
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build Docker images
Write-Status "Building Docker images..."
try {
    & "$PSScriptRoot\build_images.sh"
} catch {
    Write-Error "Failed to build Docker images"
    exit 1
}

Write-Status "Docker images built successfully"

# Apply Kubernetes configurations
Write-Status "Deploying to Kubernetes..."

# Create namespace if it doesn't exist
kubectl apply -f k8s/namespace.yaml

# Apply PostgreSQL deployment
kubectl apply -f k8s/postgresql.yaml

# Wait for PostgreSQL to be ready
Write-Status "Waiting for PostgreSQL to be ready..."
try {
    kubectl rollout status deployment/postgres-deployment -n todoapp --timeout=120s
} catch {
    Write-Warning "PostgreSQL rollout may have timed out, continuing deployment..."
}

# Apply Kafka if available
if (Test-Path "k8s/kafka/kafka-full.yaml") {
    kubectl apply -f k8s/kafka/kafka-full.yaml
    Write-Status "Waiting for Kafka to be ready..."
    try {
        kubectl rollout status deployment/kafka-deployment -n todoapp --timeout=180s
    } catch {
        Write-Warning "Kafka may take longer to start, continuing deployment..."
    }
}

# Apply backend deployment
kubectl apply -f k8s/deployments/backend-deployment.yaml

# Wait for backend to be ready
Write-Status "Waiting for backend to be ready..."
try {
    kubectl rollout status deployment/backend-deployment -n todoapp --timeout=120s
} catch {
    Write-Warning "Backend rollout may have timed out, continuing deployment..."
}

# Apply frontend deployment
kubectl apply -f k8s/deployments/frontend-deployment.yaml

# Wait for frontend to be ready
Write-Status "Waiting for frontend to be ready..."
try {
    kubectl rollout status deployment/frontend-deployment -n todoapp --timeout=120s
} catch {
    Write-Warning "Frontend rollout may have timed out, continuing deployment..."
}

# Apply ingress if available
if (Test-Path "k8s/ingress/todo-app-ingress.yaml") {
    kubectl apply -f k8s/ingress/todo-app-ingress.yaml
}

# Get service information
Write-Status "Deployment completed! Service information:"
kubectl get services -n todoapp

# Get pod status
Write-Status "Pod status:"
kubectl get pods -n todoapp

Write-Status "Deployment script completed successfully!"

Write-Host "${green}=== DEPLOYMENT SUMMARY ===${reset}" -ForegroundColor Green
Write-Host "Namespace: todoapp"
Write-Host ""
Write-Host "To check service status run: kubectl get services -n todoapp"
Write-Host "To check pod status run: kubectl get pods -n todoapp"