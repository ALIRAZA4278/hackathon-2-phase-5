# TaskFlow - Advanced Cloud-Native AI Todo Platform

> Phase V: Event-Driven AI Todo Chatbot with Kafka, Dapr Runtime, and Oracle OKE Deployment

Built entirely using **Spec-Driven Development (SDD)** with Claude Code - no manual coding.

## Architecture

```
                          KUBERNETES CLUSTER (Oracle OKE / Minikube)

  +---------------+   +------------------+   +---------------------------+
  |   Frontend    |   |    Backend Pod   |   |      KAFKA (Redpanda)     |
  |   Next.js     |-->|  FastAPI + Dapr  |-->|  todo.events              |
  |   + Dapr      |   |  AI Agent (13    |   |  reminder.events          |
  |   Sidecar     |   |  tools) + Dapr   |   |  recurring.events         |
  +---------------+   |  Sidecar         |   |  ai.events                |
                       +--------+---------+   |  audit.events             |
                                |             +-----------+---------------+
                                v                         |
                       +----------------+                 v
                       |   Neon DB      |   +---------------------------+
                       |  (PostgreSQL)  |   |     Event Consumers       |
                       +----------------+   |  - Reminder Consumer      |
                                            |  - Recurring Consumer     |
                                            |  - Audit Consumer         |
                                            |  - Notification Consumer  |
                                            +---------------------------+
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Better Auth |
| Backend | Python FastAPI, SQLModel, OpenAI Agents SDK |
| AI | Gemini API via OpenAI SDK provider bridge |
| Database | Neon Serverless PostgreSQL |
| Messaging | Kafka (Redpanda) via Dapr Pub/Sub |
| Runtime | Dapr (Pub/Sub, State, Bindings, Secrets, Service Invocation) |
| Container | Docker (multi-stage builds) |
| Orchestration | Kubernetes (Minikube + Oracle OKE) |
| Packaging | Helm 3 (9 charts + umbrella chart) |
| CI/CD | GitHub Actions (build, test, scan, push, deploy, rollback) |
| Observability | Prometheus, Grafana, OpenTelemetry, JSON structured logging |

## Features

### Part A: Advanced Features

- **Task Priorities**: Low, Medium, High, Urgent with color-coded badges
- **Tags**: Flexible tagging system with search across tags
- **Due Dates**: Date picker with overdue detection
- **Reminders**: Scheduled reminders with trigger notifications
- **Recurring Tasks**: Daily, weekly, monthly, custom cron expressions
- **Search**: Full-text search across title, description, and tags
- **Filter**: By status, priority, tags, date range, and combinations
- **Sort**: By due date, priority, created date, updated date (asc/desc)
- **AI Chatbot**: 13 tool functions via natural language (create, update, delete, complete, list, search, filter, sort, set priority, add tags, set due date, schedule reminder, create recurring)
- **Event-Driven Architecture**: All task operations emit events via Kafka/Dapr
- **Safety Guardrails**: Confirmation for destructive ops, rate limiting (200 req/min), prompt injection defense

### Part B: Local Deployment (Minikube)

- 9 Helm charts (backend, frontend, 4 consumers, redpanda, redis, observability)
- Umbrella chart for one-command deployment
- Full Dapr integration: Pub/Sub, State Store, Cron Bindings, Secrets, Service Invocation
- Dapr component YAMLs for all building blocks

### Part C: Cloud Deployment (Oracle OKE)

- CI/CD pipeline: build > test > scan > push > deploy > rollback
- GitHub Container Registry (ghcr.io) for images
- Oracle OKE with Dapr sidecars
- Automated rollback on deployment failure
- Prometheus + Grafana observability stack

## Project Structure

```
.
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # App entry, Prometheus metrics, CORS
│   │   ├── agent.py           # AI agent with 13 tool definitions
│   │   ├── mcp_tools.py       # Tool function implementations
│   │   ├── models.py          # SQLModel: Task, Reminder, AuditLog
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── config.py          # Settings (env vars)
│   │   ├── routes/
│   │   │   ├── tasks.py       # Task CRUD + search/filter/sort
│   │   │   ├── chat.py        # AI chat with rate limiting
│   │   │   └── events.py      # Dapr event subscriptions
│   │   └── events/
│   │       ├── schemas.py     # Event payload schemas
│   │       ├── topics.py      # Topic constants
│   │       └── producer.py    # Dapr pub/sub publisher
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Next.js frontend
│   ├── app/
│   │   ├── (auth)/            # Sign in / Sign up pages
│   │   ├── (app)/tasks/       # Task dashboard
│   │   └── api/               # Auth + token API routes
│   ├── components/
│   │   ├── ui/                # Button, Input, Card, Toast, Spinner
│   │   └── todo/              # TaskList, TaskCard, TaskForm, TaskSearch,
│   │                          # TaskFilters, TaskSort, DeleteConfirmModal
│   ├── lib/
│   │   ├── auth.ts            # Better Auth client
│   │   ├── auth-server.ts     # Better Auth server config
│   │   └── api.ts             # API client with JWT
│   ├── types/task.ts          # TypeScript interfaces
│   └── Dockerfile
├── consumers/                  # Event consumer microservices
│   ├── audit/                 # Audit log consumer
│   ├── notification/          # Notification consumer
│   ├── reminder/              # Reminder consumer
│   └── recurring/             # Recurring task consumer
├── dapr/                       # Dapr configuration
│   ├── config.yaml            # Tracing + metrics config
│   └── components/
│       ├── pubsub.yaml        # Kafka pub/sub (Redpanda)
│       ├── statestore.yaml    # Redis state store
│       ├── secretstore.yaml   # K8s secrets store
│       └── binding-cron.yaml  # Cron binding for schedules
├── helm/                       # Helm charts
│   ├── backend/               # Backend chart with Dapr sidecar
│   ├── frontend/              # Frontend chart with Dapr sidecar
│   ├── consumers/             # Consumer charts (4 services)
│   ├── infrastructure/
│   │   ├── redpanda/          # Kafka-compatible broker
│   │   ├── redis/             # State store backend
│   │   └── observability/     # Prometheus + Grafana
│   └── todo-app/              # Umbrella chart (all-in-one)
├── .github/workflows/
│   └── ci-cd.yaml             # 6-stage CI/CD pipeline
├── specs/                      # SDD specification artifacts
│   └── 002-cloud-native-platform/
│       ├── spec.md            # Feature specification
│       ├── plan.md            # Architecture plan
│       ├── tasks.md           # Implementation tasks (103 tasks)
│       └── quickstart.md      # Deployment quickstart
├── CLAUDE.md                   # Claude Code instructions
└── history/prompts/            # Prompt History Records (SDD audit trail)
```

## Spec-Driven Development (SDD) Workflow

This entire project was built using the SDD methodology:

```
1. /sp.constitution  -->  Project principles and constraints
2. /sp.specify       -->  Feature specification (spec.md)
3. /sp.plan          -->  Architecture plan (plan.md)
4. /sp.tasks         -->  103 implementation tasks (tasks.md)
5. /sp.implement     -->  Automated execution via Claude Code agents
6. /sp.git.commit_pr -->  Git commit and PR creation
```

Every user interaction is recorded as a **Prompt History Record (PHR)** in `history/prompts/`.

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker Desktop
- Minikube
- Helm 3.x
- Dapr CLI
- kubectl

### Quick Start (without Kubernetes)

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Environment Variables

**Backend** (`backend/.env`):
```
DATABASE_URL=postgresql://...@neon.tech/neondb?sslmode=require
GEMINI_API_KEY=your-gemini-api-key
BETTER_AUTH_SECRET=your-secret
FRONTEND_URL=http://localhost:3000
```

**Frontend** (`frontend/.env.local`):
```
BETTER_AUTH_SECRET=your-secret
DATABASE_URL=postgresql://...@neon.tech/neondb?sslmode=require
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Minikube Deployment (Part B)

