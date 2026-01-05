---
id: 001
title: kubernetes specification created
stage: spec
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-kubernetes-deployment
branch: 004-kubernetes-deployment
user: developer
command: /sp.specify
labels: [spec, kubernetes, docker, deployment]
links:
  spec: specs/004-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/004-kubernetes-deployment/spec.md
 - specs/004-kubernetes-deployment/checklists/requirements.md
tests:
 - Specification quality validation checklist created and completed
---

## Prompt

# Phase IV: Local Kubernetes Deployment - Complete Specification

## 1. Project Overview

### 1.1 Purpose
Deploy the Todo AI Chatbot on a local Kubernetes cluster using Minikube, with containerized applications, Helm charts for deployment management, and AI-assisted DevOps tools (Docker AI, kubectl-ai, kagent).

### 1.2 Phase Objectives
- Containerize frontend and backend applications using Docker
- Create Helm charts for Kubernetes deployment
- Deploy complete application stack on Minikube locally
- Utilize AI-powered DevOps tools for intelligent operations
- Establish production-ready deployment patterns

### 1.3 Success Criteria
- [ ] Frontend and backend successfully containerized
- [ ] Helm charts deploy application to Minikube
- [ ] All services communicate correctly in Kubernetes
- [ ] Database connectivity established from pods
- [ ] AI DevOps tools (kubectl-ai, kagent) operational
- [ ] Application accessible via local browser
- [ ] Deployments are reproducible and documented

---

## 2. Constitution (WHY - Principles & Constraints)

### 2.1 Core Principles

#### 2.1.1 Cloud-Native Architecture
- **Principle**: Design for containerized, orchestrated environments
- **Rationale**: Enables scalability, portability, and resilience
- **Implementation**: 12-factor app principles, stateless services

#### 2.1.2 Infrastructure as Code
- **Principle**: All infrastructure defined in version-controlled files
- **Rationale**: Reproducibility, auditability, and automation
- **Implementation**: Helm charts, Dockerfiles, YAML manifests

#### 2.1.3 AI-Assisted Operations (AIOps)
- **Principle**: Leverage AI tools for DevOps tasks
- **Rationale**: Faster troubleshooting, better resource optimization
- **Implementation**: Docker AI (Gordon), kubectl-ai, kagent

#### 2.1.4 Local-First Development
- **Principle**: Develop and test locally before cloud deployment
- **Rationale**: Faster iteration, cost savings, offline capability
- **Implementation**: Minikube for local Kubernetes cluster

#### 2.1.5 Service Isolation
- **Principle**: Each service runs in its own container
- **Rationale**: Independent scaling, failure isolation, easier debugging
- **Implementation**: Separate deployments for frontend, backend, database

### 2.2 Technical Constraints

#### 2.2.1 Technology Stack Requirements
- **Container Runtime**: Docker Desktop 4.53+
- **Orchestration**: Kubernetes via Minikube
- **Package Manager**: Helm 3.x
- **AI DevOps**: Docker AI (Gordon), kubectl-ai, kagent
- **Base Images**: Node:20-alpine (frontend), Python:3.13-slim (backend)
- **Database**: Neon Serverless PostgreSQL (external, not containerized)

#### 2.2.2 Resource Constraints
- Minikube minimum requirements:
  - CPU: 4 cores
  - Memory: 8 GB RAM
  - Disk: 20 GB free space
- Pod resource limits:
  - Frontend: 512Mi memory, 500m CPU
  - Backend: 1Gi memory, 1000m CPU

#### 2.2.3 Network Constraints
- Services communicate via Kubernetes internal DNS
- External access via NodePort or LoadBalancer (Minikube tunnel)
- Database remains external (Neon cloud) with secure connection
- CORS configured for frontend-backend communication

#### 2.2.4 Security Constraints
- Secrets stored in Kubernetes Secrets (not in images)
- Environment variables injected at runtime
- No hardcoded credentials in Dockerfiles or Helm charts
- Image scanning for vulnerabilities (optional but recommended)

### 2.3 Architectural Decisions

#### 2.3.1 Monorepo with Multi-Container Deployment
**Decision**: Keep monorepo structure but deploy as separate containers

