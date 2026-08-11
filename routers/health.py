from fastapi import APIRouter

from config import __version__
from schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness probe. Deliberately does not touch the database."""
    return HealthResponse(status="ok", version=__version__)
