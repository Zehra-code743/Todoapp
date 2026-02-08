# Azure Setup and Deployment Instructions for Todoapp

This guide will help you deploy your Todoapp frontend and backend to Microsoft Azure.
We'll use Azure Kubernetes Service (AKS) to host your application.

## Prerequisites

1. Azure account with email: shanezehra117@gmail.com
2. Azure CLI installed
3. kubectl installed
4. Docker installed

## Steps to deploy

### Step 1: Make the deployment script executable
```bash
chmod +x deploy_to_azure.sh
```

### Step 2: Run the deployment script
```bash
./deploy_to_azure.sh
```

### Step 3: Follow the interactive prompts to:
- Select your Azure subscription
- Create/confirm resource group
- Create/confirm Azure Container Registry (ACR)
- Create/confirm Azure Kubernetes Service (AKS)
- Build and push Docker images to ACR
- Deploy the application to AKS

### Step 4: Wait for deployment to complete
- The script will show you the external IPs when ready
- This may take 10-15 minutes for the first time

### Step 5: Access your application
- Frontend: http://<FRONTEND_IP>:3000
- Backend: http://<BACKEND_IP>:8000

## Additional files created for your reference:

- `AZURE_DEPLOYMENT_GUIDE.md`: Complete manual setup guide
- `setup_azure_deployment.sh`: Alternative setup script
- `deploy_to_azure.sh`: Main deployment script
- `azure-k8s-configs/`: Updated Kubernetes configurations for Azure
- `update_acr_references.sh`: Script to update ACR references

## Troubleshooting

- If you encounter issues, check the Azure portal: https://portal.azure.com
- Use `kubectl get pods -n todoapp` to check pod status
- Use `kubectl logs <pod-name> -n todoapp` to check logs

## Cleanup (when done)

- To remove all resources: `az group delete --name todoapp-rg --yes --no-wait`

---

Ready to begin deployment? Run: `./deploy_to_azure.sh`