**Justification**:
- Maintains code organization from previous phases
- Allows independent scaling of frontend/backend
- Simplifies CI/CD with single repository
- Better resource utilization in Kubernetes

#### 2.3.2 Helm Charts Over Raw YAML
**Decision**: Use Helm charts instead of plain Kubernetes manifests

**Justification**:
- Templating reduces duplication
- Easy environment-specific configuration
- Version management for deployments
- Industry standard for Kubernetes packaging
- Easier rollbacks and upgrades

#### 2.3.3 External Database (Neon)
**Decision**: Don't containerize PostgreSQL, keep using Neon

**Justification**:
- Neon provides serverless scaling
- Managed backups and high availability
- Simpler than managing PostgreSQL in Kubernetes
- Matches previous phase architecture
- Focus on application layer, not database ops

#### 2.3.4 NodePort for Local Access
**Decision**: Use NodePort service type for Minikube access

**Justification**:
- Simple local access pattern
- Works reliably on Minikube
- No need for ingress controller in local environment
- Easy to test from browser

#### 2.3.5 Multi-Stage Docker Builds
**Decision**: Use multi-stage builds for optimized images

**Justification**:
- Smaller final image size
- Faster deployments
- Reduced attack surface
- Build tools not included in runtime image

---

## 3. Specify (WHAT - Requirements & Features)

### 3.1 User Journeys

#### 3.1.1 Developer: First-Time Deployment
```
Actor: Developer with Minikube installed
Goal: Deploy application to local Kubernetes cluster

Steps:
1. Developer clones repository
2. Runs `minikube start` to create cluster
3. Builds Docker images: `docker build -t todo-frontend:local frontend/`
4. Builds backend: `docker build -t todo-backend:local backend/`
5. Installs Helm chart: `helm install todo-app ./helm/todo-chart`
6. Waits for pods to be ready: `kubectl get pods --watch`
7. Gets service URL: `minikube service todo-frontend --url`
8. Opens browser to access application
9. Application loads successfully
10. Can interact with chatbot and manage tasks
```

#### 3.1.2 Developer: Using AI DevOps Tools
```
Actor: Developer troubleshooting deployment
Goal: Use AI tools to diagnose and fix issues

Steps:
1. Deployment fails with unknown error
2. Developer asks: `kubectl-ai "why are my pods failing?"`
3. kubectl-ai analyzes pod logs and events
4. kubectl-ai suggests: "Backend pod missing DATABASE_URL secret"
5. Developer asks: `kubectl-ai "create secret for database connection"`
6. kubectl-ai generates and applies secret YAML
7. Developer restarts deployment
8. Pods become healthy
9. Developer asks: `kagent "analyze cluster health"`
10. kagent provides resource utilization report
```

#### 3.1.3 Developer: Scaling Application
```
Actor: Developer load testing application
Goal: Scale backend to handle increased load

Steps:
1. Developer runs load test on API
2. Backend pods show high CPU usage
3. Developer asks: `kubectl-ai "scale backend to handle more load"`
4. kubectl-ai suggests: `kubectl scale deployment todo-backend --replicas=3`
5. kubectl-ai applies scaling automatically
6. New backend pods spin up
7. Load balances across 3 backend instances
8. Response times improve
9. Developer verifies with: `kagent "check backend performance"`
```

#### 3.1.4 Developer: Updating Application
```
Actor: Developer with new feature code
Goal: Deploy updated version

Steps:
1. Developer makes code changes
2. Rebuilds Docker images with new tag: `docker build -t todo-frontend:v2 frontend/`
3. Updates Helm values: `image.tag: v2`
4. Upgrades release: `helm upgrade todo-app ./helm/todo-chart`
5. Kubernetes performs rolling update
6. Old pods terminate gracefully
7. New pods come online
8. Zero downtime deployment
9. Developer verifies new feature works
```

### 3.2 Functional Requirements

#### 3.2.1 Docker Containerization (FR-D)

**FR-D-1: Frontend Dockerfile**
```dockerfile
Purpose: Create optimized Next.js production image

Requirements:
- Multi-stage build (build stage + runtime stage)
- Node 20 Alpine base image
- Install dependencies with npm ci
- Build Next.js application
- Expose port 3000
- Non-root user for security
- Environment variables injectable at runtime

Stages:
1. Builder: Install deps, build app
2. Runner: Copy built artifacts, run production server
```

