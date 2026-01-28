# Todoapp Deployment Instructions

Congratulations! You now have everything you need to deploy your Todoapp to Kubernetes with a single script that pulls from GitHub and deploys automatically.

## Files Created

1. **deploy.sh** - Bash script for Linux/macOS
2. **deploy.ps1** - PowerShell script for Windows
3. **deploy.bat** - Batch script for Windows Command Prompt
4. **DEPLOYMENT.md** - Complete documentation

## Pre-requisites Already Configured

✅ Minikube is running
✅ kubectl is connected to Minikube
✅ Docker environment is configured for Minikube

## How to Deploy

Simply run the appropriate script for your system:

### Linux/macOS:
```bash
./deploy.sh
```

### Windows (PowerShell):
```powershell
.\deploy.ps1
```

### Windows (Command Prompt):
```cmd
deploy.bat
```

## What Happens During Deployment

1. **Pulls latest code** from GitHub (origin/main or origin/master)
2. **Builds Docker images** for backend and frontend
3. **Deploys infrastructure** in the correct order:
   - Namespace (todoapp)
   - PostgreSQL database
   - Kafka (if available)
   - Backend service
   - Frontend service
4. **Waits for all services** to be ready
5. **Provides access information** when complete

## Quick Start Command

To deploy right now with the default configuration:
```bash
./deploy.sh
```

## Accessing Your Application

After deployment completes, the script will show you the external IPs. Typically:
- Frontend: http://[EXTERNAL-IP]:3000
- Backend: http://[EXTERNAL-IP]:8000

For Minikube, you might need to run `minikube tunnel` in a separate terminal to expose LoadBalancer services.

## Troubleshooting

If you encounter issues:
1. Make sure all prerequisites are installed
2. Run the script with admin/root privileges if needed
3. Check that Minikube is running with `minikube status`
4. Verify connectivity to GitHub and Docker Hub

Your deployment is ready! Just run the appropriate script and your application will be deployed to Kubernetes with the latest code from GitHub.