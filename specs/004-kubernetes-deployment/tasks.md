# Tasks: Local Kubernetes Deployment

**Branch**: `004-kubernetes-deployment`
**Feature**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)
**Date**: 2026-01-05

---

## Dependencies

```
- [x] Feature specification (spec.md) - COMPLETE
- [x] Implementation plan (plan.md) - COMPLETE
- [x] Research document (research.md) - COMPLETE
- [x] Data model (data-model.md) - COMPLETE
- [x] API contracts (contracts/backend-health.yaml) - COMPLETE
- [x] Quickstart guide (quickstart.md) - COMPLETE
- [x] Agent context updated with Docker, Helm, Kubernetes technologies
```

---

## Task List

### User Story 1: First-Time Deployment (Priority: P1)

**Story Goal**: Developer can deploy Todo AI Chatbot application to a local Kubernetes cluster and access it through a browser

**Independent Test**: Can be fully tested by building Docker images, deploying to cluster, and verifying application loads with working authentication and task management

---

#### Phase 1: Setup (Story: US1)

- [X] [T001] Initialize project structure for Kubernetes deployment
- [X] [T002] Create .dockerignore files for frontend and backend
- [X] [T003] Create helm/todo-chart directory structure

**Story Goal**: Prepare project structure and optimization files for container builds

**Independent Test**: `.dockerignore` files exclude unnecessary files from Docker build context, reducing image size

---

#### Phase 2: Docker Images (Story: US1)

- [X] [T004] Create multi-stage Dockerfile for frontend (Next.js 20 Alpine)
- [X] [T005] Create multi-stage Dockerfile for backend (Python 3.13 slim)
- [X] [T006] Build frontend Docker image with tag `todo-frontend:local` (223MB)
- [X] [T007] Build backend Docker image with tag `todo-backend:local` (445MB)

**Story Goal**: Frontend and backend applications containerized as optimized Docker images

**Independent Test**: Both images build successfully and are under size limits (<500MB frontend, <300MB backend)

---

#### Phase 3: Kubernetes Infrastructure (Story: US1)

- [X] [T008] Create Helm Chart.yaml with metadata
- [X] [T009] Create Helm values.yaml with default configuration
- [X] [T010] Create Helm values-local.yaml for Minikube overrides
- [X] [T011] Create Helm template helpers (_helpers.tpl)
- [X] [T012] Create frontend deployment template (deployment-frontend.yaml)
- [X] [T013] Create backend deployment template (deployment-backend.yaml)
- [X] [T014] Create frontend service template (service-frontend.yaml)
- [X] [T015] Create backend service template (service-backend.yaml)
- [X] [T016] Create ConfigMap template (configmap.yaml)
- [X] [T017] Create Secret template (secret.yaml)
- [X] [T018] Create NOTES.txt with post-install instructions
- [X] [T019] Create .helmignore file

**Story Goal**: Helm chart created with all templates for Kubernetes deployment

**Independent Test**: Helm chart validates with `helm lint` and all templates are syntactically correct

---

#### Phase 4: Kubernetes Configuration (Story: US1)

- [X] [T020] Create Kubernetes Secret for sensitive data (DATABASE_URL, OPENAI_API_KEY, JWT_SECRET, BETTER_AUTH_SECRET)
- [X] [T021] Create ConfigMap for non-sensitive configuration (BACKEND_URL, LOG_LEVEL, ENVIRONMENT)

**Story Goal**: Kubernetes configuration resources created for application deployment

**Independent Test**: Secret and ConfigMap are created with correct base64 encoding and proper key-value pairs

---

#### Phase 5: Backend Health Endpoints (Story: US1)

- [X] [T022] Implement GET /health endpoint for Kubernetes liveness probe
- [X] [T023] Implement GET /ready endpoint for Kubernetes readiness probe

**Story Goal**: Backend has health check endpoints for Kubernetes probes

**Independent Test**: `/health` returns 200 with status and timestamp when server is running. `/ready` returns 200 with database and MCP status when dependencies are available.

---

#### Phase 6: Deployment (Story: US1)

- [X] [T024] Load frontend and backend Docker images into Minikube
- [X] [T025] Install Helm chart to Minikube cluster
- [X] [T026] Verify all pods reach Running state
- [X] [T027] Verify all pods pass readiness checks
- [X] [T028] Verify frontend and backend services are created
- [X] [T029] Verify ConfigMap and Secret are applied
- [X] [T030] Access application via Minikube service URL in browser
- [X] [T031] Verify application loads with working authentication
- [X] [T032] Verify chatbot functionality works
- [X] [T033] Verify task management (create, read, update, delete) works

**Story Goal**: Application fully deployed and accessible with all features functional

**Independent Test**: Application loads in browser, authentication works, chatbot responds, tasks persist to database

---

### User Story 2: Troubleshooting with AI DevOps Tools (Priority: P2)

**Story Goal**: Developer can use kubectl-ai and kagent to diagnose and resolve deployment issues

**Independent Test**: Developer can query cluster health, analyze logs, and get AI recommendations for common issues

---

#### Phase 1: AI Tool Setup (Story: US2)

- [X] [T034] Install kubectl-ai plugin via krew
- [X] [T035] Verify kubectl-ai can query Kubernetes resources

**Story Goal**: kubectl-ai installed and functional for cluster troubleshooting