**FR-D-2: Backend Dockerfile**
```dockerfile
Purpose: Create optimized FastAPI production image

Requirements:
- Multi-stage build (build stage + runtime stage)
- Python 3.13 slim base image
- Install dependencies with uv
- Copy application code
- Expose port 8000
- Non-root user for security
- Environment variables injectable at runtime

Stages:
1. Builder: Install uv, install dependencies
2. Runner: Copy venv and code, run uvicorn
```

**FR-D-3: Image Optimization**
- Final image size < 500MB for frontend
- Final image size < 300MB for backend
- Use .dockerignore to exclude unnecessary files
- Layer caching optimized for fast rebuilds
- Security scanning passes (no critical vulnerabilities)

**FR-D-4: Docker AI (Gordon) Integration**
```bash
# Gordon can assist with:
docker ai "optimize my dockerfile for production"
docker ai "why is my image so large?"
docker ai "add health check to my container"
docker ai "secure my dockerfile following best practices"
```

#### 3.2.2 Kubernetes Manifests (FR-K)

**FR-K-1: Frontend Deployment**
```yaml
Purpose: Deploy Next.js frontend pods

Specifications:
- Replicas: 2 (for high availability)
- Container port: 3000
- Resource requests: 256Mi memory, 250m CPU
- Resource limits: 512Mi memory, 500m CPU
- Liveness probe: HTTP GET /
- Readiness probe: HTTP GET /
- Environment variables from ConfigMap/Secret
- Rolling update strategy (maxSurge: 1, maxUnavailable: 0)
```

**FR-K-2: Backend Deployment**
```yaml
Purpose: Deploy FastAPI backend pods

Specifications:
- Replicas: 2 (for high availability)
- Container port: 8000
- Resource requests: 512Mi memory, 500m CPU
- Resource limits: 1Gi memory, 1000m CPU
- Liveness probe: HTTP GET /health
- Readiness probe: HTTP GET /ready
- Environment variables from ConfigMap/Secret
- Rolling update strategy (maxSurge: 1, maxUnavailable: 0)
```

**FR-K-3: Frontend Service**
```yaml
Purpose: Expose frontend to external traffic

Specifications:
- Type: NodePort
- Port: 80 (maps to container 3000)
- NodePort: 30080 (fixed for easy access)
- Selector: app=todo-frontend
- Session affinity: None
```

**FR-K-4: Backend Service**
```yaml
Purpose: Expose backend to frontend pods

Specifications:
- Type: ClusterIP (internal only)
- Port: 8000
- Selector: app=todo-backend
- Session affinity: None
```

**FR-K-5: ConfigMap**
```yaml
Purpose: Store non-sensitive configuration

Data:
- BACKEND_URL: http://todo-backend:8000
- LOG_LEVEL: info
- ENVIRONMENT: local
```

**FR-K-6: Secrets**
```yaml
Purpose: Store sensitive data

Data (base64 encoded):
- DATABASE_URL: Neon PostgreSQL connection string
- OPENAI_API_KEY: OpenAI API key
- JWT_SECRET: Better Auth JWT secret
- BETTER_AUTH_SECRET: Better Auth secret
```

#### 3.2.3 Helm Chart Structure (FR-H)

**FR-H-1: Chart Directory Structure**
```
helm/todo-chart/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── values-local.yaml       # Local/Minikube overrides
├── values-prod.yaml        # Production overrides (for Phase V)
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   ├── deployment-frontend.yaml
│   ├── deployment-backend.yaml
│   ├── service-frontend.yaml
│   ├── service-backend.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml            # Horizontal Pod Autoscaler (optional)
│   └── NOTES.txt           # Post-install instructions
└── .helmignore
```

**FR-H-2: Chart.yaml Specification**
```yaml
apiVersion: v2
name: todo-app
description: AI-Powered Todo Chatbot Application
type: application
version: 1.0.0          # Chart version
appVersion: "1.0.0"     # Application version
keywords:
  - todo
  - chatbot
  - ai
maintainers:
  - name: [Your Name]
    email: [Your Email]
```

