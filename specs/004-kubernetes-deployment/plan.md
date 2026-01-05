# Implementation Plan: Local Kubernetes Deployment

**Branch**: `004-kubernetes-deployment` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-kubernetes-deployment/spec.md`

**Note**: This template is filled in by `/sp.plan` command. See `.specify/templates/commands/plan.md` for execution workflow.

## Summary

[Extract from feature spec: Containerize frontend (Next.js) and backend (FastAPI) applications with multi-stage Docker builds, create Helm charts for Kubernetes deployment with separate deployments for frontend and backend services, implement health endpoints (/health, /ready), configure ConfigMap for non-sensitive data, Secrets for sensitive data (database URL, API keys), support external NodePort access, integrate AI DevOps tools (kubectl-ai, kagent, Docker AI) for troubleshooting and operations]

## Technical Context

<!--
  ACTION REQUIRED: Replace content in this section with technical details
  for the project. The structure here is presented in an advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.13 (backend), Node 20 (frontend)
**Primary Dependencies**: Docker, Helm 3.x, Kubernetes (Minikube), kubectl, uv (Python package manager)
**Storage**: Neon Serverless PostgreSQL (external)
**Testing**: pytest (backend), pytest-asyncio, pytest-cov (backend)
**Target Platform**: Local Kubernetes (Minikube)
**Project Type**: Monorepo with multi-container deployment
**Performance Goals**: <60s pod startup, <2min deployment, zero-downtime rolling updates, <500MB frontend image, <300MB backend image
**Constraints**: Resource limits (512Mi/1Gi), non-root containers, secrets in Kubernetes, multi-stage builds
**Scale/Scope**: 1-3 replicas, 2 services (frontend/backend), local development focus

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

### Stateless Design
✅ **PASS**: Application uses external database (Neon PostgreSQL) for state persistence - complies with Constitution Principle III (Stateless Architecture by Default)
✅ **PASS**: No in-memory state for business logic specified - complies with Constitution Principle III

### Separation of Concerns
✅ **PASS**: Specifications define requirements (feature spec) - clear separation
✅ **PASS**: CLAUDE.md defines agent patterns - clear separation
✅ **PASS**: Infrastructure (Kubernetes/Helm) provides deployment capabilities - clear separation
✅ **PASS**: AI agents execute implementation following CLAUDE.md - clear separation

### Specification Before Implementation
✅ **PASS**: Feature specification exists at `/specs/004-kubernetes-deployment/spec.md`
✅ **PASS**: Acceptance criteria defined with testable scenarios
✅ **PASS**: Clear definition of user-observable behavior

### No Manual Coding Rule
✅ **PASS**: All implementation will be AI-generated following `/sp.implement`
✅ **PASS**: No manual code modifications to AI-generated files

### Transparent Spec History
✅ **PASS**: Specification lives in `/specs` directory with version control
✅ **PASS**: Will preserve iteration history

## Project Structure

### Documentation (this feature)

```text
specs/004-kubernetes-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace placeholder tree below with concrete layout
  for this feature. Delete unused options and expand to chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# Current monorepo structure (unchanged)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
├── tests/
├── pyproject.toml
├── uv.lock
├── Dockerfile           # NEW: Multi-stage container build
└── .dockerignore        # NEW: Build optimization

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
├── tests/
├── package.json
├── next.config.js
├── Dockerfile           # NEW: Multi-stage container build
└── .dockerignore        # NEW: Build optimization