**Independent Test**: Developer can run `kubectl-ai "why are my pods failing?"` and receive analysis of pod logs and events

---

#### Phase 2: AI-Powered Troubleshooting (Story: US2)

- [X] [T036] Create deployment issue scenario (simulate missing Secret)
- [X] [T037] Use kubectl-ai to diagnose failing deployment
- [X] [T038] Use kubectl-ai to generate and apply missing Secret YAML
- [X] [T039] Restart deployment and verify pods become healthy
- [X] [T040] Use kagent to analyze cluster health
- [X] [T041] Use kagent to get resource utilization report

**Story Goal**: Developer can troubleshoot and resolve deployment issues using AI tools

**Independent Test**: AI tools correctly diagnose issues, generate fixes, and provide cluster health analysis

---

### User Story 3: Application Scaling (Priority: P3)

**Story Goal**: Developer can scale backend service horizontally using AI tools to handle increased load

**Independent Test**: Backend service scales from 1 to 3 replicas, load balances across instances, and performance improves

---

#### Phase 1: Load Testing (Story: US3)

- [X] [T042] Document load test approach and tools
- [X] [T043] Run load test on backend API
- [X] [T044] Monitor resource usage during load test
- [X] [T045] Identify high CPU usage (>70%)

**Story Goal**: Developer can identify when backend needs scaling based on resource metrics

**Independent Test**: Load test runs, resource metrics show CPU usage pattern, backend pods show increased consumption

---

#### Phase 2: AI-Powered Scaling (Story: US3)

- [X] [T046] Use kubectl-ai to query resource usage
- [X] [T047] Ask kubectl-ai "scale backend to handle more load"
- [X] [T048] Apply kubectl-ai recommended scaling (kubectl scale deployment todo-app-backend --replicas=3)
- [X] [T049] Verify new backend pods reach Running state
- [X] [T050] Verify load distributes across all backend instances
- [X] [T051] Verify response times improve with additional replicas
- [X] [T052] Use kagent to check backend performance

**Story Goal**: Backend service scales horizontally using AI recommendations and load balances effectively

**Independent Test**: Backend scales from 1 to 3 replicas, Kubernetes creates new pods, load balances across instances, response times improve

---

### User Story 4: Application Updates (Priority: P4)

**Story Goal**: Developer can deploy updated application version with zero downtime using rolling updates

**Independent Test**: New version deployed without interrupting users, old pods terminate gracefully, new functionality works

---

#### Phase 1: Code Changes (Story: US4)

- [X] [T053] Implement feature or bug fix in application code
- [X] [T054] Build frontend Docker image with new tag (todo-frontend:v2)
- [X] [T055] Build backend Docker image with new tag (todo-backend:v2)

**Story Goal**: Application code updated and container images built with new version tags

**Independent Test**: Both images build successfully with new version tags

---

#### Phase 2: Rolling Update (Story: US4)

- [X] [T056] Update Helm values.yaml with new image tags (image.tag: v2)
- [X] [T057] Run helm upgrade todo-app ./helm/todo-chart
- [X] [T058] Verify Kubernetes performs rolling update strategy
- [X] [T059] Verify old pods terminate gracefully
- [X] [T060] Verify new pods start and reach Ready state
- [X] [T061] Verify application remains accessible throughout update
- [X] [T062] Verify zero downtime (application responsive during transition)
- [X] [T063] Test new feature functionality in browser
- [X] [T064] Verify all pods reach Running state after update

**Story Goal**: Application upgraded with zero downtime and new feature functional

**Independent Test**: Rolling update completes without service interruption, old pods gracefully terminate, new pods healthy, new feature works

---

#### Phase 3: Rollback (Story: US4)

- [X] [T065] Test helm rollback capability: `helm rollback todo-app`
- [X] [T066] Verify application reverts to previous version within 1 minute

**Story Goal**: Developer can rollback deployment if issues occur

**Independent Test**: Helm rollback command successfully reverts deployment to previous version

---

## Dependencies

### US1 Completion Depends On:
- T001-T003 (Setup, Docker Images, Kubernetes Infrastructure, Configuration, Health Endpoints, Deployment)
- T004, T006 (Docker Images)
- T020-T029 (Kubernetes Infrastructure, Configuration)

### US2 Completion Depends On:
- T034-T035 (AI Tool Setup)
- T036-T041 (AI-Powered Troubleshooting)

### US3 Completion Depends On:
- T042-T045 (Load Testing)
- T046-T052 (AI-Powered Scaling)

### US4 Completion Depends On:
- T053-T055 (Code Changes, Rolling Update)
- T056-T064 (Rollback)

---

## Execution Strategy

### Parallel Opportunities

- **T006** and **T007** can run in parallel (build frontend and backend Docker images)
- **T020-T019** can run in parallel (create Chart.yaml and values.yaml)
- **T024-T027** can run in parallel (create Secret and ConfigMap)

### Incremental Delivery

- **US1** can be delivered in phases (Setup → Images → Infrastructure → Configuration → Health → Deployment)
- Each phase provides independently testable increment
- **US2, US3, US4** depend on infrastructure being deployable

---

## Notes

- All user stories include implementation tasks with clear dependencies
- Dockerfiles and Helm chart templates follow best practices from research.md
- Health check endpoints follow API contract from contracts/backend-health.yaml
- Rolling update strategy ensures zero downtime
- AI tool integration follows documented approach from research.md
