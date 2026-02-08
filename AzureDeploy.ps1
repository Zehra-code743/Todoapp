# Azure Deployment Script for Todoapp
# Targeted for Azure Container Apps (Cost-effective and Modern)

$ErrorActionPreference = "Stop"

# Configuration
$RESOURCE_GROUP = "todoapp-resources"
$LOCATION = "eastus"
$ACR_NAME = "todoappregistry" + (Get-Date -Format "yyyyMMddHHmm")
$ENVIRONMENT_NAME = "todoapp-env"
$BACKEND_APP_NAME = "todo-backend"
$FRONTEND_APP_NAME = "todo-frontend"

function Print-Status {
    param($msg)
    Write-Host "`n[INFO] $msg" -ForegroundColor Green
}

function Print-Error {
    param($msg)
    Write-Host "`n[ERROR] $msg" -ForegroundColor Red
}

try {
    # 1. Check Azure CLI
    Print-Status "Checking Azure CLI..."
    if (!(Get-Command az -ErrorAction SilentlyContinue)) {
        Print-Error "Azure CLI (az) is not installed. Please install it from https://aka.ms/installazurecliwindows"
        return
    }

    # 2. Azure Login
    Print-Status "Checking Azure Authentication..."
    $account = az account show --query name -o tsv 2>$null
    if ($null -eq $account) {
        Print-Status "Please log in to Azure in the browser window that opens..."
        az login --use-device-code
    } else {
        Print-Status "Already logged in as $account"
    }

    # 3. Register Resource Providers (Required for new subscriptions)
    Print-Status "Ensuring Azure Resource Providers are registered..."
    az provider register -n Microsoft.ContainerRegistry
    az provider register -n Microsoft.OperationalInsights
    az provider register -n Microsoft.App
    
    # 4. Create Resource Group
    Print-Status "Creating Resource Group: $RESOURCE_GROUP..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
    if ($LASTEXITCODE -ne 0) { throw "Failed to create resource group" }

    # 5. Create Container Registry
    Print-Status "Creating Azure Container Registry: $ACR_NAME (this might take a minute)..."
    az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
    if ($LASTEXITCODE -ne 0) { throw "Failed to create Azure Container Registry. If this is a new subscription, it might take a few minutes for the provider registration to complete. Please try again in 2-3 minutes." }
    
    $ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --query loginServer -o tsv
    if ($LASTEXITCODE -ne 0) { throw "Failed to get ACR login server" }

    # 6. Build and Push Backend Image
    Print-Status "Building and Pushing Backend Image..."
    az acr build --registry $ACR_NAME --image "$($BACKEND_APP_NAME):latest" --file backend/Dockerfile .
    if ($LASTEXITCODE -ne 0) { throw "Failed to build/push backend image" }

    # 7. Create Container App Environment
    Print-Status "Creating Container App Environment..."
    az containerapp env create --name $ENVIRONMENT_NAME --resource-group $RESOURCE_GROUP --location $LOCATION
    if ($LASTEXITCODE -ne 0) { throw "Failed to create Container App environment" }

    # 8. Deploy Backend Container App
    Print-Status "Deploying Backend Container App..."
    $ACR_PASSWORD = az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv
    
    $DATABASE_URL = "sqlite:///./todoapp.db"
    
    az containerapp create `
        --name $BACKEND_APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --environment $ENVIRONMENT_NAME `
        --image "$ACR_LOGIN_SERVER/$($BACKEND_APP_NAME):latest" `
        --target-port 8000 `
        --ingress external `
        --registry-server $ACR_LOGIN_SERVER `
        --registry-user $ACR_NAME `
        --registry-password $ACR_PASSWORD `
        --env-vars "DATABASE_URL=$DATABASE_URL" "BETTER_AUTH_SECRET=todoapp-phase2-jwt-secret-key-2025-very-secure-32ch" "PORT=8000" "ENV=production"
    if ($LASTEXITCODE -ne 0) { throw "Failed to deploy backend app" }

    $BACKEND_URL = az containerapp show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv
    $BACKEND_URL = "https://$BACKEND_URL"
    Print-Status "Backend deployed at: $BACKEND_URL"

    # 9. Build and Push Frontend Image
    Print-Status "Building and Pushing Frontend Image with Backend URL: $BACKEND_URL..."
    az acr build --registry $ACR_NAME --image "$($FRONTEND_APP_NAME):latest" --file frontend/Dockerfile --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL .
    if ($LASTEXITCODE -ne 0) { throw "Failed to build/push frontend image" }

    # 10. Deploy Frontend Container App
    Print-Status "Deploying Frontend Container App..."
    az containerapp create `
        --name $FRONTEND_APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --environment $ENVIRONMENT_NAME `
        --image "$ACR_LOGIN_SERVER/$($FRONTEND_APP_NAME):latest" `
        --target-port 3000 `
        --ingress external `
        --registry-server $ACR_LOGIN_SERVER `
        --registry-user $ACR_NAME `
        --registry-password $ACR_PASSWORD `
        --env-vars "NEXT_PUBLIC_API_URL=$BACKEND_URL" "PORT=3000"
    if ($LASTEXITCODE -ne 0) { throw "Failed to deploy frontend app" }

    $FRONTEND_URL = az containerapp show --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv
    $FRONTEND_URL = "https://$FRONTEND_URL"

    # 11. Update Backend CORS
    Print-Status "Updating Backend CORS with Frontend URL: $FRONTEND_URL..."
    az containerapp update `
        --name $BACKEND_APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --set-env-vars "CORS_ORIGINS=$FRONTEND_URL,http://localhost:3000"
    if ($LASTEXITCODE -ne 0) { throw "Failed to update backend CORS" }

    Print-Status "SUCCESS! Deployment Complete."
    Print-Status "Frontend URL: $FRONTEND_URL"
    Print-Status "Backend URL: $BACKEND_URL"
    Print-Status "Note: Backend is currently using a non-persistent SQLite database. Please update the DATABASE_URL secret in Azure Portal for production use."

} catch {
    Print-Error $_.Exception.Message
}