helm/todo-chart/          # NEW: Helm chart for deployment
├── Chart.yaml            # Chart metadata
├── values.yaml           # Default configuration
├── values-local.yaml       # Minikube-specific overrides
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   ├── deployment-frontend.yaml
│   ├── deployment-backend.yaml
│   ├── service-frontend.yaml
│   ├── service-backend.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── NOTES.txt           # Post-install instructions
└── .helmignore
```

**Structure Decision**: Maintain existing monorepo structure with Dockerfile additions and new Helm chart directory at repository root. Container images built from existing backend/ and frontend/ directories.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|------------|------------|------------------------------------|
| None | Constitution compliant | No violations detected |

---

## Phase 0: Outline & Research

### Task: Create research.md

**Rationale**: Document all technology choices, best practices, and architectural decisions for Kubernetes deployment phase.

### Subtasks

1. Research Docker multi-stage build best practices for Next.js applications
2. Research Docker multi-stage build best practices for FastAPI applications
3. Research Helm chart structure and best practices for multi-service deployments
4. Research Kubernetes resource limits and health probe configurations
5. Research ConfigMap vs Secrets usage patterns
6. Research NodePort vs LoadBalancer for local Kubernetes access
7. Research AI DevOps tools integration (kubectl-ai, kagent, Docker AI)
8. Research rolling update strategies for zero downtime
9. Document technology stack: Docker, Helm, Kubernetes (Minikube), uv, Node 20, Python 3.13

**Output**: research.md with all decisions documented

---

## Phase 1: Design & Contracts

### Task: Create data-model.md

**Input**: Extract entities from feature specification
**Approach**: Document Kubernetes entities and their relationships

### Subtasks

1. Extract Container Image entity with attributes (name, tag, size, build stage)
2. Extract Service Instance entity with attributes (pod name, replica count, resource limits, health probes)
3. Extract Network Service entity with attributes (type, port mapping, internal/external access)
4. Extract Deployment entity with attributes (name, update strategy, template specification)
5. Extract Deployment Package entity with attributes (metadata, version, templates, values)
6. Extract Credential Storage entity with attributes (base64 encoding, secret keys)
7. Extract Configuration Storage entity with attributes (environment variables)
8. Extract Health Check entity with attributes (liveness, readiness, endpoints)
9. Document entity relationships (Deployment → Service Instance, Deployment Package → Deployment, Deployment Package → Secrets/Config)
10. Add state transitions for pod lifecycle (Pending → Running → Ready → Terminating)

**Output**: data-model.md with all Kubernetes entities documented

---

### Task: Generate API contracts

**Input**: Functional requirements from feature specification
**Approach**: Define backend API endpoints required for Kubernetes deployment (health checks)

### Subtasks

1. Define GET /health endpoint contract (returns 200 with status and timestamp)
2. Define GET /ready endpoint contract (returns 200 with database and MCP status, or 503 if not ready)
3. Document response schemas for health and readiness endpoints
4. Define error response formats (500 server error, 503 not ready)
5. Document probe configuration requirements (initial delay, period, timeout, thresholds)
6. Generate OpenAPI specification fragment for health endpoints
7. Export to /contracts/backend-health.yaml

**Output**: /contracts/backend-health.yaml

---

### Task: Create quickstart.md

**Input**: User stories from feature specification (P1: First-Time Deployment)
**Approach**: Step-by-step guide for developers to deploy application

### Subtasks

1. Document Minikube prerequisites (Docker, kubectl, Helm installation)
2. Document cluster startup: `minikube start --cpus=4 --memory=8192`
3. Document Docker image build commands for frontend
4. Document Docker image build commands for backend
5. Document local image loading to Minikube (if needed for local builds)
6. Document Helm chart installation: `helm install todo-app ./helm/todo-chart --values values-local.yaml`
7. Document secret creation from existing secrets
8. Document service access: `minikube service todo-frontend --url`
9. Document verification steps (pod status, health checks)
10. Document troubleshooting commands with AI tools (kubectl-ai, kagent)

**Output**: quickstart.md with complete deployment guide

---

### Task: Update agent context

**Input**: Technology stack from Technical Context section
**Approach**: Add Docker, Helm, Kubernetes technologies to agent context

### Subtasks

1. Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`
2. Verify Docker configuration added to context
3. Verify Helm configuration added to context
4. Verify Kubernetes configuration added to context
5. Verify Minikube configuration added to context
6. Verify uv configuration maintained (Python package manager)
7. Verify Next.js and FastAPI maintained as primary technologies

**Output**: Updated agent context file with new technologies

---

## Re-evaluation

### Post-Design Constitution Check

**Stateless Design**: ✅ PASS - Using external database (Neon PostgreSQL)

**Separation of Concerns**: ✅ PASS - Clear separation between spec, contracts, infrastructure, and implementation

**No Manual Coding Rule**: ✅ PASS - All implementation will follow /sp.implement

**Specification Before Implementation**: ✅ PASS - Complete spec, contracts, and quickstart available

---

## Implementation Roadmap

### Phase 0 (Completed)
- ✅ Created plan.md

### Phase 1 (Ready for /sp.tasks)
1. Create research.md (document all technology choices)
2. Create data-model.md (Kubernetes entities and relationships)
3. Generate API contracts (health endpoints)
4. Create quickstart.md (deployment guide)
5. Update agent context (add Docker, Helm, Kubernetes)

### Phase 2 (Execution)
- Create Dockerfiles (frontend and backend)
- Create .dockerignore files
- Create Helm chart (Chart.yaml, values.yaml, templates)
- Implement health check endpoints (/health, /ready)
- Build and test container images
- Deploy to Minikube
- Test with AI DevOps tools

---

## Dependencies

**Internal**:
- Feature specification (spec.md) - COMPLETE
- Constitution (.specify/memory/constitution.md) - COMPLIANT
- Phase 0 research (research.md) - PENDING
- Phase 1 contracts (/contracts/) - PENDING
- Phase 1 data-model (data-model.md) - PENDING
- Phase 1 quickstart (quickstart.md) - PENDING

**External**:
- Docker Desktop 4.53+ - Required
- Minikube - Required
- Helm 3.x - Required
- kubectl - Required
- Neon PostgreSQL connection - Required (existing from Phase II)
- OpenAI API key - Required (existing from Phase III)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|-------|---------|------------|
| Insufficient local machine resources for Minikube | Deployment failures | Document 4CPU/8GB minimum, suggest alternative Kind/K3d |
| Docker build cache pollution from node_modules | Large images | Add .dockerignore files, use multi-stage builds |
| Port conflicts on host | Service access failure | Document dynamic port assignment or port conflict resolution |
| Helm chart template errors | Deployment failures | Validate templates with `helm lint` before deployment |
| AI tool unavailability (kubectl-ai, kagent) | Extended troubleshooting time | Document manual alternatives for common issues |

---

## Next Steps

1. Execute Phase 0: Generate research.md by addressing technology choices and best practices
2. Execute Phase 1: Create design artifacts (data-model, contracts, quickstart, update agent context)
3. Execute Phase 2: Generate tasks.md via `/sp.tasks` command
4. Begin implementation via `/sp.implement` command
