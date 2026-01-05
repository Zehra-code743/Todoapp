# Research: Local Kubernetes Deployment

**Feature**: 004-kubernetes-deployment
**Date**: 2026-01-05

## Overview

Research findings for containerizing Todo AI Chatbot applications and deploying to local Kubernetes cluster using Minikube with Helm charts and AI DevOps tools.

---

## Technology Stack Decisions

### Docker Multi-Stage Build Strategy

**Decision**: Use multi-stage builds for both frontend (Next.js) and backend (FastAPI)

**Frontend (Next.js 20 Alpine)**:
- Builder stage: node:20-alpine, install dependencies with npm ci, build Next.js application
- Runner stage: node:20-alpine, copy built artifacts, run production server
- Non-root user: nextjs (UID 1001)
- Base: Alpine Linux for minimal image size
- Target: <500MB final image

**Backend (Python 3.13 slim)**:
- Builder stage: python:3.13-slim, install uv, install dependencies with uv sync
- Runner stage: python:3.13-slim, copy venv and code, run uvicorn
- Non-root user: appuser (UID 1001)
- Base: Debian slim for Python packages
- Target: <300MB final image

**Rationale**: Multi-stage builds reduce final image size by excluding build tools and dependencies, improve security by running as non-root user, and enable layer caching for faster rebuilds.

**Alternatives Considered**:
- Single-stage build: Simpler but larger images (rejected)
- BuildKit with Buildah: More complex learning curve (rejected)
- Nix-based builds: Overkill for this use case (rejected)

---

## Helm Chart Structure

**Decision**: Use standard Helm chart structure with templates and values files

**Chart Organization**:
```
helm/todo-chart/
├── Chart.yaml           # Chart metadata (name, version, maintainers)
├── values.yaml          # Default values (replicas: 2, resource limits)
├── values-local.yaml    # Minikube overrides (replicas: 1, lower resources)
├── values-prod.yaml     # Production overrides (for Phase V)
├── templates/
│   ├── _helpers.tpl      # Template helper functions
│   ├── deployment-frontend.yaml
│   ├── deployment-backend.yaml
│   ├── service-frontend.yaml
│   ├── service-backend.yaml
│   ├── configmap.yaml
│   └── secret.yaml
└── NOTES.txt            # Post-install instructions
```

**Rationale**: Standard Helm structure provides templating capabilities, environment-specific overrides, and industry-recognized pattern for deployment automation.

**Alternatives Considered**:
- Kustomize: Less familiar, more verbose (rejected)
- Plain Kubernetes manifests: No templating, harder to manage (rejected)
- Argo CD workflows: Overkill for local deployment (rejected)

---

## Kubernetes Resource Configuration

**Decision**: Define resource requests and limits per pod

**Frontend Pod**:
- Requests: 256Mi memory, 250m CPU
- Limits: 512Mi memory, 500m CPU
- Replicas: 2 (prod) / 1 (local)

**Backend Pod**:
- Requests: 512Mi memory, 500m CPU
- Limits: 1Gi memory, 1000m CPU
- Replicas: 2 (prod) / 1 (local)

**Rationale**: Resource requests ensure pods get scheduled, limits prevent runaway resource consumption. Different values for local vs. prod environment.

**Alternatives Considered**:
- No resource limits: Risk of resource exhaustion (rejected)
- Vertical Pod Autoscaler: More complex for local use (rejected)
- Horizontal Pod Autoscaler (HPA): Optional for production (deferred to Phase V)

---

## Health Probe Configuration

**Decision**: Implement both liveness and readiness probes with specific timings

**Frontend**:
- Liveness: HTTP GET /, initialDelay: 30s, period: 10s, timeout: 5s, failureThreshold: 3
- Readiness: HTTP GET /, initialDelay: 10s, period: 5s, timeout: 3s, failureThreshold: 3

**Backend**:
- Liveness: HTTP GET /health, initialDelay: 30s, period: 10s, timeout: 5s, failureThreshold: 3
- Readiness: HTTP GET /ready, initialDelay: 10s, period: 5s, timeout: 3s, failureThreshold: 3

**Rationale**: Health probes ensure pod health, trigger restarts for unhealthy pods, and prevent traffic until ready. Backend needs database connection check (/ready endpoint).

**Alternatives Considered**:
- TCP probes: Simpler but less informative (rejected)
- Command probes: More complex but reliable for specific checks (rejected)
- No probes: Cannot detect pod failures (rejected)

---

## Service Exposure Strategy

**Decision**: Use NodePort for local Minikube access

**Frontend Service**:
- Type: NodePort
- Port: 80
- NodePort: 30080 (fixed for easy access)
- SessionAffinity: None

**Backend Service**:
- Type: ClusterIP (internal only)
- Port: 8000
- SessionAffinity: None

**Rationale**: NodePort provides simple, reliable local access without ingress controller. ClusterIP for backend since it's only consumed by frontend.

