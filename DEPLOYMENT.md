# Deployment Guide for Todoapp

This guide explains how to deploy the Todoapp application to Kubernetes using the provided deployment scripts.

## Prerequisites

Before deploying, ensure you have the following installed:

- [kubectl](https://kubernetes.io/docs/tasks/tools/) - Kubernetes command-line tool
- [git](https://git-scm.com/) - Version control system
- [Docker](https://www.docker.com/) - Container platform
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) - Local Kubernetes environment (for local deployment)
- [Helm](https://helm.sh/docs/intro/install/) (optional) - Package manager for Kubernetes

## Deployment Scripts

Three deployment scripts are provided for different environments:

1. **deploy.sh** - For Linux/macOS environments
2. **deploy.ps1** - For PowerShell on Windows
3. **deploy.bat** - For Command Prompt on Windows

## Usage

### For Linux/macOS:

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

### For Windows (PowerShell):

```powershell
# Run the deployment (make sure to run as Administrator if needed)
.\deploy.ps1
```

### For Windows (Command Prompt):

```cmd
# Run the deployment (run as Administrator if needed)
deploy.bat
```

## What the Script Does

The deployment script performs the following actions:

1. Pulls the latest code from the GitHub repository
2. Sets up the Docker environment (assumes Minikube is running)
3. Builds Docker images for the backend and frontend applications
4. Applies Kubernetes configurations in the following order:
   - Namespace (`todoapp`)
   - PostgreSQL database
   - Kafka (if available)
   - Backend service
   - Frontend service
   - Ingress (if available)
5. Waits for all deployments to be ready
6. Displays deployment summary with service information

## Before Running the Script

Make sure you have:

1. Started Minikube (if deploying locally):
   ```bash
   minikube start
   ```

2. Have the necessary Kubernetes secrets configured (database credentials, etc.)

3. Verified that all required Docker images are available or can be built from the source

## Troubleshooting

- If the script fails during image building, make sure Docker is running and you have sufficient disk space
- If deployments fail to become ready, check the pod logs with:
  ```bash
  kubectl get pods -n todoapp
  kubectl logs <pod-name> -n todoapp
  ```
- If you encounter permission issues on Windows, try running the command prompt or PowerShell as Administrator

## Environment Configuration

The script assumes the following:

- Minikube is used as the Kubernetes cluster
- The application uses PostgreSQL as the database
- The application uses Kafka for messaging (optional)
- Services are exposed via LoadBalancer type (adjust as needed for your environment)

## Accessing the Application

After successful deployment, the script will display the external IP addresses for the frontend and backend services. You can access:

- Frontend: `http://<frontend-ip>:3000`
- Backend: `http://<backend-ip>:8000`

For local Minikube deployments, you might need to use `minikube tunnel` to expose LoadBalancer services.