# Kubernetes Tools Installation Script for Windows
# Installs Chocolatey, Minikube, and Helm

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Kubernetes Tools Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Step 1: Check/Install Chocolatey
Write-Host "[1/4] Checking Chocolatey..." -ForegroundColor Yellow
try {
    $chocoVersion = choco --version
    Write-Host "Chocolatey is installed: $chocoVersion" -ForegroundColor Green
} catch {
    Write-Host "Chocolatey not found. Installing..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    $chocoVersion = choco --version
    Write-Host "Chocolatey installed: $chocoVersion" -ForegroundColor Green
}
Write-Host ""

# Step 2: Install Minikube
Write-Host "[2/4] Installing Minikube..." -ForegroundColor Yellow
try {
    $minikubeVersion = minikube --version
    Write-Host "Minikube is already installed: $minikubeVersion" -ForegroundColor Green
} catch {
    Write-Host "Installing Minikube via Chocolatey..." -ForegroundColor Gray
    choco install minikube -y

    # Refresh environment
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    $minikubeVersion = minikube --version
    Write-Host "Minikube installed: $minikubeVersion" -ForegroundColor Green
}
Write-Host ""

# Step 3: Install Helm
Write-Host "[3/4] Installing Helm..." -ForegroundColor Yellow
try {
    $helmVersion = helm version --short
    Write-Host "Helm is already installed: $helmVersion" -ForegroundColor Green
} catch {
    Write-Host "Installing Helm via Chocolatey..." -ForegroundColor Gray
    choco install kubernetes-helm -y

    # Refresh environment
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    $helmVersion = helm version --short
    Write-Host "Helm installed: $helmVersion" -ForegroundColor Green
}
Write-Host ""

# Step 4: Verify installations
Write-Host "[4/4] Verifying installations..." -ForegroundColor Yellow
Write-Host ""

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker: Not found (install from docker.com)" -ForegroundColor Red
}

# Check Minikube
try {
    $minikubeVersion = minikube --version
    Write-Host "✅ Minikube: $minikubeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Minikube: Installation failed" -ForegroundColor Red
}

# Check kubectl
try {
    $kubectlVersion = kubectl version --client --short
    Write-Host "✅ kubectl: $kubectlVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ kubectl: Not found" -ForegroundColor Red
}

# Check Helm
try {
    $helmVersion = helm version --short
    Write-Host "✅ Helm: $helmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Helm: Installation failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Next steps
Write-Host "Next steps:" -ForegroundColor White
Write-Host ""
Write-Host "1. Close this terminal and open a new one (to refresh PATH)" -ForegroundColor Yellow
Write-Host "2. Start Minikube:" -ForegroundColor Yellow
Write-Host "   minikube start --cpus=4 --memory=8192 --disk-size=20g" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Build Docker images:" -ForegroundColor Yellow
Write-Host "   cd frontend && docker build -t todo-frontend:local -f Dockerfile ." -ForegroundColor Cyan
Write-Host "   cd ..\backend && docker build -t todo-backend:local -f Dockerfile ." -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Deploy to Kubernetes:" -ForegroundColor Yellow
Write-Host "   cd helm\todo-chart" -ForegroundColor Cyan
Write-Host "   .\deploy.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed instructions, see: helm\chart\DEVELOPER_GUIDE.md" -ForegroundColor Gray
Write-Host ""

# Ask to start Minikube
$response = Read-Host "Do you want to start Minikube now? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "Starting Minikube (4 CPU, 8GB RAM)..." -ForegroundColor Yellow
    minikube start --cpus=4 --memory=8192 --disk-size=20g

    Write-Host ""
    Write-Host "Minikube started successfully!" -ForegroundColor Green
    Write-Host "Current status:" -ForegroundColor Yellow
    minikube status
    Write-Host ""
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
