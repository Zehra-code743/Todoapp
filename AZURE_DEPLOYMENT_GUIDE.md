# Azure Deployment Guide for Todoapp

This guide will walk you through deploying your Todoapp frontend and backend to Microsoft Azure using Azure Kubernetes Service (AKS).

## Prerequisites

1. **Azure Account**: You need an Azure account with the email `shanezehra117@gmail.com` that you've already created.
2. **Azure CLI**: The Azure command-line interface tool.
3. **kubectl**: Kubernetes command-line tool.
4. **Docker**: For building container images.
5. **Git**: For pulling the latest code.

## Setup Process

### Step 1: Install Azure CLI

If you don't have Azure CLI installed, run the setup script:

```bash
chmod +x setup_azure_deployment.sh
./setup_azure_deployment.sh
```

This script will:
- Check if Azure CLI is installed (and install if needed)
- Log you into Azure using device code authentication
- Help you select your subscription
- Create an Azure Resource Group
- Create an Azure Container Registry (ACR)
- Create an Azure Kubernetes Service (AKS) cluster
- Configure kubectl to connect to your AKS cluster
- Build and push Docker images to ACR
- Deploy your Todoapp to AKS

### Step 2: Manual Setup (Alternative to script)

If you prefer to set up manually, follow these steps:

#### 2.1: Install Azure CLI

**For Ubuntu/Debian:**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**For macOS:**
```bash
brew install azure-cli
```

**For Windows:**
Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

#### 2.2: Login to Azure
```bash
az login --use-device-code
```
Use your email: `shanezehra117@gmail.com`

#### 2.3: Set Subscription
```bash
az account list -o table
az account set --subscription <your-subscription-id>
```

#### 2.4: Create Resource Group
```bash
RESOURCE_GROUP_NAME="todoapp-rg"
LOCATION="EastUS"
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION
```

#### 2.5: Create Container Registry
```bash
ACR_NAME="todoappregistry$(date +%s)"
az acr create --resource-group $RESOURCE_GROUP_NAME --name $ACR_NAME --sku Basic
```

#### 2.6: Create AKS Cluster
```bash
AKS_CLUSTER_NAME="todoapp-aks"
az aks create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $AKS_CLUSTER_NAME \
    --node-count 2 \
    --enable-addons monitoring \
    --generate-ssh-keys \
    --attach-acr $ACR_NAME
```

#### 2.7: Configure kubectl
```bash
az aks get-credentials --resource-group $RESOURCE_GROUP_NAME --name $AKS_CLUSTER_NAME
kubectl get nodes
```

#### 2.8: Build and Push Images
```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build and tag images
docker build -t todo-backend:latest -f backend/Dockerfile .
docker tag todo-backend:latest $ACR_NAME.azurecr.io/todo-backend:latest

docker build -t todo-frontend:latest -f frontend/Dockerfile .
docker tag todo-frontend:latest $ACR_NAME.azurecr.io/todo-frontend:latest

# Push images
docker push $ACR_NAME.azurecr.io/todo-backend:latest
docker push $ACR_NAME.azurecr.io/todo-frontend:latest
```

#### 2.9: Deploy to AKS

First, update the deployment files to use your ACR images:

In `k8s/deployments/backend-deployment.yaml`:
```yaml
spec:
  containers:
  - name: backend
    image: <ACR_NAME>.azurecr.io/todo-backend:latest  # Replace <ACR_NAME>
```

In `k8s/deployments/frontend-deployment.yaml`:
```yaml
spec:
  containers:
  - name: frontend
    image: <ACR_NAME>.azurecr.io/todo-frontend:latest  # Replace <ACR_NAME>
```

Then deploy:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgresql.yaml
kubectl apply -f k8s/deployments/backend-deployment.yaml
kubectl apply -f k8s/deployments/frontend-deployment.yaml
kubectl apply -f k8s/ingress/todo-app-ingress.yaml
```

## Verifying the Deployment

Check if all pods are running:
```bash
kubectl get pods -n todoapp
```

Check services:
```bash
kubectl get services -n todoapp
```

Get the external IP of your services:
```bash
kubectl get svc frontend-service -n todoapp
kubectl get svc backend-service -n todoapp
```

## Accessing Your Application

Once the LoadBalancer services have external IPs (may take a few minutes), you can access:

- Frontend: `http://<FRONTEND_EXTERNAL_IP>:3000`
- Backend: `http://<BACKEND_EXTERNAL_IP>:8000`

## Troubleshooting

### Common Issues:

1. **ImagePullBackOff Error**: Check if your ACR images are properly tagged and pushed
2. **LoadBalancer Pending**: May take 5-10 minutes for Azure to provision external IPs
3. **Service Unavailable**: Check pod logs with `kubectl logs <pod-name> -n todoapp`

### Useful Commands:

```bash
# Check pod logs
kubectl logs -f <pod-name> -n todoapp

# Check pod status
kubectl describe pod <pod-name> -n todoapp

# Execute commands inside a pod
kubectl exec -it <pod-name> -n todoapp -- /bin/sh

# Scale deployments
kubectl scale deployment backend-deployment -n todoapp --replicas=3
```

## Scaling and Maintenance

### Scaling Applications:
```bash
kubectl scale deployment backend-deployment -n todoapp --replicas=3
kubectl scale deployment frontend-deployment -n todoapp --replicas=3
```

### Updating Applications:
1. Build and push new images to ACR
2. Update the image tag in your deployment files
3. Apply the updated configurations:
```bash
kubectl apply -f k8s/deployments/backend-deployment.yaml
kubectl apply -f k8s/deployments/frontend-deployment.yaml
```

### Monitoring:
Access Azure Portal to monitor your AKS cluster, view logs, and manage resources.

## Cleanup

To remove all resources when no longer needed:
```bash
az group delete --name todoapp-rg --yes --no-wait
```

This will delete the entire resource group and all associated resources.