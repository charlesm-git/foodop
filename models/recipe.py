from datetime import datetime

from sqlalchemy import JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class RecipeRow(Base):
    """A generated recipe, persisted whole.

    ponytail: ingredients/steps are stored as JSON blobs rather than child tables.
    Normalise only if you need to query across recipes by ingredient.
    """

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    ingredients: Mapped[list[dict]] = mapped_column(JSON)
    steps: Mapped[list[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
