# Azure App Service Deployment Script for Todoapp
# (Free Tier Version - No Quota Required)

$ErrorActionPreference = "Stop"

# Configuration
$RESOURCE_GROUP = "todoapp-free-resources"
$LOCATION = "eastus" # Try East US
$BACKEND_NAME = "todo-backend-" + (Get-Date -Format "yyyyMMddHHmm")
$FRONTEND_NAME = "todo-frontend-" + (Get-Date -Format "yyyyMMddHHmm")
$PLAN_NAME = "todo-free-plan"

function Print-Status {
    param($msg)
    Write-Host "`n[INFO] $msg" -ForegroundColor Green
}

function Print-Error {
    param($msg)
    Write-Host "`n[ERROR] $msg" -ForegroundColor Red
}

try {
    # 1. Login Check
    Print-Status "Checking Azure Authentication..."
    $account = az account show --query name -o tsv 2>$null
    if ($null -eq $account) {
        az login --use-device-code
    }

    # 2. Register Providers (Required for Web/App)
    Print-Status "Ensuring Resource Providers are registered..."
    az provider register -n Microsoft.Web --wait
    Start-Sleep -Seconds 10

    # 3. Create Resource Group
    Print-Status "Creating Resource Group: $RESOURCE_GROUP..."
    az group create --name $RESOURCE_GROUP --location $LOCATION

    # 4. Deploy Backend (FastAPI)
    Print-Status "Deploying Backend to Azure Web App (Free Tier)..."
    Set-Location -Path "d:\Todoapp\backend"
    
    # Using F1 (Free) SKU to avoid quota issues
    az webapp up `
        --name $BACKEND_NAME `
        --resource-group $RESOURCE_GROUP `
        --plan $PLAN_NAME `
        --sku F1 `
        --runtime "PYTHON:3.11" `
        --location $LOCATION

    # Set Startup Command for FastAPI
    az webapp config set `
        --name $BACKEND_NAME `
        --resource-group $RESOURCE_GROUP `
        --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app"

    $BACKEND_URL = "https://$BACKEND_NAME.azurewebsites.net"
    Print-Status "Backend deployed at: $BACKEND_URL"

    # Set Backend App Settings
    az webapp config appsettings set `
        --name $BACKEND_NAME `
        --resource-group $RESOURCE_GROUP `
        --settings "DATABASE_URL=sqlite:///./todoapp.db" "BETTER_AUTH_SECRET=todoapp-phase2-jwt-secret-key-2025-very-secure-32ch" "PORT=80" "ENV=production"

    # 5. Deploy Frontend (Next.js)
    Print-Status "Deploying Frontend to Azure Web App (Free Tier)..."
    Set-Location -Path "d:\Todoapp\frontend"
    
    # Using NODE:20-lts
    az webapp up `
        --name $FRONTEND_NAME `
        --resource-group $RESOURCE_GROUP `
        --plan $PLAN_NAME `
        --sku F1 `
        --runtime "NODE:20-lts" `
        --location $LOCATION

    # Set Startup Command for Next.js
    az webapp config set `
        --name $FRONTEND_NAME `
        --resource-group $RESOURCE_GROUP `
        --startup-file "npm run build && npm run start"

    $FRONTEND_URL = "https://$FRONTEND_NAME.azurewebsites.net"
    Print-Status "Frontend deployed at: $FRONTEND_URL"

    # Set Frontend App Settings
    az webapp config appsettings set `
        --name $FRONTEND_NAME `
        --resource-group $RESOURCE_GROUP `
        --settings "NEXT_PUBLIC_API_URL=$BACKEND_URL"

    # 6. Update Backend CORS
    Print-Status "Updating Backend CORS with Frontend URL..."
    az webapp config appsettings set `
        --name $BACKEND_NAME `
        --resource-group $RESOURCE_GROUP `
        --settings "CORS_ORIGINS=$FRONTEND_URL,http://localhost:3000"

    Print-Status "SUCCESS! Deployment Complete."
    Print-Status "Frontend URL: $FRONTEND_URL"
    Print-Status "Backend URL: $BACKEND_URL"

} catch {
    Print-Error $_.Exception.Message
} finally {
    Set-Location -Path "d:\Todoapp"
}
