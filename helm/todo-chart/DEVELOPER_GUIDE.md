# Kubernetes Development Guide

**Feature**: 004-kubernetes-deployment
**Updated**: 2026-01-06

---

## Quick Start

### Windows Batch
```cmd
cd helm/todo-chart
deploy.bat
```

### Windows PowerShell
```powershell
cd helm/todo-chart
.\deploy.ps1
```

---

## Prerequisites

1. **Docker Desktop** - Download from [docker.com](https://www.docker.com/products/docker-desktop/)
2. **Minikube** - `choco install minikube` (requires Chocolatey)
3. **Helm** - `choco install kubernetes-helm`
4. **kubectl** - `choco install kubernetes-cli`
5. **Minimum Resources**: 4 CPU, 8GB RAM

---

## Common Commands

### Minikube

```bash
# Start cluster
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Check status
minikube status

# Stop cluster
minikube stop

# Delete cluster
minikube delete

# Get service URL
minikube service todo-app-frontend --url

# Open service in browser (Windows)
start $(minikube service todo-app-frontend --url)

# Open Kubernetes Dashboard
minikube dashboard
```

### Docker Images

```bash
# Build frontend
cd frontend
docker build -t todo-frontend:local -f Dockerfile .

# Build backend
cd backend
docker build -t todo-backend:local -f Dockerfile .

# Load into Minikube (if needed)
minikube image load todo-frontend:local
minikube image load todo-backend:local

# View images
docker images

# Remove old images
docker rmi todo-frontend:local
docker rmi todo-backend:local
```

### Kubernetes (kubectl)

```bash
# Get all pods
kubectl get pods

# Watch pods (live updates)
kubectl get pods -w

# Get services
kubectl get services

# Describe pod (for troubleshooting)
kubectl describe pod <pod-name>

# Get logs
kubectl logs <pod-name>

# Follow logs (live)
kubectl logs -f <pod-name>

# Get logs for all pods with label
kubectl logs -l app=todo-app-backend
kubectl logs -l app=todo-app-frontend

# Exec into pod
kubectl exec -it <pod-name> -- /bin/sh

# Delete pod (Kubernetes will recreate)
kubectl delete pod <pod-name>

# Scale deployment
kubectl scale deployment todo-app-backend --replicas=3
```

### Helm

```bash
# Install chart
helm install todo-app ./helm/todo-chart --values values-local.yaml

# Upgrade deployment
helm upgrade todo-app ./helm/todo-chart --values values-local.yaml

# Rollback to previous version
helm rollback todo-app

# View history
helm history todo-app

# Uninstall
helm uninstall todo-app

# List releases
helm list

# Lint chart (validate)
helm lint ./helm/todo-chart
```

### Secrets Management

```bash
# Create secret from literal values
kubectl create secret generic todo-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=openai-api-key="sk-..." \
  --from-literal=jwt-secret="your-secret" \
  --from-literal=better-auth-secret="your-secret"

# Create secret from file
kubectl create secret generic todo-secrets --from-env-file=backend/.env

# View secret (base64 encoded)
kubectl get secret todo-secrets -o yaml

# Decode secret value
kubectl get secret todo-secrets -o jsonpath='{.data.database-url}' | base64 -d

# Update secret (delete and recreate)
kubectl delete secret todo-secrets
kubectl create secret generic todo-secrets --from-env-file=backend/.env
```

---

## Development Workflow

### 1. Local Development

Make changes to frontend or backend code.

### 2. Test Locally

```bash
# Start backend
cd backend
uvicorn src.main:app --reload --port 8000

# Start frontend (new terminal)
cd frontend
npm run dev
```

### 3. Build Docker Images

```bash
# Frontend
cd frontend
docker build -t todo-frontend:local -f Dockerfile .

# Backend
cd backend
docker build -t todo-backend:local -f Dockerfile .
```

### 4. Deploy to Kubernetes

```bash
cd helm/todo-chart
# Run deploy.bat or deploy.ps1
```

### 5. Verify Changes

```bash
# Check pods
kubectl get pods

# View logs
kubectl logs -l app=todo-app-backend

# Access application
start $(minikube service todo-app-frontend --url)
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod to see events
kubectl describe pod <pod-name>

# Common issues:
# - ImagePullBackOff: Load image into Minikube
# - CrashLoopBackOff: Check logs for errors
# - Pending: Check resources/scheduling
```

### Service Not Accessible

```bash
# Check NodePort
kubectl get service todo-app-frontend

# Verify firewall allows NodePort (30080)

# Try port forwarding
kubectl port-forward service/todo-app-frontend 3000:80
```

### Database Connection Errors

```bash
# Check secret exists
kubectl get secret todo-secrets

# Verify secret values (base64 decoded)
kubectl get secret todo-secrets -o yaml

# Check backend logs
kubectl logs -l app=todo-app-backend

# Test database connectivity
kubectl exec -it <pod-name> -- python -c "from src.db import engine; print(engine.connect())"
```

### Health Probe Failures

```bash
# Check probe configuration
kubectl describe pod <pod-name> | grep -A 10 Liveness

# Manually test health endpoint
kubectl exec -it <pod-name> -- wget -O- http://localhost:8000/health
kubectl exec -it <pod-name> -- wget -O- http://localhost:8000/ready

# Adjust probe timing in values.yaml
helm upgrade todo-app ./helm/todo-chart --set backend.livenessProbe.initialDelaySeconds=60
```

### Helm Chart Issues

```bash
# Validate chart
helm lint ./helm/todo-chart

# Dry run to see what would be deployed
helm upgrade --dry-run --debug todo-app ./helm/todo-chart

# Get deployment values
helm get values todo-app
```

---

## AI DevOps Tools

### kubectl-ai

```bash
# Install via krew
kubectl krew install kubectl-ai

# Troubleshoot
kubectl-ai "why are my pods failing?"

# Scale
kubectl-ai "scale backend to 3 replicas"

# Optimize
kubectl-ai "reduce resource usage"
```

### kagent

```bash
# Analyze health
kagent "analyze cluster health"

# Performance check
kagent "check backend performance"

# Cost analysis
kagent "show resource costs"
```

### Docker AI (Gordon)

Enable in Docker Desktop > Settings > Beta Features

```bash
# Optimize Dockerfile
docker ai "optimize my dockerfile for production"

# Reduce size
docker ai "why is my image so large?"

# Security review
docker ai "check my dockerfile for security issues"
```

---

## Monitoring

### View Pod Resources

```bash
# Top pods by resource usage
kubectl top pods

# Watch resource usage
kubectl top pods -w

# View node resources
kubectl top nodes
```

### View Events

```bash
# All cluster events
kubectl get events --sort-by='.lastTimestamp'

# Events for specific namespace
kubectl get events -n default

# Events for specific pod
kubectl describe pod <pod-name>
```

### Logs

```bash
# All logs from pod
kubectl logs <pod-name>

# Follow logs (live)
kubectl logs -f <pod-name>

# Previous container logs (if pod restarted)
kubectl logs <pod-name> --previous

# Multiple containers in pod
kubectl logs <pod-name> -c <container-name>
```

---

## Cleanup

```bash
# Uninstall Helm release
helm uninstall todo-app

# Delete secrets
kubectl delete secret todo-secrets

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete

# Remove Docker images
docker rmi todo-frontend:local todo-backend:local
```

---

## Environment Variables

### Required Secrets

| Key | Description | Source |
|------|-------------|---------|
| `database-url` | Neon PostgreSQL connection | `backend/.env` |
| `openai-api-key` | OpenAI API key | `backend/.env` |
| `jwt-secret` | JWT authentication secret | `backend/.env` |
| `better-auth-secret` | Better Auth secret | `backend/.env` |

### ConfigMap Values

| Key | Value | Description |
|------|-------|-------------|
| `BACKEND_URL` | `http://todo-backend:8000` | Backend service URL |
| `LOG_LEVEL` | `info` / `debug` | Logging verbosity |
| `ENVIRONMENT` | `local` / `production` | Deployment environment |

---

## Resources

- **Docker**: https://docs.docker.com/
- **Minikube**: https://minikube.sigs.k8s.io/docs/
- **Kubernetes**: https://kubernetes.io/docs/
- **Helm**: https://helm.sh/docs/
- **kubectl-ai**: https://github.com/sozercan/kubectl-ai
- **kagent**: https://github.com/your-repo/kagent

---

## Support

For issues or questions:
1. Check `specs/004-kubernetes-deployment/IMPLEMENTATION_STATUS.md`
2. Review `helm/todo-chart/NOTES.txt` after deployment
3. Check pod logs: `kubectl logs <pod-name>`
4. Use AI tools: `kubectl-ai "troubleshoot deployment"`