```bash
# 1. Start Minikube
minikube start --memory=8192 --cpus=4

# 2. Initialize Dapr
dapr init --kubernetes --wait

# 3. Deploy infrastructure
helm install redpanda helm/infrastructure/redpanda/
helm install redis helm/infrastructure/redis/

# 4. Apply Dapr components
kubectl apply -f dapr/components/

# 5. Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="your-neon-url" \
  --from-literal=GEMINI_API_KEY="your-key" \
  --from-literal=BETTER_AUTH_SECRET="your-secret"

# 6. Deploy all services (umbrella chart)
helm install todo-app helm/todo-app/

# 7. Access the app
minikube service todo-frontend --url

# 8. (Optional) Deploy observability
helm install observability helm/infrastructure/observability/

# 9. Verify
kubectl get pods                # All should be Running
dapr components -k              # All Dapr components loaded
dapr dashboard -k               # Open Dapr dashboard
```

## Oracle OKE Deployment (Part C)

### Step 1: Create Oracle Cloud Account

1. Sign up at https://www.oracle.com/cloud/free/
2. Get Always Free tier: 4 OCPUs, 24GB RAM

### Step 2: Create OKE Cluster

```bash
# Install OCI CLI
# Windows: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm
# Or: pip install oci-cli

# Configure OCI CLI
oci setup config

# Create compartment (if needed)
oci iam compartment create --name todo-app --description "Todo App"

# Create OKE cluster via Console:
# 1. Go to Developer Services > Kubernetes Clusters (OKE)
# 2. Click "Create Cluster" > "Quick Create"
# 3. Select: Shape VM.Standard.A1.Flex (Always Free)
# 4. Nodes: 2, OCPUs: 2 per node, Memory: 12GB per node
# 5. Wait for cluster to be Active (~10 min)

# Download kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <your-cluster-ocid> \
  --file $HOME/.kube/config \
  --region <your-region> \
  --token-version 2.0.0

# Verify connection
kubectl get nodes
```