**Alternatives Considered**:
- LoadBalancer type: More complex on Minikube (rejected)
- Ingress controller: Overkill for local development (rejected)
- HostNetwork: Direct host access but less secure (rejected)

---

## ConfigMap vs. Secrets Strategy

**Decision**: Use ConfigMap for non-sensitive config, Secrets for sensitive data

**ConfigMap (Non-Sensitive)**:
- BACKEND_URL: http://todo-backend:8000
- LOG_LEVEL: info
- ENVIRONMENT: local

**Secrets (Sensitive)**:
- database-url: Base64 encoded DATABASE_URL (Neon PostgreSQL)
- openai-api-key: Base64 encoded OPENAI_API_KEY
- jwt-secret: Base64 encoded JWT_SECRET
- better-auth-secret: Base64 encoded BETTER_AUTH_SECRET

**Rationale**: Separation follows Kubernetes best practices, enables different access controls, and supports audit trails for secret access.

**Alternatives Considered**:
- All in ConfigMap: Insecure (rejected)
- Environment variables in Dockerfile: Inflexible, not secrets management (rejected)
- External secret manager (Vault): Overkill for local deployment (rejected)

---

## Rolling Update Strategy

**Decision**: Use RollingUpdate with maxSurge: 1, maxUnavailable: 0

**Configuration**:
- Strategy: RollingUpdate
- maxSurge: 1 (one extra pod during update)
- maxUnavailable: 0 (zero pods unavailable during update)
- Readiness probe required: Yes

**Rationale**: Ensures zero-downtime deployments, maintains high availability during updates, Kubernetes manages traffic routing.

**Alternatives Considered**:
- Recreate: Deletes all pods before creating new ones (downtime, rejected)
- OnDelete: No automatic replacement (manual process, rejected)
- No strategy specified: Kubernetes default (may cause downtime, rejected)

---

## AI DevOps Tools Integration

**Decision**: Integrate kubectl-ai, kagent, and Docker AI (Gordon) for operations

**kubectl-ai**:
- Purpose: Natural language Kubernetes operations
- Capabilities: Deployment, scaling, debugging, resource queries, log analysis
- Installation: kubectl krew install kubectl-ai
- Usage: `kubectl-ai "why are my pods failing?"`

**kagent**:
- Purpose: Cluster analysis and optimization
- Capabilities: Health analysis, resource optimization, cost analysis, security scanning, performance tuning
- Usage: `kagent "analyze cluster health"`

**Docker AI (Gordon)**:
- Purpose: Intelligent Docker operations
- Capabilities: Dockerfile optimization, image analysis, build troubleshooting, security recommendations
- Setup: Docker Desktop 4.53+ > Beta features > Enable Gordon
- Usage: `docker ai "optimize my dockerfile for production"`

**Rationale**: AI tools reduce operational overhead, speed up troubleshooting, provide intelligent recommendations for optimization.

**Alternatives Considered**:
- Manual kubectl: Slow, requires expertise (rejected)
- Traditional observability tools: More setup, less interactive (rejected)

---

## .dockerignore Configuration

**Decision**: Create .dockerignore files to optimize builds

**Frontend .dockerignore**:
```
node_modules
.next
.git
.env.local
.DS_Store
*.log
```

**Backend .dockerignore**:
```
.git
__pycache__
*.pyc
.env
.venv
.pytest_cache
.pytest_cache
.coverage
.DS_Store
*.log
```

**Rationale**: Excludes unnecessary files from Docker build context, reduces image size, speeds up builds, prevents caching issues.

**Alternatives Considered**:
- No .dockerignore: Large images, slow builds (rejected)
- Manual build context specification: Error-prone (rejected)

---

## Minikube Configuration

**Decision**: Document Minikube setup requirements

**Minimum Requirements**:
- CPU: 4 cores
- Memory: 8GB RAM
- Disk: 20GB free space

**Recommended Driver**:
- Docker driver (Windows, macOS)
- HyperKit (macOS alternative)
- VirtualBox (Linux alternative)

**Startup Command**:
```bash
minikube start --cpus=4 --memory=8192 --disk-size=20g
```

**Rationale**: Clear minimum requirements prevent deployment failures. Docker driver most widely supported.

**Alternatives Considered**:
- Kind (Kubernetes in Docker): More resource overhead (rejected)
- K3d: Lighter but less mature (rejected)
- Minishift: Deprecated (rejected)

---

## Summary of Decisions

All decisions follow:
1. **Cloud-Native principles**: Container-based, orchestrated, infrastructure as code
2. **Stateless architecture**: External database (Neon) for state persistence
3. **Separation of concerns**: Clear boundaries between spec, contracts, infrastructure, implementation
4. **Best practices**: Multi-stage builds, health probes, rolling updates, ConfigMap/Secrets separation
5. **AI-First operations**: Leverage kubectl-ai, kagent, Docker AI for intelligent DevOps

All decisions documented with rationale and alternatives considered. Ready for design phase.
