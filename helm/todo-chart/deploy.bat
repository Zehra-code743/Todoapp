@echo off
REM Kubernetes Deployment Script for Todo AI Chatbot
REM Run this script after starting Minikube and building Docker images

echo ========================================
echo Todo AI Chatbot Deployment Script
echo ========================================
echo.

REM Check if Minikube is running
echo [1/6] Checking Minikube status...
minikube status
if errorlevel 1 (
    echo ERROR: Minikube is not running. Start it with: minikube start --cpus=4 --memory=8192
    exit /b 1
)
echo Minikube is running
echo.

REM Check if images exist
echo [2/6] Checking Docker images...
docker images | findstr "todo-frontend"
if errorlevel 1 (
    echo WARNING: todo-frontend:local image not found
    echo Build it with: cd frontend && docker build -t todo-frontend:local -f Dockerfile .
)
docker images | findstr "todo-backend"
if errorlevel 1 (
    echo WARNING: todo-backend:local image not found
    echo Build it with: cd backend && docker build -t todo-backend:local -f Dockerfile .
)
echo.

REM Load images into Minikube
echo [3/6] Loading images into Minikube...
minikube image load todo-frontend:local
minikube image load todo-backend:local
echo Images loaded
echo.

REM Check if secret exists
echo [4/6] Checking Kubernetes secrets...
kubectl get secret todo-secrets
if errorlevel 1 (
    echo WARNING: todo-secrets not found
    echo Create it manually:
    echo kubectl create secret generic todo-secrets ^
    echo   --from-literal=database-url="postgresql://..." ^
    echo   --from-literal=openai-api-key="sk-..." ^
    echo   --from-literal=jwt-secret="your-jwt-secret" ^
    echo   --from-literal=better-auth-secret="your-better-auth-secret"
    echo.
)
echo.

REM Install or upgrade Helm chart
echo [5/6] Installing Helm chart...
helm list | findstr "todo-app"
if errorlevel 1 (
    echo Installing todo-app for the first time...
    helm install todo-app ./helm/todo-chart --values helm/todo-chart/values-local.yaml
) else (
    echo Upgrading existing todo-app deployment...
    helm upgrade todo-app ./helm/todo-chart --values helm/todo-chart/values-local.yaml
)
echo.

REM Verify deployment
echo [6/6] Verifying deployment...
echo Waiting for pods to be ready...
timeout /t 30
kubectl get pods
echo.

echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Access the application:
echo   minikube service todo-app-frontend --url
echo.
echo View logs:
echo   kubectl logs -l app=todo-app-backend
echo   kubectl logs -l app=todo-app-frontend
echo.
echo Check pod status:
echo   kubectl get pods -w
echo.
