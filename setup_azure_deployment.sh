#!/bin/bash

# Azure Deployment Setup Script for Todoapp
# This script will guide you through setting up Azure CLI, creating resources,
# and deploying the Todoapp to Azure Kubernetes Service (AKS)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}Todoapp Azure Deployment Setup${NC}"
echo -e "${BLUE}=======================================${NC}"

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

check_az_cli() {
    print_status "Checking if Azure CLI is installed..."
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Installing Azure CLI..."
        install_az_cli
    else
        print_status "Azure CLI is already installed."
        az --version
    fi
}

install_az_cli() {
    print_status "Installing Azure CLI..."

    # Detect OS and install Azure CLI accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux installation
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS installation
        brew install azure-cli
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows installation (PowerShell)
        print_error "Please run this script on Linux/macOS or install Azure CLI manually on Windows:"
        print_error "Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi

    print_status "Azure CLI installed successfully!"
}

login_to_azure() {
    print_status "Logging in to Azure..."

    # Login using device code flow (recommended for security)
    print_status "Opening browser for Azure login. Please login with your account."
    print_status "Use the email: shanezehra117@gmail.com"
    az login --use-device-code

    if [ $? -eq 0 ]; then
        print_status "Successfully logged in to Azure!"
    else
        print_error "Failed to log in to Azure"
        exit 1
    fi
}

