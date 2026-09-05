<div align="center">

# 🚀 ProjectPulse AI

**Intelligent Government Infrastructure Monitoring & Early Warning System**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-TimescaleDB-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-AsyncIO-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io)
[![Groq](https://img.shields.io/badge/Groq-AI%20Inference-F05032?style=flat)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## 📖 Table of Contents

- [Executive Overview](#-executive-overview)
- [Repository Structure](#-repository-structure)
- [Backend System Architecture](#-backend-system-architecture)
- [Core Features](#-core-features)
- [Tech Stack & Dependencies](#-tech-stack--dependencies)
- [Backend Environment Configuration](#-backend-environment-configuration)
- [Local Setup & Installation](#-local-setup--installation)
- [Running the Backend Services](#-running-the-backend-services)
- [API Documentation & Endpoints](#-api-documentation--endpoints)
  - [System & Health](#system--health)
  - [Dashboard & Executive Metrics](#dashboard--executive-metrics)
  - [Infrastructure Projects](#infrastructure-projects)
  - [Alert Engine](#alert-engine)
  - [AI Natural Language Assistant](#ai-natural-language-assistant)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Contribution & Git Workflow](#-contribution--git-workflow)

---

## 🏛 Executive Overview

**ProjectPulse AI** is an enterprise-grade platform engineered to monitor, evaluate, and provide predictive risk intelligence for large-scale national infrastructure initiatives.

The platform continuously aggregates periodic project reports, evaluates cost and schedule deviations, computes multi-dimensional composite risk scores, triggers automated early-warning alerts, and provides a grounded natural-language AI assistant for decision-makers.

---

## 📁 Repository Structure

The repository is organized into distinct domain folders to maintain separation of concerns:

```
PROJECTPULSE_AI/
├── backend/                      # Complete Backend Service Suite
│   ├── .env.example              # Environment configuration template
│   ├── Makefile                  # Developer task commands
│   ├── pytest.ini                # Pytest configuration & path resolution
│   ├── requirements.txt          # Python dependencies
│   ├── data/
│   │   ├── raw/                  # Incoming raw reports (.pdf, .xlsx)
│   │   └── staging/              # Extracted and normalized data files
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── main.py           # FastAPI application lifespan & middleware
│   │   │   ├── dependencies.py   # Dependency injection providers
│   │   │   ├── core/             # Caching, logging, resilience & errors
│   │   │   ├── db/               # Async SQLAlchemy engine & session factory
│   │   │   ├── middleware/       # Correlation ID & security headers
│   │   │   ├── models/           # Declarative database models
│   │   │   ├── repositories/     # Data access layer (Projects, Alerts)
│   │   │   ├── routes/           # REST API endpoints
│   │   │   └── services/         # Business logic & AI assistant services
│   │   └── ingestion/
│   │       └── loaders/          # Document & database ingestion pipelines
│   └── tests/
│       └── test_api.py           # Integration & endpoint test suite
├── .gitignore                    # Global ignore definitions
├── pyrightconfig.json            # Editor LSP & type checker configuration
└── README.md                     # Root project documentation
```

---

## 🏗 Backend System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client / Frontend                        │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON
┌──────────────────────────────▼──────────────────────────────┐
│                   FastAPI Application                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Middlewares: RequestId, Security Headers, GZip, CORS  │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │                    API Routers                        │  │
│  │  • /dashboard  • /projects  • /alerts  • /assistant   │  │
│  └───────────────────────────┬───────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                      Service Layer                          │
│   • ProjectService       • AlertEngine      • AssistantAI   │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
┌──────────────▼──────────────┐ ┌──────────────▼──────────────┐
│      Repository Layer       │ │         Cache Port          │
│   • ProjectRepo • AlertRepo │ │  • RedisCache (AsyncIO)     │
└──────────────┬──────────────┘ │  • InMemoryCache (Fallback) │
               │                └─────────────────────────────┘
┌──────────────▼──────────────┐
│  SQLAlchemy 2.0 (Async)     │
│  PostgreSQL / TimescaleDB   │
└─────────────────────────────┘
```

---

## ✨ Core Features

1. **Executive Dashboard Analytics**:
   - High-performance portfolio aggregations (capital at risk, project counts by risk tiers).
   - Month-over-month trajectory analysis (deteriorating vs. improving projects).
   - Weighted intervention priorities ranking based on risk velocity and exposure.
2. **Comprehensive Projects Catalog**:
   - Multi-field filtering (Ministry, Sector, State, Risk Tier, Keyword Search).
   - Keyset/cursor-based and page-offset pagination for sub-millisecond response times.
3. **Automated Risk & Early-Warning Alert Engine**:
   - Rule-based detection for critical schedule slippages, budget overruns, and anomaly spikes.
   - Alert lifecycle tracking (`open`, `acknowledged`, `resolved`).
4. **AI-Powered Natural Language Query Assistant**:
   - LLM integration via **Groq** for high-throughput, low-latency conversational queries.
   - Grounded context retrieval with guarded data access.
5. **Resilient Caching Layer**:
   - Dual-mode cache port: connects to distributed asynchronous Redis (`redis.asyncio`) in production with automatic fallback to thread-safe `InMemoryCache` with TTL support in local development.
6. **Robust Ingestion Pipeline**:
   - Multi-format ingestion support for PDFs and Excel sheets (`pdfplumber`, `camelot-py`, `openpyxl`).

---

## 🛠 Tech Stack & Dependencies

| Category | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Web Framework** | [FastAPI](https://fastapi.tiangolo.com) (0.109.0) | High-performance asynchronous REST API |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org) (0.27.0) | Lightning-fast ASGI web server |
| **Validation & Settings** | [Pydantic v2](https://docs.pydantic.dev) (2.5.0) | Data schemas, serialization, and settings management |
| **ORM & Database** | [SQLAlchemy](https://www.sqlalchemy.org) 2.0 (Async) | Async SQL toolkit and ORM mapper |
| **Database Driver** | [asyncpg](https://github.com/MagicStack/asyncpg) | High-speed PostgreSQL async client library |
| **Caching** | [Redis](https://redis.io) (`redis.asyncio`) | In-memory distributed caching with local fallback |
| **AI Inference** | [Groq SDK](https://groq.com) | Ultra-fast LLM inference for the query assistant |
| **Document Ingestion** | `pdfplumber`, `camelot-py`, `openpyxl` | Structured data extraction from government project reports |
| **Testing** | `pytest`, `pytest-asyncio`, `httpx` | Asynchronous integration and unit test suite |

---

## ⚙️ Backend Environment Configuration

Inside `backend/`, copy the `.env.example` template:

```bash
cp backend/.env.example backend/.env
```

### Environment Variables Reference

| Variable | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| `DATABASE_URL` | **Yes** | `postgresql+asyncpg://postgres:postgres@localhost:5432/projectpulse` | PostgreSQL / TimescaleDB async connection string |
| `DB_POOL_SIZE` | No | `20` | Database connection pool size |
| `DB_MAX_OVERFLOW` | No | `10` | Max overflow connections beyond pool size |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection URL (falls back to in-memory if unreachable) |
| `GROQ_API_KEY` | **Yes** (for AI) | — | API key for Groq LLM inference service |
| `ENVIRONMENT` | No | `development` | Deployment environment (`development`, `staging`, `production`) |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## 🚀 Local Setup & Installation

### Prerequisites

- **Python 3.11+** installed
- **PostgreSQL 14+** (Optional: TimescaleDB extension enabled)
- **Redis** (Optional: fallback activates automatically if Redis is omitted)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sumaiyalaskar25/ProjectPulse-Ai.git
cd ProjectPulse-Ai
```

### Step 2: Create and Activate Virtual Environment

On Windows (PowerShell):
```powershell
python -m venv venv_backend
.\venv_backend\Scripts\Activate.ps1
```

On Linux / macOS:
```bash
python3 -m venv venv_backend
source venv_backend/bin/activate
```

### Step 3: Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## ⚡ Running the Backend Services

### Step 1: Navigate to the `backend/` directory

```bash
cd backend
```

### Step 2: Start the Server

Using the Makefile:
```bash
make run
```

Or using Uvicorn directly:
```bash
uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000
```

Once running:
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Alternative UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📡 API Documentation & Endpoints

### System & Health

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root greeting and links to documentation. |
| `GET` | `/health` | Live system health check probing database readiness. |

---

### Dashboard & Executive Metrics

| Method | Endpoint | Description | Cache TTL |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/dashboard/summary` | Portfolio-wide overview (total cost, risk tier counts, capital at risk). | 60s |
| `GET` | `/api/v1/dashboard/changes` | Month-over-month trajectory (new critical/high projects, deterioration metrics). | 60s |
| `GET` | `/api/v1/dashboard/priorities` | Top urgent intervention projects ranked by risk velocity & exposure. | Real-time |

#### Example Response: `/api/v1/dashboard/summary`
```json
{
  "total_projects": 1842,
  "total_cost_cr": 2684120.5,
  "critical_count": 87,
  "high_count": 214,
  "moderate_count": 540,
  "stable_count": 1001,
  "capital_at_risk_cr": 845230.0
}
```

---

### Infrastructure Projects

| Method | Endpoint | Query Parameters | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/projects` | `page`, `limit`, `cursor`, `ministry`, `sector`, `state`, `tier`, `search` | Paginated project list with latest snapshot and risk score. |
| `GET` | `/api/v1/projects/{project_id}` | — | Detailed breakdown for a specific project. |

---

### Alert Engine

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/alerts` | Retrieve active & historical alerts with `status` and `severity` filters. |
| `POST` | `/api/v1/alerts/run-engine` | Trigger the anomaly and risk detection engine across all projects. |

---

### AI Natural Language Assistant

| Method | Endpoint | Request Body | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/assistant/query` | `{"query": "Which highway projects in Maharashtra are facing the highest delay?"}` | Conversational query grounded in project database knowledge. |

---

## 🧪 Testing & Quality Assurance

Run the automated test suite with `pytest`:

```bash
cd backend
python -m pytest
```

---

## 🤝 Contribution & Git Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Commit your changes:
   ```bash
   git commit -m "feat(backend): descriptive summary of changes"
   ```
3. Push to your branch:
   ```bash
   git push -u origin feature/your-feature-name
   ```
4. Open a **Pull Request** targeting the `main` branch.

---

<div align="center">
  <sub>Built with ❤️ for resilient infrastructure governance • ProjectPulse AI</sub>
</div>