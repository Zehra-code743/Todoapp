#!/bin/bash
# Build script for Todoapp Docker images

# Set Docker environment for Minikube
eval $(minikube -p minikube docker-env --shell bash)

echo "Building backend image..."
docker build -t todo-task-service:latest -f backend/Dockerfile .

if [ $? -eq 0 ]; then
    echo "Backend image built successfully!"
else
    echo "Failed to build backend image"
    exit 1
fi

echo "Building frontend image..."
docker build -t todo-frontend:latest -f frontend/Dockerfile .

if [ $? -eq 0 ]; then
    echo "Frontend image built successfully!"
else
    echo "Failed to build frontend image"
    exit 1
fi

echo "Listing built images:"
docker images | grep todo