get_subscription_id() {
    print_status "Getting Azure subscriptions..."
    az account list -o table

    echo
    read -p "Enter the Subscription ID you want to use: " SUBSCRIPTION_ID

    # Validate subscription ID format (basic validation)
    if [[ ! $SUBSCRIPTION_ID =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
        print_error "Invalid subscription ID format"
        exit 1
    fi

    export SUBSCRIPTION_ID=$SUBSCRIPTION_ID

    print_status "Setting subscription to: $SUBSCRIPTION_ID"
    az account set --subscription $SUBSCRIPTION_ID
}

create_resource_group() {
    print_status "Creating Azure Resource Group..."

    RESOURCE_GROUP_NAME="todoapp-rg"
    LOCATION="EastUS"  # You can change this to your preferred region

    echo "Resource Group Name: $RESOURCE_GROUP_NAME"
    echo "Location: $LOCATION"

    az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

    if [ $? -eq 0 ]; then
        print_status "Resource group created successfully!"
        export RESOURCE_GROUP_NAME=$RESOURCE_GROUP_NAME
        export LOCATION=$LOCATION
    else
        print_error "Failed to create resource group"
        exit 1
    fi
}

create_acr() {
    print_status "Creating Azure Container Registry..."

    ACR_NAME="todoappregistry$(date +%s)"  # Unique name with timestamp
    export ACR_NAME=$ACR_NAME

    print_status "Creating ACR with name: $ACR_NAME"

    az acr create --resource-group $RESOURCE_GROUP_NAME --name $ACR_NAME --sku Basic

    if [ $? -eq 0 ]; then
        print_status "Azure Container Registry created successfully!"
    else
        print_error "Failed to create Azure Container Registry"
        exit 1
    fi
}

create_aks_cluster() {
    print_status "Creating Azure Kubernetes Service (AKS) cluster..."

    AKS_CLUSTER_NAME="todoapp-aks"
    export AKS_CLUSTER_NAME=$AKS_CLUSTER_NAME

    print_status "Creating AKS cluster with name: $AKS_CLUSTER_NAME"

    az aks create \
        --resource-group $RESOURCE_GROUP_NAME \
        --name $AKS_CLUSTER_NAME \
        --node-count 2 \
        --enable-addons monitoring \
        --generate-ssh-keys \
        --attach-acr $ACR_NAME

    if [ $? -eq 0 ]; then
        print_status "AKS cluster created successfully!"
    else
        print_error "Failed to create AKS cluster"
        exit 1
    fi
}

configure_kubectl() {
    print_status "Configuring kubectl to connect to AKS cluster..."

    az aks get-credentials --resource-group $RESOURCE_GROUP_NAME --name $AKS_CLUSTER_NAME

    if [ $? -eq 0 ]; then
        print_status "kubectl configured successfully!"

        # Verify connection
        print_status "Verifying kubectl connection..."
        kubectl get nodes
    else
        print_error "Failed to configure kubectl"
        exit 1
    fi
}

build_and_push_images() {
    print_status "Building and pushing Docker images to Azure Container Registry..."

    # Log in to ACR
    az acr login --name $ACR_NAME

    # Build backend image
    print_status "Building backend image..."
    docker build -t todo-backend:latest -f backend/Dockerfile .

    # Tag backend image for ACR
    docker tag todo-backend:latest $ACR_NAME.azurecr.io/todo-backend:latest

    # Push backend image
    docker push $ACR_NAME.azurecr.io/todo-backend:latest

    # Build frontend image
    print_status "Building frontend image..."
    docker build -t todo-frontend:latest -f frontend/Dockerfile .

    # Tag frontend image for ACR
    docker tag todo-frontend:latest $ACR_NAME.azurecr.io/todo-frontend:latest

    # Push frontend image
    docker push $ACR_NAME.azurecr.io/todo-frontend:latest

    if [ $? -eq 0 ]; then
        print_status "Docker images built and pushed successfully!"
    else
        print_error "Failed to build or push Docker images"
        exit 1
    fi
}

update_k8s_configs() {
    print_status "Updating Kubernetes configurations for Azure..."

    # Create a temporary directory for updated configs
    mkdir -p azure-k8s-configs

    # Copy existing configs and update image references
    for file in k8s/deployments/backend-deployment.yaml k8s/deployments/frontend-deployment.yaml; do
        if [ -f "$file" ]; then
            # Update image references in deployment files
            sed "s|image: todo-task-service:latest|image: $ACR_NAME.azurecr.io/todo-backend:latest|g" "$file" > "azure-k8s-configs/$(basename "$file")"
            sed -i.bak "s|image: todo-frontend:latest|image: $ACR_NAME.azurecr.io/todo-frontend:latest|g" "azure-k8s-configs/$(basename "$file")"
            rm "azure-k8s-configs/$(basename "$file").bak"  # Remove backup file
        fi
    done

    print_status "Kubernetes configurations updated for Azure!"
}

deploy_to_aks() {
    print_status "Deploying Todoapp to AKS cluster..."

    # Create namespace
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

    # Apply updated deployments with Azure ACR images
    if [ -d "azure-k8s-configs" ]; then
        kubectl apply -f azure-k8s-configs/
    else
        kubectl apply -f k8s/deployments/
    fi

    # Apply ingress if available
    if [ -f "k8s/ingress/todo-app-ingress.yaml" ]; then
        kubectl apply -f k8s/ingress/todo-app-ingress.yaml
    fi

    # Wait for deployments to be ready
    print_status "Waiting for backend to be ready..."
    kubectl rollout status deployment/backend-deployment -n todoapp --timeout=120s

    print_status "Waiting for frontend to be ready..."
    kubectl rollout status deployment/frontend-deployment -n todoapp --timeout=120s

    if [ $? -eq 0 ]; then
        print_status "Todoapp deployed successfully to AKS!"
    else
        print_error "Failed to deploy Todoapp to AKS"
        exit 1
    fi
}

show_access_info() {
    print_status "Getting deployment information..."

    echo ""
    echo -e "${GREEN}=== DEPLOYMENT INFORMATION ===${NC}"
    echo ""
    echo "Resource Group: $RESOURCE_GROUP_NAME"
    echo "AKS Cluster: $AKS_CLUSTER_NAME"
    echo "Container Registry: $ACR_NAME.azurecr.io"
    echo ""

    # Get service information
    echo -e "${GREEN}Services:${NC}"
    kubectl get services -n todoapp

    echo ""
    echo -e "${GREEN}Pods:${NC}"
    kubectl get pods -n todoapp

    # Get external IP if using LoadBalancer
    echo ""
    echo -e "${GREEN}External Access:${NC}"
    FRONTEND_IP=$(kubectl get svc frontend-service -n todoapp -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    BACKEND_IP=$(kubectl get svc backend-service -n todoapp -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

    echo "Frontend External IP: ${FRONTEND_IP:-pending}"
    echo "Backend External IP: ${BACKEND_IP:-pending}"
    echo ""

    echo "To access the application:"
    echo "  Frontend: http://${FRONTEND_IP:-PENDING}:3000"
    echo "  Backend: http://${BACKEND_IP:-PENDING}:8000"
    echo ""

    echo -e "${GREEN}Deployment completed successfully!${NC}"
}

# Main execution flow
main() {
    print_status "Starting Azure deployment setup for Todoapp..."

    # Step 1: Check/install Azure CLI
    check_az_cli

    # Step 2: Login to Azure
    login_to_azure

    # Step 3: Select subscription
    get_subscription_id

    # Step 4: Create resource group
    create_resource_group

    # Step 5: Create ACR
    create_acr

    # Step 6: Create AKS cluster
    create_aks_cluster

    # Step 7: Configure kubectl
    configure_kubectl

    # Step 8: Build and push images
    build_and_push_images

    # Step 9: Update K8s configs
    update_k8s_configs

    # Step 10: Deploy to AKS
    deploy_to_aks

    # Step 11: Show access information
    show_access_info

    print_status "Azure deployment setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Verify the deployment using: kubectl get pods -n todoapp"
    echo "2. Access your application using the external IPs shown above"
    echo "3. Monitor the application using Azure portal"
}

# Run the main function
main