**FR-H-3: values.yaml Structure**
```yaml
Purpose: Define configurable parameters

Sections:
- global: Global settings (environment, region)
- frontend: Frontend image, replicas, resources, env vars
- backend: Backend image, replicas, resources, env vars
- database: External database configuration
- secrets: Secret references (not values!)
- ingress: Ingress configuration (for prod)
- serviceAccount: Service account settings
```

**FR-H-4: Template Functions**
```yaml
Purpose: Reusable template helpers

Functions:
- todo-app.name: Generate resource names
- todo-app.fullname: Generate full resource names
- todo-app.labels: Generate standard labels
- todo-app.selectorLabels: Generate selector labels
```

**FR-H-5: values-local.yaml Overrides**
```yaml
Purpose: Local Minikube-specific settings

Overrides:
- Service type: NodePort (instead of ClusterIP)
- Replicas: 1 (to save resources)
- Resource limits: Lower values
- Image pull policy: IfNotPresent
- Database: External Neon URL
```

#### 3.2.4 Health Checks & Probes (FR-HC)

**FR-HC-1: Backend Health Endpoint**
```python
Purpose: Kubernetes liveness check

Endpoint: GET /health

Response (200 OK):
{
  "status": "healthy",
  "timestamp": "2026-01-05T12:00:00Z"
}

Checks:
- Server is running
- No exceptions in handler
```

**FR-HC-2: Backend Readiness Endpoint**
```python
Purpose: Kubernetes readiness check

Endpoint: GET /ready

Response (200 OK):
{
  "status": "ready",
  "database": "connected",
  "mcp_server": "running"
}

Response (503 Service Unavailable):
{
  "status": "not ready",
  "database": "disconnected"
}

Checks:
- Database connection is active
- MCP server is initialized
```

**FR-HC-3: Probe Configuration**
```yaml
Liveness Probe:
- Initial delay: 30 seconds
- Period: 10 seconds
- Timeout: 5 seconds
- Failure threshold: 3

Readiness Probe:
- Initial delay: 10 seconds
- Period: 5 seconds
- Timeout: 3 seconds
- Failure threshold: 3
- Success threshold: 1
```

#### 3.2.5 AI DevOps Integration (FR-AI)

**FR-AI-1: kubectl-ai Usage**
```bash
Purpose: Natural language Kubernetes operations

Capabilities:
- Deployment: "deploy the todo frontend with 2 replicas"
- Scaling: "scale backend to handle more load"
- Debugging: "check why the pods are failing"
- Resource management: "show me resource usage"
- Logs: "show me backend logs from the last hour"

Installation:
kubectl krew install kubectl-ai
```

**FR-AI-2: kagent Usage**
```bash
Purpose: Cluster analysis and optimization

Capabilities:
- Health analysis: "analyze cluster health"
- Resource optimization: "optimize resource allocation"
- Cost analysis: "show resource costs"
- Security scanning: "check for security issues"
- Performance tuning: "suggest performance improvements"

Installation:
[Follow kagent installation docs]
```

**FR-AI-3: Docker AI (Gordon) Usage**
```bash
Purpose: Intelligent Docker operations

Capabilities:
- Dockerfile optimization
- Image analysis
- Build troubleshooting
- Security recommendations
- Multi-platform builds

Setup:
- Docker Desktop 4.53+
- Settings > Beta features > Enable Gordon
```

### 3.3 Non-Functional Requirements

#### 3.3.1 Performance (NFR-P)
- **NFR-P-1**: Pod startup time < 60 seconds
- **NFR-P-2**: Rolling update with zero downtime
- **NFR-P-3**: Resource utilization < 70% under normal load
- **NFR-P-4**: Image pull time < 2 minutes

#### 3.3.2 Scalability (NFR-S)
- **NFR-S-1**: Support horizontal scaling (2-10 replicas)
- **NFR-S-2**: StatefulSets not required (stateless design)
- **NFR-S-3**: Load balancing across multiple pods
- **NFR-S-4**: Auto-scaling capable (HPA ready)

#### 3.3.3 Reliability (NFR-R)
- **NFR-R-1**: 99% uptime during deployment
- **NFR-R-2**: Automatic pod restart on failure
- **NFR-R-3**: Graceful shutdown (SIGTERM handling)
- **NFR-R-4**: Rollback capability via Helm

