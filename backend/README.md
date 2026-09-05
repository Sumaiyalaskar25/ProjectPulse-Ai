<div align="center">

# 🚀 ProjectPulse AI — Backend Service Suite

**Intelligent Government Infrastructure Monitoring & Early Warning API System**

</div>

---

## 📁 Directory Layout

- **`services/api/`**: FastAPI application, REST endpoints, dependency injection, middleware, models, and repositories.
- **`services/ingestion/`**: Data ingestion loaders for PDF, Excel, and database pipelines.
- **`tests/`**: Integration and unit tests.
- **`data/`**: Staging and raw document storage.
- **`requirements.txt`**: Backend Python package dependencies.
- **`pytest.ini`**: Pytest path and async test configurations.
- **`Makefile`**: Developer automation commands.
- **`.env.example`**: Backend configuration template.

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run test suite
python -m pytest

# 3. Start development server
uvicorn services.api.main:app --reload --port 8000
```
