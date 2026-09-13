# services/api/services/project_service.py
from typing import Optional, Any, List
from ..repositories.project_repo import ProjectRepository
from ..core.cache import CachePort, get_cache
from ..core.logging import get_logger

logger = get_logger("project_service")

class ProjectService:
    """Application use case service for Projects."""
    def __init__(self, repo: ProjectRepository, cache: Optional[CachePort] = None):
        self.repo = repo
        self.cache = cache or get_cache()

    async def list_projects(
        self,
        filters: dict[str, Any],
        page: int = 1,
        limit: int = 50,
        cursor: Optional[str] = None
    ) -> dict[str, Any]:
        """Fetch filtered and paginated project list."""
        return await self.repo.list_with_filters(filters=filters, page=page, limit=limit, cursor=cursor)

    async def get_project(self, project_id: str) -> Optional[dict]:
        """Retrieve single project by ID with cache lookup."""
        cache_key = f"project:{project_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
            
        project = await self.repo.get_by_id(project_id)
        if project:
            await self.cache.setex(cache_key, 300, project)
        return project

    async def get_risk_history(self, project_id: str, limit: int = 12) -> List[dict]:
        """Retrieve historical risk scores for a project."""
        cache_key = f"project:{project_id}:history:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        history = await self.repo.get_risk_history(project_id=project_id, limit=limit)
        if history:
            await self.cache.setex(cache_key, 120, history)
        return history

    async def get_risk_drivers(self, project_id: str) -> Optional[dict]:
        """Retrieve latest risk drivers for a project."""
        cache_key = f"project:{project_id}:drivers"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        drivers = await self.repo.get_risk_drivers(project_id=project_id)
        if drivers:
            await self.cache.setex(cache_key, 120, drivers)
        return drivers
