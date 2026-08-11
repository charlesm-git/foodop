from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import __version__
from db import engine
from models.base import Base
from models.recipe import RecipeRow  # noqa: F401 - registers the table on Base.metadata
from routers import health, recipe


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create tables on startup. No Alembic, so this is the schema authority."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="foodop API", version=__version__, lifespan=lifespan)
app.include_router(health.router)
app.include_router(recipe.router)