### Step 3: Install Dapr on OKE

```bash
# Initialize Dapr on the cluster
dapr init --kubernetes --wait

# Verify Dapr is running
dapr status -k
kubectl get pods -n dapr-system
```

### Step 4: Deploy Infrastructure

```bash
# Deploy Redpanda (Kafka-compatible)
helm install redpanda helm/infrastructure/redpanda/

# Deploy Redis (state store)
helm install redis helm/infrastructure/redis/

# Apply Dapr components
kubectl apply -f dapr/components/

# Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="your-neon-url" \
  --from-literal=GEMINI_API_KEY="your-key" \
  --from-literal=BETTER_AUTH_SECRET="your-secret"
```

### Step 5: Deploy Application

```bash
# Deploy everything with umbrella chart
helm install todo-app helm/todo-app/

# Watch pods come up
kubectl get pods -w

# Get frontend external URL
kubectl get svc todo-frontend
```

### Step 6: Configure CI/CD Secrets

Add these secrets to your GitHub repository (Settings > Secrets):

| Secret | Description |
|--------|-------------|
| `OKE_CLUSTER_OCID` | Your OKE cluster OCID |
| `OCI_REGION` | e.g., `us-ashburn-1` |
| `OCI_TENANCY_OCID` | Your tenancy OCID |
| `OCI_USER_OCID` | Your user OCID |
| `OCI_FINGERPRINT` | API key fingerprint |
| `OCI_PRIVATE_KEY` | API signing private key |

After configuring, every push to `main` triggers automated deployment.

## CI/CD Pipeline

