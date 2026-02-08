#!/bin/bash

# Azure Deployment Script for Todoapp
# This script handles the complete deployment of Todoapp to Azure AKS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}Todoapp Azure Deployment Script${NC}"
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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Please install it first."
        print_status "Installation guide: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install it first."
        print_status "Installation guide: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        print_status "Installation guide: https://docs.docker.com/get-docker/"
        exit 1
    fi

    print_status "All prerequisites are installed."
}

# Function to login to Azure
login_to_azure() {
    print_status "Checking Azure authentication..."

    # Check if already logged in
    if az account show &> /dev/null; then
        CURRENT_USER=$(az account show --query user.name -o tsv 2>/dev/null)
        print_status "Already logged in as: $CURRENT_USER"
        return 0
    fi

    print_status "Logging in to Azure. Please use your email: shanezehra117@gmail.com"
    az login --use-device-code

    if [ $? -eq 0 ]; then
        print_status "Successfully logged in to Azure!"
    else
        print_error "Failed to log in to Azure"
        exit 1
    fi
}

# Function to get or create resource group
setup_resource_group() {
    print_status "Setting up Azure Resource Group..."

    # Check if RESOURCE_GROUP_NAME is already set
    if [ -z "$RESOURCE_GROUP_NAME" ]; then
        # List existing resource groups
        print_status "Existing Resource Groups:"
        az group list --query "[].{Name:name, Location:location}" -o table 2>/dev/null || echo "No resource groups found"

        echo
        read -p "Enter Resource Group name (or press Enter to create 'todoapp-rg'): " INPUT_RG
        if [ -z "$INPUT_RG" ]; then
            RESOURCE_GROUP_NAME="todoapp-rg"
        else
            RESOURCE_GROUP_NAME="$INPUT_RG"
        fi
    fi

    # Check if resource group exists
    if az group show --name $RESOURCE_GROUP_NAME &> /dev/null; then
        print_status "Resource group '$RESOURCE_GROUP_NAME' already exists."
    else
        # Ask for location or use default
        if [ -z "$LOCATION" ]; then
            echo
            read -p "Enter location (or press Enter for 'EastUS'): " INPUT_LOCATION
            if [ -z "$INPUT_LOCATION" ]; then
                LOCATION="EastUS"
            else
                LOCATION="$INPUT_LOCATION"
            fi
        fi

        print_status "Creating resource group '$RESOURCE_GROUP_NAME' in location '$LOCATION'..."
        az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

        if [ $? -eq 0 ]; then
            print_status "Resource group created successfully!"
        else
            print_error "Failed to create resource group"
            exit 1
        fi
    fi

    export RESOURCE_GROUP_NAME=$RESOURCE_GROUP_NAME
    export LOCATION=$LOCATION
}

# Function to get or create ACR
setup_acr() {
    print_status "Setting up Azure Container Registry..."

    # Check if ACR_NAME is already set
    if [ -z "$ACR_NAME" ]; then
        # List existing ACRs in the resource group
        print_status "Existing ACRs in resource group '$RESOURCE_GROUP_NAME':"
        az acr list --resource-group $RESOURCE_GROUP_NAME --query "[].{Name:name, Location:location}" -o table 2>/dev/null || echo "No ACRs found in this resource group"

        echo
        read -p "Enter ACR name (or press Enter to create one with timestamp): " INPUT_ACR
        if [ -z "$INPUT_ACR" ]; then
            ACR_NAME="todoappregistry$(date +%s)"
        else
            ACR_NAME="$INPUT_ACR"
        fi
    fi

    # Check if ACR exists
    if az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP_NAME &> /dev/null; then
        print_status "ACR '$ACR_NAME' already exists."
    else
        print_status "Creating ACR '$ACR_NAME'..."
        az acr create --resource-group $RESOURCE_GROUP_NAME --name $ACR_NAME --sku Basic

        if [ $? -eq 0 ]; then
            print_status "Azure Container Registry created successfully!"
        else
            print_error "Failed to create Azure Container Registry"
            exit 1
        fi
    fi

    export ACR_NAME=$ACR_NAME

    # Enable admin user for easier access (not recommended for production)
    print_status "Enabling admin user for ACR..."
    az acr update --name $ACR_NAME --admin-enabled true
}

# Function to get or create AKS cluster
setup_aks() {
    print_status "Setting up Azure Kubernetes Service..."

    # Check if AKS_CLUSTER_NAME is already set
    if [ -z "$AKS_CLUSTER_NAME" ]; then
        # List existing AKS clusters in the resource group
        print_status "Existing AKS clusters in resource group '$RESOURCE_GROUP_NAME':"
        az aks list --resource-group $RESOURCE_GROUP_NAME --query "[].{Name:name, Location:location}" -o table 2>/dev/null || echo "No AKS clusters found in this resource group"

        echo
        read -p "Enter AKS cluster name (or press Enter to create 'todoapp-aks'): " INPUT_AKS
        if [ -z "$INPUT_AKS" ]; then
            AKS_CLUSTER_NAME="todoapp-aks"
        else
            AKS_CLUSTER_NAME="$INPUT_AKS"
        fi
    fi

    # Check if AKS cluster exists
    if az aks show --name $AKS_CLUSTER_NAME --resource-group $RESOURCE_GROUP_NAME &> /dev/null; then
        print_status "AKS cluster '$AKS_CLUSTER_NAME' already exists."
    else
        print_status "Creating AKS cluster '$AKS_CLUSTER_NAME'..."

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
    fi

    export AKS_CLUSTER_NAME=$AKS_CLUSTER_NAME
}

