from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.recipe_schema import Recipe


class RecipeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="The name of the recipe to generate")
    description: str = Field(..., min_length=1, max_length=1000, description="A brief description of the recipe to generate")


class SavedRecipe(Recipe):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
