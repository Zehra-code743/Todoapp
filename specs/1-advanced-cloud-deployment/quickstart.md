# Quickstart Guide: Advanced Cloud Deployment with Event-Driven Architecture

## Overview
This guide provides a step-by-step approach to setting up the advanced todo application with event-driven architecture using Kafka and Dapr, deployed to Kubernetes.

## Prerequisites
- Docker and Docker Compose
- Kubernetes cluster (Minikube for local development, AKS/GKE/DOKS for cloud)
- kubectl
- Helm
- Dapr CLI
- Git

## Local Development Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Initialize Dapr
```bash
# For local development
dapr init

# For Kubernetes
dapr init -k
```

### 3. Set Up Kafka with Strimzi (Local)
```bash
# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka

# Deploy Kafka cluster
kubectl apply -f ./k8s/kafka/kafka-cluster.yaml

# Create topics
kubectl apply -f ./k8s/kafka/kafka-topics.yaml
```

### 4. Deploy Dapr Components
```bash
kubectl apply -f ./dapr-components/pubsub.yaml
kubectl apply -f ./dapr-components/statestore.yaml
kubectl apply -f ./dapr-components/secrets.yaml
```

### 5. Build and Deploy Services
```bash
# Build Docker images
docker build -t todo-chat-service ./services/chat
docker build -t todo-task-service ./services/task
docker build -t todo-notification-service ./services/notification
docker build -t todo-recurring-service ./services/recurring

# Deploy to Kubernetes
kubectl apply -f ./k8s/deployments/
```

## Cloud Deployment Setup

### 1. Choose Cloud Provider
We recommend DigitalOcean for its simplicity and generous free tier:
- $200 credit for 60 days
- Easy Kubernetes setup
- Integrated load balancer

### 2. Create Kubernetes Cluster
For DigitalOcean:
```bash
doctl kubernetes cluster create todo-production --region <region> --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3"
doctl kubernetes cluster kubeconfig save todo-production
```

### 3. Set Up Cloud Resources
- Set up managed Kafka (Redpanda Cloud or Confluent Cloud)
- Configure secrets in cloud provider
- Set up monitoring and logging

### 4. Update Configuration
Update Dapr components to point to cloud resources:
- Update Kafka connection details
- Update database connection strings
- Update API keys and secrets

## Service Architecture

### 1. Chat API Service
- Handles user requests via chat interface
- Communicates with other services via Dapr service invocation
- Uses Dapr secrets for API keys

### 2. Task Service (MCP Server)
- Core task CRUD operations
- Publishes events to Kafka via Dapr pub/sub
- Stores task data in PostgreSQL
- Implements advanced features (priorities, tags, etc.)

### 3. Notification Service
- Consumes reminder events from Kafka
- Schedules Dapr jobs for timed notifications
- Sends notifications via configured channels

### 4. Recurring Task Service
- Consumes task completion events from Kafka
- Creates new task instances based on recurrence patterns
- Publishes new task events

## Event Flows

### Task Creation Flow
1. Chat API receives task creation request
2. Invokes Task Service via Dapr service invocation
3. Task Service creates task in database
4. Task Service publishes `task.created` event to Kafka via Dapr pub/sub
5. If due date with reminder set, Task Service publishes `reminder.scheduled` event

### Task Completion Flow
1. Task Service marks task as completed
2. Task Service publishes `task.completed` event to Kafka
3. If task is recurring, Recurring Task Service creates new instance
4. Notification Service processes any pending reminders for the task

## MCP Tool Extensions

The following MCP tools are extended to support new features:

- `create_task`: Extended with priority, tags, due_date, recurrence, and reminder parameters
- `update_task`: Extended to update new attributes
- `search_tasks`: New tool for full-text search
- `filter_tasks`: New tool for filtering by multiple criteria
- `sort_tasks`: New tool for sorting tasks by different fields

## Monitoring and Observability

- Use Dapr's built-in metrics
- Monitor Kafka consumer lag
- Track service health and response times
- Set up alerts for critical failures
- Use distributed tracing to track requests across services

## Troubleshooting

### Common Issues
- Dapr sidecar not starting: Check if Dapr runtime is installed
- Kafka connectivity issues: Verify Kafka cluster is running and accessible
- Service-to-service communication: Ensure Dapr service invocation is configured correctly
- Database connection issues: Verify database credentials and network access

### Debugging Tips
- Use `dapr logs` to check service logs
- Monitor Kafka topics with `kafka-console-consumer`
- Use Dapr dashboard to visualize service interactions
- Enable debug logging for detailed tracing