```
Push to main
    |
    v
[Build] --> Build 6 Docker images (backend, frontend, 4 consumers)
    |
    v
[Test]  --> Python import check + TypeScript type check
[Scan]  --> Trivy vulnerability scanner (parallel with test)
    |
    v
[Push]  --> Push to ghcr.io (GitHub Container Registry)
    |
    v
[Deploy] --> helm upgrade --install to Oracle OKE
    |
    v
[Rollback] --> Auto-rollback on deploy failure
```

## Event-Driven Architecture

### Kafka Topics

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `todo.events` | Backend API | Audit, Notification | All task CRUD operations |
| `reminder.events` | Backend API | Reminder Consumer | Scheduled reminder triggers |
| `recurring.events` | Backend API | Recurring Consumer | Recurring task spawning |
| `ai.events` | AI Agent | Audit Consumer | AI tool call tracking |
| `audit.events` | All services | Audit Consumer | System audit trail |

### Event Flow

```
User Action (UI/Chat) --> Backend API --> Dapr Pub/Sub --> Kafka Topic --> Consumer Service
                                                                              |
                                                                              v
                                                                    Process + Store Result
```

## Dapr Building Blocks

| Block | Component | Purpose |
|-------|-----------|---------|
| Pub/Sub | `pubsub.kafka` (Redpanda) | Event messaging |
| State Store | `state.redis` | Conversation state, caching |
| Bindings | `bindings.cron` | Scheduled reminder checks |
| Secrets | `secretstores.kubernetes` | API keys, DB credentials |
| Service Invocation | Built-in | Frontend-to-backend communication |

## AI Chatbot Tools (13 Functions)

| Tool | Description |
|------|-------------|
| `add_task` | Create task with priority, tags, due date |
| `list_tasks` | List all user tasks |
| `search_tasks` | Search by keyword (title, description, tags) |
| `toggle_task_completion` | Mark task complete/incomplete |
| `delete_task` | Delete with confirmation flow |
| `set_due_date` | Set/update due date |
| `schedule_reminder` | Set reminder at specific time |
| `create_recurring` | Set recurring rule (daily/weekly/monthly) |
| `set_priority` | Change priority level |
| `add_tags` | Add tags with deduplication |
| `filter_tasks` | Filter by status/priority/tags/date |
| `sort_tasks` | Sort by any field |
| `update_task` | Partial update any field |

## Observability

- **Prometheus**: Metrics endpoint at `/metrics` on backend and all consumers
- **Grafana**: Pre-configured dashboards for service health, event flow, AI tool usage
- **Structured Logging**: JSON format with timestamp, level, service, message
- **OpenTelemetry**: Distributed tracing via Dapr

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List tasks (search, filter, sort) |
| POST | `/api/{user_id}/tasks` | Create task |
| GET | `/api/{user_id}/tasks/{id}` | Get single task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |
| POST | `/api/{user_id}/tasks/{id}/reminder` | Set reminder |
| DELETE | `/api/{user_id}/tasks/{id}/reminder` | Cancel reminder |
| POST | `/api/{user_id}/chat` | AI chatbot (rate limited) |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/dapr/subscribe` | Dapr subscription list |

## Security

- JWT authentication on every endpoint (Better Auth)
- User isolation: every query filtered by `user_id` from JWT
- AI tool ownership validation before execution
- Rate limiting: 200 requests/min per user on chat
- Prompt injection defense: 17 regex patterns strip injection phrases
- Secrets via Kubernetes Secrets (never in code)
- Non-root Docker containers
- Trivy vulnerability scanning in CI/CD

## Troubleshooting

```bash
# Check pod status
kubectl get pods

# View backend logs
kubectl logs -f deployment/todo-backend -c todo-backend

# View Dapr sidecar logs
kubectl logs -f deployment/todo-backend -c daprd

# Check Dapr components
dapr components -k

# Dapr dashboard
dapr dashboard -k

# Helm release status
helm list
helm status todo-app
```

## License

MIT
