<div align="center">

# 🚀 ProjectPulse AI

**Intelligent Government Infrastructure Monitoring & Early Warning Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-TimescaleDB-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%20(Async)-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Redis](https://img.shields.io/badge/Redis-AsyncIO-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io)
[![Groq](https://img.shields.io/badge/Groq-Llama%203%20Inference-F05032?style=flat)](https://groq.com)
[![Pytest](https://img.shields.io/badge/Tests-Passing-46A2F0?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<p align="center">
  <b>ProjectPulse AI</b> is an enterprise-grade AI decision support and early warning system designed for monitoring, risk quantification, and anomaly detection across central and state-level infrastructure projects.
</p>

</div>

---

## 📖 Table of Contents

- [Executive Overview](#-executive-overview)
- [System Architecture](#-system-architecture)
- [Mathematical Risk & Priority Formulation](#-mathematical-risk--priority-formulation)
- [Database Schema & Data Models](#-database-schema--data-models)
- [Data Ingestion & Extraction Pipeline](#-data-ingestion--extraction-pipeline)
- [AI Assistant & Guardrail System](#-ai-assistant--guardrail-system)
- [Monorepo Directory Structure](#-monorepo-directory-structure)
- [Tech Stack & Architecture Decisions](#-tech-stack--architecture-decisions)
- [Environment Variables Configuration](#-environment-variables-configuration)
- [Local Installation & Setup](#-local-installation--setup)
- [Running the Services](#-running-the-services)
- [API Reference & Sample Payloads](#-api-reference--sample-payloads)
- [Resilience, Observability & Caching](#-resilience-observability--caching)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Contribution & Git Workflow](#-contribution--git-workflow)

---

## 🏛 Executive Overview

Infrastructure initiatives frequently suffer from **unreported cost overruns**, **unforeseen timeline slippages**, and **fragmented reporting across ministries**.

**ProjectPulse AI** bridges this gap through:
1. **Automated Document Ingestion**: Ingesting monthly progress reports (MPRs), PDFs, and Excel tables directly into structured time-series snapshots.
2. **Quantified Early-Warning Risk Engine (P-Score)**: Calculating dynamic composite risk metrics spanning expenditure velocity, milestone slippage, and historical contractor performance.
3. **Executive Decision Intelligence**: Aggregating total capital at risk, tracking month-over-month trajectory changes, and prioritizing projects requiring urgent intervention.
4. **Conversational AI Query Agent**: Grounded natural-language query engine powered by Groq LLM and scoped SQL generation.

---

## 🏗 System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["Client & Consumers"]
        UI["Web Dashboard / React Frontend"]
        External["External Government Portals"]
    end

    subgraph APILayer["FastAPI Application Layer (services/api)"]
        direction TB
        MW["Middleware Pipeline\n(RequestId, GZip, CORS, Security Headers)"]
        
        subgraph Routers["API Routers"]
            R_Dash["/api/v1/dashboard"]
            R_Proj["/api/v1/projects"]
            R_Alert["/api/v1/alerts"]
            R_AI["/api/v1/assistant"]
            R_Health["/health"]
        end
    end

    subgraph ServiceLayer["Business Logic & Service Layer"]
        S_Proj["ProjectService"]
        S_Alert["AlertEngine"]
        S_AI["AssistantService (Groq LLM)"]
    end

    subgraph DataAccess["Persistence & Cache Ports"]
        Repo_Proj["ProjectRepository"]
        Repo_Alert["AlertRepository"]
        
        subgraph CachePort["Cache Abstraction Layer"]
            RedisClient["RedisCache (redis.asyncio)"]
            MemClient["InMemoryCache (Fallback)"]
        end
    end

    subgraph StorageLayer["Data Storage Engine"]
        Postgres["PostgreSQL / TimescaleDB\n(Hypertables: project_snapshots)"]
        RedisDB[("Redis Store")]
    end

    subgraph IngestionSystem["Ingestion Pipeline (services/ingestion)"]
        RawDocs["Monthly PDF / Excel Reports"] --> Parser["Document Parsers\n(pdfplumber / camelot-py / openpyxl)"]
        Parser --> Staging["Staging & Validation"]
        Staging --> DBLoader["DBLoader (Postgres Batch Upsert)"]
        DBLoader --> Postgres
    end

    UI & External --> MW
    MW --> Routers
    R_Dash --> S_Proj
    R_Proj --> S_Proj
    R_Alert --> S_Alert
    R_AI --> S_AI
    
    S_Proj --> Repo_Proj
    S_Proj --> CachePort
    S_Alert --> Repo_Alert
    S_AI --> Repo_Proj
    
    Repo_Proj --> Postgres
    Repo_Alert --> Postgres
    CachePort -. Production .-> RedisDB
    CachePort -. Local / Fallback .-> MemClient
```

---

## 📐 Mathematical Risk & Priority Formulation

The **ProjectPulse Early Warning System** evaluates projects using a multi-dimensional risk matrix:

### 1. Composite Risk Score ($P$-Score)
The composite risk score $S_{\text{composite}} \in [0, 100]$ is computed as a weighted combination of three distinct vectors:

$$\large S_{\text{composite}} = w_c \cdot S_{\text{cost}} + w_s \cdot S_{\text{schedule}} + w_t \cdot S_{\text{trajectory}}$$

Where:
- $S_{\text{cost}}$: Expenditure vs. physical completion ratio ($\text{Cost Burn Rate}$).
- $S_{\text{schedule}}$: Time elapsed vs. baseline completion schedule slippage.
- $S_{\text{trajectory}}$: Rate of deterioration over the previous 3 reporting periods ($\Delta \text{Velocity}$).
- $w_c = 0.40, \quad w_s = 0.40, \quad w_t = 0.20$

### 2. Risk Tiers
| Tier | Score Range | Operational Meaning |
| :--- | :---: | :--- |
| 🔴 **Critical** | $75 \le S \le 100$ | Severe cost overrun / indefinite stoppage. Immediate ministerial escalation required. |
| 🟠 **High** | $50 \le S < 75$ | Significant milestone delay or high cost burn without proportional physical progress. |
| 🟡 **Moderate** | $25 \le S < 50$ | Minor deviations within standard tolerance thresholds. |
| 🟢 **Stable** | $0 \le S < 25$ | On schedule, within budget allocations. |

### 3. Intervention Priority Index
Prioritizes executive interventions by factoring in both the **severity of deterioration** and the **total capital exposure**:

$$\large \text{Priority Index} = S_{\text{composite}} \times \ln(\text{Original Cost (in ₹ Cr)}) \times (1 + \max(0, \Delta_{\text{30-day Risk}}))$$

---

## 🗄 Database Schema & Data Models

```mermaid
erDiagram
    ministries ||--o{ projects : "oversees"
    sectors ||--o{ projects : "categorizes"
    states ||--o{ projects : "located in"
    
    projects ||--o{ project_snapshots : "has monthly"
    projects ||--o{ project_features : "yields"
    projects ||--o{ risk_scores : "scored by"
    projects ||--o{ alerts : "triggers"
    
    ingestion_runs ||--o{ project_snapshots : "tracks origin"

    projects {
        string project_id PK
        string project_name
        string sector
        string ministry
        string state
        string implementing_agency
        float original_cost
        date approval_date
        date original_completion_date
        date first_seen_report_month
        timestamp created_at
        timestamp updated_at
    }

    project_snapshots {
        bigint snapshot_id PK
        string project_id FK
        date report_month
        float revised_cost
        float cumulative_expenditure
        float physical_progress
        date latest_revised_completion_date
        string project_status
        text delay_reason_text
        string source_file
        string source_hash
        bigint ingestion_run_id FK
        timestamp ingested_at
    }

    risk_scores {
        bigint risk_id PK
        string project_id FK
        date report_month
        string model_version
        float cost_risk
        float schedule_risk
        float trajectory_risk
        float composite_score
        string tier
        float predicted_cost_overrun_pct
        float predicted_delay_months
        float intervention_priority
        float risk_delta
    }

    alerts {
        bigint alert_id PK
        string project_id FK
        string alert_type
        string severity
        string title
        text description
        string status
        timestamp generated_at
        timestamp acknowledged_at
        timestamp resolved_at
    }

    ingestion_runs {
        bigint run_id PK
        string source_file_name
        integer records_processed
        integer errors_count
        timestamp executed_at
    }
```

---

## 🔄 Data Ingestion & Extraction Pipeline

The ingestion service ([`services/ingestion`](file:///c:/Users/Sk%20Nooruddin/PROJECTPULSE_AI/backend/services/ingestion)) transforms messy governmental reports into structured database records:

```
[Raw PDF / Excel Monthly Progress Reports]
                 │
                 ▼
 ┌───────────────────────────────┐
 │       Format Detection        │
 ├───────────────────────────────┤
 │ • PDF with tables   ──► camelot-py
 │ • PDF text/stream   ──► pdfplumber
 │ • Excel spreadsheets──► openpyxl
 └───────────────┬───────────────┘
                 │
                 ▼
 ┌───────────────────────────────┐
 │   Data Normalization Stage    │
 ├───────────────────────────────┤
 │ • Standardize Ministry Names  │
 │ • Reconcile Sector Taxonomy   │
 │ • Clean Dates & Sanitize ₹ Cr │
 └───────────────┬───────────────┘
                 │
                 ▼
 ┌───────────────────────────────┐
 │  Idempotent DB Loader (Async) │
 ├───────────────────────────────┤
 │ • Upsert Project Master Table │
 │ • Append Snapshot (Hypertable)│
 │ • Log Ingestion Run Audit     │
 └───────────────┬───────────────┘
                 │
                 ▼
 [Trigger Alert & Risk Calculation Engine]
```

---

## 🤖 AI Assistant & Guardrail System

The `/api/v1/assistant/query` endpoint exposes a grounded conversational interface powered by **Groq** high-speed inference.

```mermaid
sequenceDiagram
    autonumber
    actor User as Decision Maker / Analyst
    participant API as /api/v1/assistant/query
    participant Svc as AssistantService
    participant LLM as Groq LLM (Llama 3)
    participant DB as PostgreSQL Database

    User->>API: POST {"query": "Which metro projects in Maharashtra are facing high delay?"}
    API->>Svc: process_query(prompt)
    Svc->>LLM: Formulate Structured Query & Filter Intent
    LLM-->>Svc: Extracted Parameters (state='Maharashtra', sector='Metro', risk='Critical/High')
    Svc->>DB: Execute Guarded & Parameterized SQL
    DB-->>Svc: Result Rows (Project IDs, Delay Months, Cost Delta)
    Svc->>LLM: Synthesize Grounded Natural Language Narrative
    LLM-->>Svc: Formatted Response with Citations & Insights
    Svc-->>API: Response JSON
    API-->>User: 200 OK (Clean summary with data tables & metrics)
```

---

## 📁 Monorepo Directory Structure

```text
PROJECTPULSE_AI/
├── backend/                            # 🚀 Backend Microservice Core
│   ├── .env.example                    # Environment template with sensible defaults
│   ├── Makefile                        # CLI helper for run, test, lint, and clean
│   ├── pytest.ini                      # Pytest discovery and pythonpath configuration
│   ├── requirements.txt                # Production and development dependencies
│   ├── README.md                       # Backend specific quick-start reference
│   ├── data/
│   │   ├── raw/                        # Ingested PDF and XLSX reports (.gitkeep)
│   │   └── staging/                    # Normalized staging payloads (.gitkeep)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                 # FastAPI application lifespan, CORS & middlewares
│   │   │   ├── dependencies.py         # FastAPI dependency injection factory
│   │   │   ├── core/
│   │   │   │   ├── cache.py            # CachePort interface, Redis & InMemory with TTL
│   │   │   │   ├── errors.py           # Custom exception hierarchy & global error handlers
│   │   │   │   ├── logging.py          # Structured JSON & contextual logging
│   │   │   │   └── resilience.py       # Tenacity retry wrappers & error boundaries
│   │   │   ├── db/
│   │   │   │   ├── __init__.py
│   │   │   │   └── session.py          # Async SQLAlchemy engine, session maker & health probe
│   │   │   ├── middleware/
│   │   │   │   └── request_id.py       # Distributed X-Request-ID propagation middleware
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   └── db.py               # SQLAlchemy 2.0 ORM Declarative Models
│   │   │   ├── repositories/
│   │   │   │   ├── alert_repo.py       # Alert CRUD & aggregation queries
│   │   │   │   └── project_repo.py     # Project listing, keyset cursor pagination & search
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── alerts.py           # Alert querying & manual engine triggers
│   │   │   │   ├── assistant.py        # Conversational AI assistant endpoint
│   │   │   │   ├── dashboard.py        # Executive summary, monthly delta & priorities
│   │   │   │   └── projects.py         # Filtered project catalog & detail views
│   │   │   └── services/
│   │   │       ├── alert_service.py    # Anomaly detection & threshold alert engine
│   │   │       ├── assistant_service.py# Groq LLM integration & prompt grounding
│   │   │       └── project_service.py  # Project orchestration business layer
│   │   └── ingestion/
│   │       ├── __init__.py
│   │       └── loaders/
│   │           ├── __init__.py
│   │           └── db_loader.py        # PDF/Excel parsers & database batch loading
│   └── tests/
│       ├── __init__.py
│       └── test_api.py                 # Pytest async HTTP integration test suite
├── .gitignore                          # Global gitignore configuration
├── pyrightconfig.json                  # VS Code Pyright & Python LSP configuration
└── README.md                           # Master project documentation
```

---

## 🛠 Tech Stack & Architecture Decisions

| Component | Choice | Rationale |
| :--- | :--- | :--- |
| **API Framework** | **FastAPI** `0.109.0` | Built-in async I/O, automatic OpenAPI 3.0 schema generation, and high throughput. |
| **Data Validation** | **Pydantic v2** `2.5.0` | Rust-backed core validation for sub-millisecond serialization of complex payloads. |
| **Async Database ORM** | **SQLAlchemy 2.0** + `asyncpg` | Native async concurrency, connection pooling, and rich relational mapping. |
| **Time-Series Storage** | **TimescaleDB** (Postgres extension) | Hypertable partitioning for lightning-fast monthly snapshots and trend aggregations. |
| **Caching Engine** | **Redis** (`redis.asyncio`) + `InMemoryCache` | Low-latency response caching with automatic local fallback when Redis is absent. |
| **LLM Inference** | **Groq Cloud API** | LPU inference providing 300+ tokens/second for real-time conversational intelligence. |
| **Document Parsers** | `pdfplumber`, `camelot-py`, `openpyxl` | Accurate extraction of structured financial and physical progress tables from PDF and Excel files. |

---

## ⚙️ Environment Variables Configuration

Create a `.env` file in `backend/`:

```bash
cp backend/.env.example backend/.env
```

| Parameter | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| `DATABASE_URL` | **Yes** | `postgresql+asyncpg://postgres:postgres@localhost:5432/projectpulse` | Async connection string for PostgreSQL / TimescaleDB. |
| `DB_POOL_SIZE` | No | `20` | Size of the persistent database connection pool. |
| `DB_MAX_OVERFLOW` | No | `10` | Maximum temporary connections allowed beyond pool size. |
| `DB_POOL_TIMEOUT` | No | `30.0` | Seconds to wait before timing out on pool checkout. |
| `DB_POOL_RECYCLE` | No | `1800` | Seconds after which connections are recycled (prevents stale drops). |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis instance URL (system seamlessly falls back to in-memory cache if omitted). |
| `GROQ_API_KEY` | **Yes** (for AI) | `your_groq_api_key` | API Key from [console.groq.com](https://console.groq.com) for AI Assistant functionality. |
| `ENVIRONMENT` | No | `development` | Environment label (`development`, `staging`, `production`). |
| `LOG_LEVEL` | No | `INFO` | Application log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

## 🚀 Local Installation & Setup

### Prerequisites
- **Python 3.11+** installed
- **PostgreSQL 14+** (TimescaleDB extension recommended)
- **Redis 6+** *(Optional)*

### 1. Clone the Repository
```bash
git clone https://github.com/Sumaiyalaskar25/ProjectPulse-Ai.git
cd ProjectPulse-Ai
```

### 2. Set Up Virtual Environment
#### On Windows (PowerShell):
```powershell
python -m venv venv_backend
.\venv_backend\Scripts\Activate.ps1
```

#### On Linux / macOS:
```bash
python3 -m venv venv_backend
source venv_backend/bin/activate
```

### 3. Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

---

## ⚡ Running the Services

### Option 1: Using the Makefile
```bash
cd backend
make run
```

### Option 2: Using Uvicorn Directly
```bash
cd backend
uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Production Multi-Worker Mode
```bash
cd backend
uvicorn services.api.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 🌐 Accessible Interfaces:
- **Interactive Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Technical Reference**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health & DB Readiness Probe**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📡 API Reference & Sample Payloads

### 1. Executive Summary: `GET /api/v1/dashboard/summary`
*Cached with 60s TTL.*

```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/summary"
```

```json
{
  "total_projects": 1842,
  "total_cost_cr": 2684120.50,
  "critical_count": 87,
  "high_count": 214,
  "moderate_count": 540,
  "stable_count": 1001,
  "capital_at_risk_cr": 845230.00
}
```

---

### 2. Urgent Intervention Priorities: `GET /api/v1/dashboard/priorities`
*Retrieves projects demanding immediate executive intervention.*

```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/priorities?limit=2"
```

```json
{
  "priorities": [
    {
      "project_id": "NHAI-DEL-MUM-EXP-PKG4",
      "project_name": "Delhi-Mumbai Expressway Package 4",
      "sector": "Roads and Highways",
      "ministry": "Ministry of Road Transport and Highways",
      "risk": 89.4,
      "tier": "Critical",
      "priority": 98.2,
      "delta": 12.5,
      "exposure": 12450.00
    },
    {
      "project_id": "MRTS-BANGALORE-PH2",
      "project_name": "Bangalore Metro Phase 2 Underground Section",
      "sector": "Urban Development / Metro",
      "ministry": "Ministry of Housing and Urban Affairs",
      "risk": 82.1,
      "tier": "Critical",
      "priority": 94.0,
      "delta": 8.0,
      "exposure": 15890.00
    }
  ]
}
```

---

### 3. Filtered Project Catalog: `GET /api/v1/projects`

| Parameter | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `page` | `int` | `1` | Page number (1-indexed). |
| `limit` | `int` | `50` | Page limit (max 100). |
| `ministry` | `str` | `null` | Filter by exact or partial ministry name. |
| `sector` | `str` | `null` | Filter by sector (e.g. `Roads and Highways`, `Railways`, `Power`). |
| `state` | `str` | `null` | Filter by Indian State / UT name. |
| `tier` | `str` | `null` | Filter by risk tier (`Critical`, `High`, `Moderate`, `Stable`). |
| `search` | `str` | `null` | Search query across project name or unique project ID. |

---

### 4. Trigger Alert Detection: `POST /api/v1/alerts/run-engine`

```bash
curl -X POST "http://localhost:8000/api/v1/alerts/run-engine"
```

```json
{
  "status": "success",
  "new_alerts_count": 3,
  "alert_ids": [1024, 1025, 1026]
}
```

---

### 5. AI Assistant Query: `POST /api/v1/assistant/query`

```bash
curl -X POST "http://localhost:8000/api/v1/assistant/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Give me a summary of Railway projects facing cost overrun greater than 20% in Eastern states"}'
```

---

## 🛡 Resilience, Observability & Caching

### 1. Request Tracing & Correlation IDs
Every incoming HTTP request is automatically injected with an `X-Request-ID` UUID header via [RequestIdMiddleware](file:///c:/Users/Sk%20Nooruddin/PROJECTPULSE_AI/backend/services/api/middleware/request_id.py). This correlation ID is propagated through all log statements and returned in API responses along with execution timings (`X-Process-Time-Ms`).

### 2. Graceful Lifecycle & Pool Management
FastAPI lifespan handlers ensure that database connection pools are cleanly established on startup and gracefully drained on SIGTERM/SIGINT:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ProjectPulse AI API starting up...")
    get_cache()
    yield
    logger.info("Disposing database pool...")
    await engine.dispose()
```

### 3. Dual-Mode Caching Layer
The caching layer follows the Port-and-Adapter pattern (`CachePort`):
- **Production**: Uses `redis.asyncio` with configurable connection timeouts and connection pooling.
- **Development / Standalone**: If Redis is not running or unreachable, it transparently falls back to `InMemoryCache` with automatic TTL expiration, preventing service failures during offline development.

---

## 🧪 Testing & Quality Assurance

The test suite validates endpoint status codes, correlation ID propagation, and security response headers:

```bash
cd backend
python -m pytest -v
```

### Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Sk Nooruddin\PROJECTPULSE_AI\backend
configfile: pytest.ini
plugins: anyio-4.15.0, asyncio-1.4.0
collected 3 items

tests\test_api.py::test_health_check_endpoint PASSED                     [ 33%]
tests\test_api.py::test_security_headers_present PASSED                  [ 66%]
tests\test_api.py::test_custom_request_id_propagation PASSED            [100%]

============================== 3 passed in 9.76s ==============================
```

---

## 🤝 Contribution & Git Workflow

We follow standard Trunk-Based and Feature-Branch workflows:

1. **Create a Topic Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Implement & Test**:
   ```bash
   cd backend
   python -m pytest
   ```
3. **Commit with Conventional Commits**:
   ```bash
   git commit -m "feat(api): add export endpoint for filtered project spreadsheets"
   ```
4. **Push & Open a PR**:
   ```bash
   git push -u origin feature/your-feature-name
   ```

---

<div align="center">
  <sub>ProjectPulse AI • Engineering Resilient National Infrastructure Intelligence</sub>
</div>