# Function to configure kubectl
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

# Function to build and push images
build_and_push_images() {
    print_status "Building and pushing Docker images to Azure Container Registry..."

    # Login to ACR
    print_status "Logging in to ACR: $ACR_NAME"
    az acr login --name $ACR_NAME

    # Build backend image
    print_status "Building backend image..."
    docker build -t todo-backend:latest -f backend/Dockerfile .

    # Tag backend image for ACR
    BACKEND_IMAGE="$ACR_NAME.azurecr.io/todo-backend:latest"
    print_status "Tagging backend image: $BACKEND_IMAGE"
    docker tag todo-backend:latest $BACKEND_IMAGE

    # Push backend image
    print_status "Pushing backend image to ACR..."
    docker push $BACKEND_IMAGE

    # Build frontend image
    print_status "Building frontend image..."
    docker build -t todo-frontend:latest -f frontend/Dockerfile .

    # Tag frontend image for ACR
    FRONTEND_IMAGE="$ACR_NAME.azurecr.io/todo-frontend:latest"
    print_status "Tagging frontend image: $FRONTEND_IMAGE"
    docker tag todo-frontend:latest $FRONTEND_IMAGE

    # Push frontend image
    print_status "Pushing frontend image to ACR..."
    docker push $FRONTEND_IMAGE

    if [ $? -eq 0 ]; then
        print_status "Docker images built and pushed successfully!"

        # Store image names as environment variables for later use
        export BACKEND_IMAGE=$BACKEND_IMAGE
        export FRONTEND_IMAGE=$FRONTEND_IMAGE
    else
        print_error "Failed to build or push Docker images"
        exit 1
    fi
}

# Function to update deployment files with ACR images
update_deployment_files() {
    print_status "Updating Kubernetes deployment files with ACR images..."

    # Create a temporary directory for updated configs if it doesn't exist
    mkdir -p azure-k8s-configs

    # Copy existing configs if they don't exist
    if [ ! -f "azure-k8s-configs/backend-deployment.yaml" ]; then
        cp k8s/deployments/backend-deployment.yaml azure-k8s-configs/backend-deployment.yaml
    fi

    if [ ! -f "azure-k8s-configs/frontend-deployment.yaml" ]; then
        cp k8s/deployments/frontend-deployment.yaml azure-k8s-configs/frontend-deployment.yaml
    fi

    if [ ! -f "azure-k8s-configs/namespace.yaml" ]; then
        cp k8s/namespace.yaml azure-k8s-configs/namespace.yaml
    fi

    # Update image references in deployment files
    sed -i.bak "s|image: todo-task-service:latest|image: $BACKEND_IMAGE|g" azure-k8s-configs/backend-deployment.yaml
    sed -i.bak "s|image: todo-backend:latest|image: $BACKEND_IMAGE|g" azure-k8s-configs/backend-deployment.yaml
    rm azure-k8s-configs/backend-deployment.yaml.bak

    sed -i.bak "s|image: todo-frontend:local|image: $FRONTEND_IMAGE|g" azure-k8s-configs/frontend-deployment.yaml
    rm azure-k8s-configs/frontend-deployment.yaml.bak

    print_status "Kubernetes configurations updated with ACR image references!"
}

