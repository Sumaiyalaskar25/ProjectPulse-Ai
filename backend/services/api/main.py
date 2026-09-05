# services/api/main.py
from contextlib import asynccontextmanager
from typing import Any, cast
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.responses import JSONResponse

from .routes import dashboard, projects, alerts, assistant
from .middleware.request_id import RequestIdMiddleware, get_current_request_id
from .core.errors import AppException, app_exception_handler, unhandled_exception_handler
from .core.logging import get_logger
from .core.cache import get_cache
from .db.session import engine, check_db_health

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and graceful shutdown."""
    logger.info("ProjectPulse AI API starting up...")
    # Initialize cache
    get_cache()
    yield
    logger.info("ProjectPulse AI API shutting down, disposing database pool...")
    await engine.dispose()
    logger.info("Shutdown complete.")

app = FastAPI(
    title="ProjectPulse AI Backend API",
    description="Government Infrastructure Monitoring & Early Warning System API",
    version="1.0.0",
    lifespan=lifespan
)

# 1. Register Global Exception Handlers
app.add_exception_handler(AppException, cast(Any, app_exception_handler))
app.add_exception_handler(Exception, unhandled_exception_handler)

# 2. Security Headers & Observability Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# 3. Request Tracing Middleware
app.add_middleware(RequestIdMiddleware)

# 4. Response Compression Middleware (for payloads > 1KB)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 5. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Register Application Routers
app.include_router(dashboard.router)
app.include_router(projects.router)
app.include_router(alerts.router)
app.include_router(assistant.router)

# 7. System Endpoints
@app.get("/health", tags=["system"])
async def health_check():
    """System health check with active database probe."""
    db_ok = await check_db_health()
    return {
        "status": "healthy" if db_ok else "degraded",
        "service": "projectpulse-api",
        "database_connected": db_ok,
        "request_id": get_current_request_id() or None
    }

@app.get("/", tags=["system"])
async def root():
    return {
        "message": "Welcome to ProjectPulse AI API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