#### 3.3.4 Security (NFR-SE)
- **NFR-SE-1**: Secrets not in container images
- **NFR-SE-2**: Non-root user in containers
- **NFR-SE-3**: Network policies for pod isolation (optional)
- **NFR-SE-4**: Image vulnerability scanning

#### 3.3.5 Maintainability (NFR-M)
- **NFR-M-1**: Helm chart documentation complete
- **NFR-M-2**: All resources properly labeled
- **NFR-M-3**: Deployment instructions in README
- **NFR-M-4**: Environment variables clearly documented

#### 3.3.6 Portability (NFR-PO)
- **NFR-PO-1**: Works on Minikube (local)
- **NFR-PO-2**: Ready for cloud deployment (Phase V)
- **NFR-PO-3**: No Minikube-specific dependencies
- **NFR-PO-4**: Multi-architecture support (amd64, arm64)

### 3.4 Acceptance Criteria

#### AC-1: Containerization
- [ ] Frontend builds successfully as Docker image
- [ ] Backend builds successfully as Docker image
- [ ] Images are optimized (multi-stage builds)
- [ ] Containers run locally with `docker run`
- [ ] Environment variables injectable at runtime

#### AC-2: Kubernetes Deployment
- [ ] Helm chart installs without errors
- [ ] All pods reach Running state
- [ ] All pods pass readiness checks
- [ ] Services created and endpoints available
- [ ] ConfigMap and Secrets applied correctly

#### AC-3: Application Functionality
- [ ] Frontend accessible via NodePort
- [ ] Frontend can reach backend service
- [ ] Backend connects to Neon database
- [ ] User authentication works
- [ ] Chat functionality operational
- [ ] Tasks can be created/read/updated/deleted

#### AC-4: High Availability
- [ ] Multiple frontend replicas running
- [ ] Multiple backend replicas running
- [ ] Load balances across replicas
- [ ] Pod failure triggers automatic restart
- [ ] Rolling updates work without downtime

#### AC-5: AI DevOps Tools
- [ ] kubectl-ai successfully installed
- [ ] kubectl-ai can query cluster with natural language
- [ ] kagent analyzes cluster health
- [ ] Docker AI (Gordon) provides container optimization recommendations

---

## Response snapshot

Successfully created feature specification for Local Kubernetes Deployment (Phase IV). The specification includes:
- 4 prioritized user stories (P1-P4) covering deployment, troubleshooting, scaling, and updates
- 4 independent test paths for each user story
- 10 edge cases identified
- 40 functional requirements across Docker, Kubernetes, Helm, and AI DevOps tools
- 10 measurable success criteria with specific time/metric targets
- Dependencies and assumptions clearly documented
- Technology-agnostic language used throughout (removed implementation specifics like Minikube, Docker, Next.js, FastAPI, Helm)

Quality validation completed with all checklist items passing:
- No implementation details (removed technology-specific terminology)
- Focused on user value (developer productivity, operational efficiency)
- Written for non-technical stakeholders (business-focused)
- All mandatory sections completed
- No [NEEDS CLARIFICATION] markers
- Requirements are testable and unambiguous
- Success criteria are measurable and technology-agnostic
- All acceptance scenarios defined
- Edge cases identified
- Scope clearly bounded
- Dependencies and assumptions identified
- All functional requirements have clear acceptance criteria
- User scenarios cover primary flows
- Feature meets measurable outcomes
- No implementation details leak into specification

Created files:
- specs/004-kubernetes-deployment/spec.md - Complete feature specification
- specs/004-kubernetes-deployment/checklists/requirements.md - Quality validation checklist (all items passed)

## Outcome

- ✅ Impact: Feature specification created for Local Kubernetes Deployment with technology-agnostic requirements, measurable success criteria, and comprehensive user stories
- 🧪 Tests: Quality validation completed - all 14 checklist items passed
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: Ready for `/sp.clarify` or `/sp.plan`
- 🧠 Reflection: Successfully removed all implementation-specific language (Docker, Kubernetes, Helm, Minikube, Next.js, FastAPI) while preserving functional requirements. Used technology-agnostic terminology (container runtime, orchestration platform, deployment package, web application, API service) to make spec accessible to non-technical stakeholders.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All quality validation criteria passed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Ready for planning phase - proceed with `/sp.plan`
