# services/api/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .db.session import get_db
from .core.cache import CachePort, get_cache
from .repositories.project_repo import ProjectRepository, SQLAlchemyProjectRepository
from .repositories.alert_repo import AlertRepository, SQLAlchemyAlertRepository
from .services.project_service import ProjectService
from .services.alert_service import AlertEngine
from .services.assistant_service import AssistantService

def get_cache_service() -> CachePort:
    """Dependency provider for cache."""
    return get_cache()

def get_project_repository(db: AsyncSession = Depends(get_db)) -> ProjectRepository:
    """Dependency provider for Project repository."""
    return SQLAlchemyProjectRepository(db)

def get_alert_repository(db: AsyncSession = Depends(get_db)) -> AlertRepository:
    """Dependency provider for Alert repository."""
    return SQLAlchemyAlertRepository(db)

def get_project_service(
    repo: ProjectRepository = Depends(get_project_repository),
    cache: CachePort = Depends(get_cache_service)
) -> ProjectService:
    """Dependency provider for Project application service."""
    return ProjectService(repo=repo, cache=cache)

def get_alert_engine(db: AsyncSession = Depends(get_db)) -> AlertEngine:
    """Dependency provider for AlertEngine."""
    return AlertEngine(db=db)

def get_assistant_service(db: AsyncSession = Depends(get_db)) -> AssistantService:
    """Dependency provider for AssistantService."""
    return AssistantService(db=db)
