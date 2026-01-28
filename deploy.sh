#!/bin/bash

# Deployment script for Todoapp to Kubernetes
# This script pulls the latest changes from GitHub and deploys to Kubernetes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting deployment process...${NC}"

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

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

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

# Build Docker images (assuming Minikube is running)
print_status "Setting Docker environment to Minikube..."
eval $(minikube -p minikube docker-env --shell bash)

print_status "Building Docker images..."
./build_images.sh

if [ $? -ne 0 ]; then
    print_error "Failed to build Docker images"
    exit 1
fi

print_status "Docker images built successfully"

# Apply Kubernetes configurations
print_status "Deploying to Kubernetes..."

# Create namespace if it doesn't exist
kubectl apply -f k8s/namespace.yaml

# Apply PostgreSQL deployment
kubectl apply -f k8s/postgresql.yaml

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
kubectl rollout status deployment/postgres-deployment -n todoapp --timeout=120s

# Apply Kafka if available
if [ -f "k8s/kafka/kafka-full.yaml" ]; then
    kubectl apply -f k8s/kafka/kafka-full.yaml
    print_status "Waiting for Kafka to be ready..."
    kubectl rollout status deployment/kafka-deployment -n todoapp --timeout=180s || print_warning "Kafka may take longer to start, continuing deployment..."
fi

# Apply backend deployment
kubectl apply -f k8s/deployments/backend-deployment.yaml

# Wait for backend to be ready
print_status "Waiting for backend to be ready..."
kubectl rollout status deployment/backend-deployment -n todoapp --timeout=120s

# Apply frontend deployment
kubectl apply -f k8s/deployments/frontend-deployment.yaml

# Wait for frontend to be ready
print_status "Waiting for frontend to be ready..."
kubectl rollout status deployment/frontend-deployment -n todoapp --timeout=120s

# Apply ingress if available
if [ -f "k8s/ingress/todo-app-ingress.yaml" ]; then
    kubectl apply -f k8s/ingress/todo-app-ingress.yaml
fi

# Get service information
print_status "Deployment completed! Service information:"
kubectl get services -n todoapp

# Get pod status
print_status "Pod status:"
kubectl get pods -n todoapp

# Get external IP if using LoadBalancer
print_status "Getting external IPs (may take a moment)..."
kubectl get svc frontend-service -n todoapp -o jsonpath='{.status.loadBalancer.ingress[0].ip}' > /tmp/frontend_ip 2>/dev/null || echo "pending" > /tmp/frontend_ip
kubectl get svc backend-service -n todoapp -o jsonpath='{.status.loadBalancer.ingress[0].ip}' > /tmp/backend_ip 2>/dev/null || echo "pending" > /tmp/backend_ip

FRONTEND_IP=$(cat /tmp/frontend_ip)
BACKEND_IP=$(cat /tmp/backend_ip)

echo ""
echo -e "${GREEN}=== DEPLOYMENT SUMMARY ===${NC}"
echo -e "Frontend External IP: ${FRONTEND_IP:-pending}"
echo -e "Backend External IP: ${BACKEND_IP:-pending}"
echo -e "Namespace: todoapp"
echo ""
echo -e "To access the application:"
echo -e "  Frontend: http://${FRONTEND_IP:-PENDING}:3000"
echo -e "  Backend: http://${BACKEND_IP:-PENDING}:8000"
echo ""

# Clean up temp files
rm -f /tmp/frontend_ip /tmp/backend_ip

print_status "Deployment script completed successfully!"