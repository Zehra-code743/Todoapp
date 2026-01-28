@echo off
REM Batch Deployment Script for Todoapp to Kubernetes
REM This script pulls the latest changes from GitHub and deploys to Kubernetes

echo Starting deployment process...

REM Check if kubectl is installed
where kubectl >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: kubectl is not installed. Please install kubectl first.
    exit /b 1
)

REM Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: git is not installed. Please install git first.
    exit /b 1
)

echo INFO: kubectl and git are installed

REM Pull the latest changes from GitHub
echo INFO: Pulling latest changes from GitHub...
git pull origin main
if %errorlevel% neq 0 (
    REM If main fails, try master
    git pull origin master
    if %errorlevel% neq 0 (
        echo ERROR: Failed to pull from GitHub
        exit /b 1
    )
)

echo INFO: Successfully pulled latest changes

REM Set Docker environment to Minikube
echo INFO: Setting Docker environment to Minikube...
for /f %%i in ('minikube -p minikube docker-env --shell cmd ^| findstr SET') do @%%i

REM Build Docker images
echo INFO: Building Docker images...
call build_images.sh
if %errorlevel% neq 0 (
    echo ERROR: Failed to build Docker images
    exit /b 1
)

echo INFO: Docker images built successfully

REM Apply Kubernetes configurations
echo INFO: Deploying to Kubernetes...

REM Create namespace if it doesn't exist
kubectl apply -f k8s/namespace.yaml

REM Apply PostgreSQL deployment
kubectl apply -f k8s/postgresql.yaml

REM Wait for PostgreSQL to be ready
echo INFO: Waiting for PostgreSQL to be ready...
kubectl rollout status deployment/postgres-deployment -n todoapp --timeout=120s

REM Apply Kafka if available
if exist "k8s\kafka\kafka-full.yaml" (
    kubectl apply -f k8s/kafka/kafka-full.yaml
    echo INFO: Waiting for Kafka to be ready...
    kubectl rollout status deployment/kafka-deployment -n todoapp --timeout=180s || echo WARNING: Kafka may take longer to start...
)

REM Apply backend deployment
kubectl apply -f k8s/deployments/backend-deployment.yaml

REM Wait for backend to be ready
echo INFO: Waiting for backend to be ready...
kubectl rollout status deployment/backend-deployment -n todoapp --timeout=120s

REM Apply frontend deployment
kubectl apply -f k8s/deployments/frontend-deployment.yaml

REM Wait for frontend to be ready
echo INFO: Waiting for frontend to be ready...
kubectl rollout status deployment/frontend-deployment -n todoapp --timeout=120s

REM Apply ingress if available
if exist "k8s\ingress\todo-app-ingress.yaml" (
    kubectl apply -f k8s/ingress/todo-app-ingress.yaml
)

REM Get service information
echo INFO: Deployment completed! Service information:
kubectl get services -n todoapp

REM Get pod status
echo INFO: Pod status:
kubectl get pods -n todoapp

echo INFO: Deployment script completed successfully!

echo.
echo === DEPLOYMENT SUMMARY ===
echo Namespace: todoapp
echo.
echo To check service status run: kubectl get services -n todoapp
echo To check pod status run: kubectl get pods -n todoapp