# Function to deploy to AKS
deploy_to_aks() {
    print_status "Deploying Todoapp to AKS cluster..."

    # Apply namespace
    print_status "Applying namespace..."
    kubectl apply -f azure-k8s-configs/namespace.yaml

    # Create default secrets if they don't exist
    if ! kubectl get secret postgres-secret -n todoapp &> /dev/null; then
        print_status "Creating default secrets..."
        kubectl create secret generic postgres-secret \
            --from-literal=username=postgres \
            --from-literal=password=yourSecurePassword123! \
            --from-literal=database_url=postgresql://postgres:yourSecurePassword123!@postgres-service:5432/todoapp \
            -n todoapp
    fi

    if ! kubectl get secret auth-secret -n todoapp &> /dev/null; then
        # Generate a random secret for auth (in production, use a strong secret)
        AUTH_SECRET=$(openssl rand -base64 32)
        kubectl create secret generic auth-secret \
            --from-literal=auth-secret="$AUTH_SECRET" \
            -n todoapp
    fi

    # Apply PostgreSQL deployment
    if [ -f "k8s/postgresql.yaml" ]; then
        print_status "Applying PostgreSQL deployment..."
        kubectl apply -f k8s/postgresql.yaml
    fi

    # Wait for PostgreSQL to be ready (if deployed)
    if kubectl get deployment postgres-deployment -n todoapp &> /dev/null; then
        print_status "Waiting for PostgreSQL to be ready..."
        kubectl rollout status deployment/postgres-deployment -n todoapp --timeout=120s
    fi

    # Apply Kafka if available
    if [ -f "k8s/kafka/kafka-full.yaml" ]; then
        print_status "Applying Kafka deployment..."
        kubectl apply -f k8s/kafka/kafka-full.yaml

        if kubectl get deployment kafka-deployment -n todoapp &> /dev/null; then
            print_status "Waiting for Kafka to be ready..."
            kubectl rollout status deployment/kafka-deployment -n todoapp --timeout=180s || print_warning "Kafka may take longer to start, continuing deployment..."
        fi
    fi

    # Apply updated deployments with Azure ACR images
    print_status "Applying backend deployment..."
    kubectl apply -f azure-k8s-configs/backend-deployment.yaml

    print_status "Applying frontend deployment..."
    kubectl apply -f azure-k8s-configs/frontend-deployment.yaml

    # Apply ingress if available
    if [ -f "k8s/ingress/todo-app-ingress.yaml" ]; then
        print_status "Applying ingress configuration..."
        kubectl apply -f k8s/ingress/todo-app-ingress.yaml
    fi

    # Wait for deployments to be ready
    print_status "Waiting for backend to be ready..."
    kubectl rollout status deployment/backend-deployment -n todoapp --timeout=180s

    print_status "Waiting for frontend to be ready..."
    kubectl rollout status deployment/frontend-deployment -n todoapp --timeout=180s

    if [ $? -eq 0 ]; then
        print_status "Todoapp deployed successfully to AKS!"
    else
        print_error "Failed to deploy Todoapp to AKS"
        exit 1
    fi
}

# Function to show access information
show_access_info() {
    print_status "Getting deployment information..."

    echo ""
    echo -e "${GREEN}=== DEPLOYMENT INFORMATION ===${NC}"
    echo ""
    echo "Resource Group: $RESOURCE_GROUP_NAME"
    echo "AKS Cluster: $AKS_CLUSTER_NAME"
    echo "Container Registry: $ACR_NAME.azurecr.io"
    echo "Backend Image: $BACKEND_IMAGE"
    echo "Frontend Image: $FRONTEND_IMAGE"
    echo ""

    # Get service information
    echo -e "${GREEN}Services:${NC}"
    kubectl get services -n todoapp

    echo ""
    echo -e "${GREEN}Deployments:${NC}"
    kubectl get deployments -n todoapp

    echo ""
    echo -e "${GREEN}Pods:${NC}"
    kubectl get pods -n todoapp

    # Get external IP if using LoadBalancer
    echo ""
    echo -e "${GREEN}External Access:${NC}"

    # Wait a bit for load balancer to provision
    print_status "Waiting for LoadBalancer IPs to be provisioned (this may take a few minutes)..."
    sleep 10

    FRONTEND_IP=$(kubectl get svc frontend-service -n todoapp -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    BACKEND_IP=$(kubectl get svc backend-service -n todoapp -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

    echo "Frontend External IP: ${FRONTEND_IP:-pending}"
    echo "Backend External IP: ${BACKEND_IP:-pending}"
    echo ""

    echo "To access the application:"
    echo "  Frontend: http://${FRONTEND_IP:-PENDING}:3000"
    echo "  Backend: http://${BACKEND_IP:-PENDING}:8000"
    echo ""

    echo "Note: It may take 5-10 minutes for the LoadBalancer IPs to become available."
    echo "You can check the status with: kubectl get svc -n todoapp"
    echo ""

    echo -e "${GREEN}Deployment completed successfully!${NC}"
}

# Main execution flow
main() {
    print_status "Starting Azure deployment for Todoapp..."

    # Step 1: Check prerequisites
    check_prerequisites

    # Step 2: Login to Azure
    login_to_azure

    # Step 3: Setup resource group
    setup_resource_group

    # Step 4: Setup ACR
    setup_acr

    # Step 5: Setup AKS
    setup_aks

    # Step 6: Configure kubectl
    configure_kubectl

    # Step 7: Build and push images
    build_and_push_images

    # Step 8: Update deployment files
    update_deployment_files

    # Step 9: Deploy to AKS
    deploy_to_aks

    # Step 10: Show access information
    show_access_info

    print_status "Azure deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Wait for LoadBalancer IPs to become available (may take 5-10 minutes)"
    echo "2. Check status: kubectl get svc -n todoapp"
    echo "3. Access your application using the external IPs shown above"
    echo "4. Monitor the application using Azure portal: https://portal.azure.com"
}

# Run the main function
main "$@"