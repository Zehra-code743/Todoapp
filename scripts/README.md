# Scripts Directory

This directory contains helper scripts for setting up and deploying the Todo AI Chatbot application to Kubernetes.

---

## Installation Scripts

### install-k8s-tools.ps1
**Purpose**: Automatically installs Chocolatey, Minikube, and Helm on Windows

**Usage**:
```powershell
# Run as Administrator
.\install-k8s-tools.ps1
```

**What it does**:
1. Checks if Chocolatey is installed, installs if missing
2. Installs Minikube via Chocolatey
3. Installs Helm via Chocolatey
4. Verifies all installations (Docker, Minikube, kubectl, Helm)
5. Optionally starts Minikube

**Requirements**:
- Windows 10/11
- PowerShell (run as Administrator)
- Internet connection

---

## Deployment Scripts

### helm/todo-chart/deploy.bat
**Purpose**: Windows batch script for deploying to Kubernetes

**Usage**:
```cmd
cd helm/todo-chart
deploy.bat
```

### helm/todo-chart/deploy.ps1
**Purpose**: PowerShell script for deploying to Kubernetes (more feature-rich)

**Usage**:
```powershell
cd helm/todo-chart
.\deploy.ps1
```

**What both scripts do**:
1. Check if Minikube is running
2. Check if Docker images exist
3. Load images into Minikube
4. Check if Kubernetes secrets exist
5. Install or upgrade Helm chart
6. Verify deployment status

---

## Prerequisites

Before running any deployment script, ensure:

1. **Docker Desktop** is installed and running
   - Download from: https://www.docker.com/products/docker-desktop/

2. **Minikube is installed**
   - Run: `.\install-k8s-tools.ps1` (as Administrator)
   - Or: `choco install minikube`

3. **Helm is installed**
   - Run: `.\install-k8s-tools.ps1` (as Administrator)
   - Or: `choco install kubernetes-helm`

4. **Minikube is started**
   ```powershell
   minikube start --cpus=4 --memory=8192 --disk-size=20g
   ```

5. **Docker images are built**
   ```powershell
   cd frontend
   docker build -t todo-frontend:local -f Dockerfile .

   cd ..\backend
   docker build -t todo-backend:local -f Dockerfile .
   ```

6. **Kubernetes secrets are configured**
   ```powershell
   kubectl create secret generic todo-secrets `
     --from-literal=database-url="postgresql://..." `
     --from-literal=openai-api-key="sk-..." `
     --from-literal=jwt-secret="your-secret" `
     --from-literal=better-auth-secret="your-secret"
   ```

---

## Quick Start

### First-Time Setup

```powershell
# 1. Install Kubernetes tools (run as Administrator)
.\install-k8s-tools.ps1

# 2. Close and reopen PowerShell to refresh PATH

# 3. Start Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g

# 4. Build Docker images
cd frontend
docker build -t todo-frontend:local -f Dockerfile .

cd ..\backend
docker build -t todo-backend:local -f Dockerfile .

# 5. Deploy to Kubernetes
cd ..\helm\todo-chart
.\deploy.ps1
```

### Subsequent Deployments

After the first setup:

```powershell
# 1. Start Minikube (if not running)
minikube start

# 2. Build and deploy
cd frontend
docker build -t todo-frontend:local -f Dockerfile .

cd ..\backend
docker build -t todo-backend:local -f Dockerfile .

cd ..\helm\todo-chart
.\deploy.ps1
```

---

## Troubleshooting

### Script Execution Errors

**"This script must be run as Administrator"**
- Right-click PowerShell and select "Run as Administrator"

**"choco is not recognized"**
- Close and reopen PowerShell to refresh PATH
- Or manually refresh: `$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")`

### Docker Issues

**"Docker daemon is not running"**
- Start Docker Desktop from the Start menu
- Check status in system tray

**Image build fails**
- Check Docker Desktop has sufficient disk space
- Check Docker Desktop is using WSL 2 backend

### Minikube Issues

**"minikube is not running"**
```powershell
minikube start --cpus=4 --memory=8192 --disk-size=20g
```

**"The system cannot find the file specified"**
- Close and reopen PowerShell to refresh PATH
- Verify installation: `minikube --version`

**Minikube start fails**
- Check Hyper-V is enabled: `Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All`
- Check virtualization is enabled in BIOS
- Try alternative driver: `minikube start --driver=hyperv`

### Helm Issues

**"helm is not recognized"**
- Close and reopen PowerShell to refresh PATH
- Verify installation: `helm version`

**"Error: failed to download"**
- Check internet connection
- Try adding repository: `helm repo add bitnami https://charts.bitnami.com/bitnami`

### Kubernetes Deployment Issues

**Pods stuck in Pending**
```powershell
kubectl describe pod <pod-name>
minikube status
```

**Pods in CrashLoopBackOff**
```powershell
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

**Service not accessible**
```powershell
kubectl get services
minikube service todo-app-frontend --url

# Try port forwarding
kubectl port-forward service/todo-app-frontend 3000:80
```

**Secrets not found**
```powershell
kubectl get secrets
kubectl create secret generic todo-secrets --from-env-file=backend\.env
```

---

## Additional Resources

- **Developer Guide**: `helm/todo-chart/DEVELOPER_GUIDE.md`
- **Implementation Status**: `specs/004-kubernetes-deployment/IMPLEMENTATION_STATUS.md`
- **Minikube Docs**: https://minikube.sigs.k8s.io/docs/
- **Helm Docs**: https://helm.sh/docs/
- **Kubernetes Docs**: https://kubernetes.io/docs/

---

## AI DevOps Tools

### kubectl-ai
```powershell
# Install via krew
kubectl krew install kubectl-ai

# Use for troubleshooting
kubectl-ai "why are my pods failing?"
```

### kagent
```powershell
# Analyze cluster health
kagent "analyze cluster health"

# Check performance
kagent "check backend performance"
```

### Docker AI (Gordon)
Enable in Docker Desktop > Settings > Beta Features

```powershell
# Optimize Dockerfile
docker ai "optimize my dockerfile for production"

# Check image size
docker ai "why is my image so large?"
```

---

## Support

For issues or questions:
1. Check this README for common solutions
2. Review `helm/todo-chart/DEVELOPER_GUIDE.md`
3. Check pod logs: `kubectl logs <pod-name>`
4. Use AI tools: `kubectl-ai "troubleshoot deployment"`
