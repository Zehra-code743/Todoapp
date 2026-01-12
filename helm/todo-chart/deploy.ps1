# Kubernetes Deployment Script for Todo AI Chatbot
# Run this script after starting Minikube and building Docker images

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Todo AI Chatbot Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Minikube is running
Write-Host "[1/6] Checking Minikube status..." -ForegroundColor Yellow
$minikubeStatus = minikube status
if ($minikubeStatus -match "Running") {
    Write-Host "Minikube is running" -ForegroundColor Green
} else {
    Write-Host "ERROR: Minikube is not running. Start it with: minikube start --cpus=4 --memory=8192" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check if images exist
Write-Host "[2/6] Checking Docker images..." -ForegroundColor Yellow
$frontendImage = docker images --format "{{.Repository}}:{{.Tag}}" | Select-String "todo-frontend:local"
$backendImage = docker images --format "{{.Repository}}:{{.Tag}}" | Select-String "todo-backend:local"

if (-not $frontendImage) {
    Write-Host "WARNING: todo-frontend:local image not found" -ForegroundColor Yellow
    Write-Host "Build it with: cd frontend; docker build -t todo-frontend:local -f Dockerfile ." -ForegroundColor Gray
}

if (-not $backendImage) {
    Write-Host "WARNING: todo-backend:local image not found" -ForegroundColor Yellow
    Write-Host "Build it with: cd backend; docker build -t todo-backend:local -f Dockerfile ." -ForegroundColor Gray
}
Write-Host ""

# Load images into Minikube
Write-Host "[3/6] Loading images into Minikube..." -ForegroundColor Yellow
if ($frontendImage) { minikube image load todo-frontend:local }
if ($backendImage) { minikube image load todo-backend:local }
Write-Host "Images loaded" -ForegroundColor Green
Write-Host ""

# Check if secret exists
Write-Host "[4/6] Checking Kubernetes secrets..." -ForegroundColor Yellow
$secretExists = kubectl get secret todo-secrets -ErrorAction SilentlyContinue
if (-not $secretExists) {
    Write-Host "WARNING: todo-secrets not found" -ForegroundColor Yellow
    Write-Host "Create it manually:" -ForegroundColor Gray
    Write-Host "kubectl create secret generic todo-secrets \"`" -ForegroundColor Gray
    Write-Host "  --from-literal=database-url='postgresql://...' \"`" -ForegroundColor Gray
    Write-Host "  --from-literal=openai-api-key='sk-...' \"`" -ForegroundColor Gray
    Write-Host "  --from-literal=jwt-secret='your-jwt-secret' \"`" -ForegroundColor Gray
    Write-Host "  --from-literal=better-auth-secret='your-better-auth-secret'" -ForegroundColor Gray
}
Write-Host ""

# Install or upgrade Helm chart
Write-Host "[5/6] Installing Helm chart..." -ForegroundColor Yellow
$releaseExists = helm list | Select-String "todo-app"
if (-not $releaseExists) {
    Write-Host "Installing todo-app for the first time..." -ForegroundColor Gray
    helm install todo-app ./helm/todo-chart --values helm/todo-chart/values-local.yaml
} else {
    Write-Host "Upgrading existing todo-app deployment..." -ForegroundColor Gray
    helm upgrade todo-app ./helm/todo-chart --values helm/todo-chart/values-local.yaml
}
Write-Host ""

# Verify deployment
Write-Host "[6/6] Verifying deployment..." -ForegroundColor Yellow
Write-Host "Waiting for pods to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 15
kubectl get pods
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the application:" -ForegroundColor White
Write-Host "  minikube service todo-app-frontend --url" -ForegroundColor Cyan
Write-Host ""
Write-Host "View logs:" -ForegroundColor White
Write-Host "  kubectl logs -l app=todo-app-backend" -ForegroundColor Cyan
Write-Host "  kubectl logs -l app=todo-app-frontend" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check pod status:" -ForegroundColor White
Write-Host "  kubectl get pods -w" -ForegroundColor Cyan
Write-Host ""
