<div align="center">

# ⚙️ ProjectPulse AI — Backend Core Services

**Asynchronous FastAPI Microservice • TimescaleDB Time-Series Persistence • Groq LLM Decision Intelligence**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-TimescaleDB-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%20(Async)-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Redis](https://img.shields.io/badge/Redis-AsyncIO-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io)
[![Groq](https://img.shields.io/badge/Groq-AI%20Inference-F05032?style=flat)](https://groq.com)
[![Pytest](https://img.shields.io/badge/Tests-Passing-46A2F0?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org)

</div>

---

## 📖 Table of Contents

- [Backend Architecture Overview](#-backend-architecture-overview)
- [Module & Directory Breakdown](#-module--directory-breakdown)
- [Core Subsystems & Internal Mechanics](#-core-subsystems--internal-mechanics)
  - [1. Data Access & Repositories](#1-data-access--repositories)
  - [2. Caching Layer (`CachePort`)](#2-caching-layer-cacheport)
  - [3. Early Warning Alert Engine](#3-early-warning-alert-engine)
  - [4. AI Assistant Service (Groq Integration)](#4-ai-assistant-service-groq-integration)
  - [5. Document Ingestion Pipeline](#5-document-ingestion-pipeline)
- [Database Models & Hypertables](#-database-models--hypertables)
- [API Endpoints Reference](#-api-endpoints-reference)
- [Environment Configuration](#-environment-configuration)
- [Local Development & Setup](#-local-development--setup)
- [Running the Backend](#-running-the-backend)
- [Testing & Quality Assurance](#-testing--quality-assurance)

---

## 🏗 Backend Architecture Overview

The backend is built around **Clean Architecture** and **Domain-Driven Design (DDD)** principles, separating presentation, business logic, data persistence, and external adapters:

```mermaid
flowchart TD
    subgraph Presentation["Presentation & API Layer (services/api/routes)"]
        R_Dash["dashboard.py\n• /api/v1/dashboard/*"]
        R_Proj["projects.py\n• /api/v1/projects/*"]
        R_Alert["alerts.py\n• /api/v1/alerts/*"]
        R_AI["assistant.py\n• /api/v1/assistant/*"]
    end

    subgraph Middleware["Middleware Pipeline (services/api/middleware)"]
        ReqId["RequestIdMiddleware\n(Correlation ID Tracing)"]
        SecHeaders["SecurityHeaders\n(nosniff, DENY, GZip)"]
    end

    subgraph CoreServices["Domain & Service Layer (services/api/services)"]
        S_Proj["ProjectService\n(Pagination, Filtering, Aggregations)"]
        S_Alert["AlertEngine\n(Rule Evaluation & Anomaly Detection)"]
        S_AI["AssistantService\n(Prompt Grounding & Groq LLM Inference)"]
    end

    subgraph DataLayer["Persistence & Ports (services/api/repositories & core)"]
        Repo_Proj["ProjectRepository"]
        Repo_Alert["AlertRepository"]
        Cache["CachePort\n(RedisCache / InMemoryCache Fallback)"]
    end

    subgraph Infrastructure["Infrastructure & Storage"]
        DB[(PostgreSQL / TimescaleDB)]
        Redis[(Redis Cache)]
    end

    Middleware --> Presentation
    R_Dash & R_Proj --> S_Proj
    R_Alert --> S_Alert
    R_AI --> S_AI

    S_Proj --> Repo_Proj
    S_Proj --> Cache
    S_Alert --> Repo_Alert
    S_AI --> Repo_Proj

    Repo_Proj --> DB
    Repo_Alert --> DB
    Cache -.-> Redis
```

---

## 📁 Module & Directory Breakdown

```text
backend/
├── .env.example                  # Environment variable template
├── Makefile                      # CLI automation commands
├── pytest.ini                    # Pytest path and async test runner configuration
├── requirements.txt              # Backend dependencies
├── README.md                     # Backend developer documentation
│
├── data/                         # Local storage for ingestion artifacts
│   ├── raw/                      # Raw incoming project reports (.pdf, .xlsx)
│   └── staging/                  # Normalized JSON / intermediate CSV data
│
├── services/
│   ├── __init__.py
│   │
│   ├── api/                      # Main FastAPI Web Application
│   │   ├── __init__.py
│   │   ├── main.py               # Application factory, lifespan, CORS, middleware assembly
│   │   ├── dependencies.py       # FastAPI dependency injection providers (Services, Repos, DB)
│   │   │
│   │   ├── core/                 # Cross-Cutting Infrastructure Concerns
│   │   │   ├── cache.py          # Abstract CachePort, RedisCache (asyncio) & InMemoryCache
│   │   │   ├── errors.py         # Standardized exception hierarchy (AppException, NotFoundError)
│   │   │   ├── logging.py        # Centralized structured logger with request correlation
│   │   │   └── resilience.py     # Retry policies (Tenacity) & execution wrappers
│   │   │
│   │   ├── db/                   # Database Engine & Connection Management
│   │   │   ├── __init__.py
│   │   │   └── session.py        # Async SQLAlchemy engine, session maker & health probe
│   │   │
│   │   ├── middleware/           # HTTP Request/Response Middlewares
│   │   │   └── request_id.py     # Injects X-Request-ID and tracks request duration
│   │   │
│   │   ├── models/               # SQLAlchemy 2.0 Declarative ORM Models
│   │   │   ├── __init__.py
│   │   │   └── db.py             # Projects, Snapshots, RiskScores, Alerts, IngestionRuns
│   │   │
│   │   ├── repositories/         # Database Query Abstraction (Data Access Layer)
│   │   │   ├── alert_repo.py     # Alert querying, creation, status updates
│   │   │   └── project_repo.py   # Keyset/offset pagination, multi-field filters, search
│   │   │
│   │   ├── routes/               # API Route Controllers
│   │   │   ├── __init__.py
│   │   │   ├── alerts.py         # Alert retrieval and engine execution endpoints
│   │   │   ├── assistant.py      # AI assistant natural language query endpoint
│   │   │   ├── dashboard.py      # Executive summary, monthly trends, top priorities
│   │   │   └── projects.py       # Project listing and detailed project views
│   │   │
│   │   └── services/             # Core Business Logic
│   │       ├── alert_service.py  # Anomaly detection and threshold alert generator
│   │       ├── assistant_service.py # Groq LLM integration and context synthesis
│   │       └── project_service.py   # Business operations on infrastructure projects
│   │
│   └── ingestion/                # Document Ingestion Pipeline
│       ├── __init__.py
│       └── loaders/
│           ├── __init__.py
│           └── db_loader.py      # Multi-format document parser & DB upsert loader
│
└── tests/                        # Automated Test Suite
    ├── __init__.py
    └── test_api.py               # Asynchronous API integration tests
```

---

## ⚙️ Core Subsystems & Internal Mechanics

### 1. Data Access & Repositories
- **Pattern**: Repository Pattern separates raw SQL/ORM mechanics from business services.
- **Query Optimization**: Complex analytics in `routes/dashboard.py` utilize SQL **Common Table Expressions (CTEs)** and window functions (`ROW_NUMBER() OVER (...)`) to fetch only the latest reporting period snapshot per project in a single indexed query.
- **Pagination**: Supports both traditional offset pagination (`page`, `limit`) and high-throughput cursor keyset pagination for infinite scrolling.

---

### 2. Caching Layer (`CachePort`)
Implemented in [`services/api/core/cache.py`](file:///c:/Users/Sk%20Nooruddin/PROJECTPULSE_AI/backend/services/api/core/cache.py):
- **Interface**: Abstract Base Class `CachePort` exposes async `get()`, `setex()`, `delete()`, and `clear_pattern()`.
- **Primary Driver**: `RedisCache` utilizes `redis.asyncio` with connection pooling and JSON serialization.
- **Offline Fallback**: If Redis is not running or encounters a connection error during startup, the system automatically initializes `InMemoryCache` (with TTL expiry tracking). This ensures local development works immediately without spinning up a Redis container.

---

### 3. Early Warning Alert Engine
Implemented in [`services/api/services/alert_service.py`](file:///c:/Users/Sk%20Nooruddin/PROJECTPULSE_AI/backend/services/api/services/alert_service.py):
- Evaluates project snapshots against risk rules:
  1. **Cost Overrun Velocity**: Cumulative expenditure exceeding original sanctioned budget by $>15\%$.
  2. **Schedule Slippage**: Revised completion date delayed by $>12\text{ months}$ beyond original target.
  3. **Stagnation Anomaly**: 3 consecutive reporting periods with $<1\%$ physical progress change while expenditure continues.
- Alerts are persisted to the database with severities (`critical`, `high`, `moderate`) and lifecycle states (`open`, `acknowledged`, `resolved`).

---

### 4. AI Assistant Service (Groq Integration)
Implemented in [`services/api/services/assistant_service.py`](file:///c:/Users/Sk%20Nooruddin/PROJECTPULSE_AI/backend/services/api/services/assistant_service.py):
- Connects to the **Groq Cloud API** using high-speed Llama 3 models.
- **Grounded Synthesis**: Extracts structured filters from the user's natural language question, executes safe, scoped SQL queries against the local repository, and formats a synthesized briefing with citations and exact metrics.

---

### 5. Document Ingestion Pipeline
Implemented in [`services/ingestion/loaders/db_loader.py`](file:///c:/Users/Sk%20Nooruddin/PROJECTPULSE_AI/backend/services/ingestion/loaders/db_loader.py):
- Ingests semi-structured Monthly Progress Reports (MPRs):
  - **PDF Documents**: Parsed with `pdfplumber` (text streams) and `camelot-py` (vector table extraction).
  - **Spreadsheets**: Parsed with `openpyxl`.
- Implements idempotent upserts using SHA-256 source content hashing to prevent duplicate snapshot records.

---

## 🗄 Database Models & Hypertables

Models are declared in [`services/api/models/db.py`](file:///c:/Users/Sk%20Nooruddin/PROJECTPULSE_AI/backend/services/api/models/db.py):

| Table | Purpose | Key Columns / Indexes |
| :--- | :--- | :--- |
| `projects` | Project Master entity | `project_id` (PK), `project_name`, `sector`, `ministry`, `state`, `original_cost` |
| `project_snapshots` | Time-series monthly snapshots *(TimescaleDB Hypertable)* | `snapshot_id` (PK), `project_id` (FK), `report_month`, `physical_progress`, `revised_cost` |
| `project_features` | Extracted ML features *(JSONB)* | `feature_id` (PK), `project_id` (FK), `report_month`, `features` (JSONB) |
| `risk_scores` | Model risk predictions | `risk_id` (PK), `project_id` (FK), `composite_score`, `tier`, `predicted_delay_months` |
| `alerts` | Anomaly early warnings | `alert_id` (PK), `project_id` (FK), `alert_type`, `severity`, `status` |
| `ingestion_runs` | Ingestion audit log | `run_id` (PK), `source_file_name`, `records_processed`, `executed_at` |

---

## 📡 API Endpoints Reference

### Base URL: `http://localhost:8000`

### 1. System Endpoints
- `GET /` — API root greeting with documentation links.
- `GET /health` — Active health probe checking database connectivity and echoing request ID.

### 2. Executive Dashboard (`/api/v1/dashboard`)
- `GET /api/v1/dashboard/summary` — High-level portfolio counts, total cost, and capital at risk *(Cached 60s)*.
- `GET /api/v1/dashboard/changes` — Month-over-month trajectory (new critical/high projects, deterioration magnitude) *(Cached 60s)*.
- `GET /api/v1/dashboard/priorities?limit=10` — Top projects needing intervention ranked by risk velocity and exposure.

### 3. Infrastructure Projects (`/api/v1/projects`)
- `GET /api/v1/projects` — Filtered project list.
  - Query parameters: `page`, `limit`, `cursor`, `ministry`, `sector`, `state`, `tier`, `search`.
- `GET /api/v1/projects/{project_id}` — Detailed view of a single project.

### 4. Alert Engine (`/api/v1/alerts`)
- `GET /api/v1/alerts` — List alerts filtered by `status` (`open`, `acknowledged`, `resolved`) and `severity`.
- `POST /api/v1/alerts/run-engine` — Trigger immediate risk rule evaluation across all projects.

### 5. AI Assistant (`/api/v1/assistant`)
- `POST /api/v1/assistant/query` — Grounded conversational Q&A endpoint.
  - Body: `{"query": "Which road projects in UP have budget overruns?"}`

---

## ⚙️ Environment Configuration

Create `.env` in `backend/` from the template:

```bash
cp .env.example .env
```

```ini
# Database Connection (PostgreSQL / TimescaleDB)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/projectpulse
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30.0
DB_POOL_RECYCLE=1800

# Redis Cache (Optional - falls back to in-memory cache if omitted)
REDIS_URL=redis://localhost:6379/0

# LLM & External AI Services
GROQ_API_KEY=your_groq_api_key_here

# Security & Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 🚀 Local Development & Setup

### 1. Create Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv_backend
.\venv_backend\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv_backend
source venv_backend/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚡ Running the Backend

Ensure you are inside the `backend/` directory:

```bash
# Using Makefile
make run

# Or directly with Uvicorn
uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Interactive Documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testing & Quality Assurance

Run the automated test suite with `pytest`:

```bash
# Run tests
python -m pytest

# Run tests with verbose output
python -m pytest -v
```

All test cases leverage `httpx.AsyncClient` with `ASGITransport` for in-memory, zero-network async API testing.
