from fastapi import APIRouter, HTTPException, status
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAIError,
    PermissionDeniedError,
    RateLimitError,
)
from pydantic import ValidationError
from sqlalchemy import select

import recipes
from db import SessionDep
from models.recipe import RecipeRow
from schemas.recipe_api import RecipeRequest, SavedRecipe

router = APIRouter(prefix="/recipes", tags=["recipes"])

# Ordered: first isinstance match wins, so subclasses must precede their base.
ERROR_STATUS: list[tuple[type[Exception], int, str]] = [
    (AuthenticationError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Recipe service is misconfigured"),
    (PermissionDeniedError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Recipe service is misconfigured"),
    (RateLimitError, status.HTTP_429_TOO_MANY_REQUESTS, "Recipe service is rate limited, retry shortly"),
    (BadRequestError, status.HTTP_400_BAD_REQUEST, "Recipe request was rejected upstream"),
    (APITimeoutError, status.HTTP_504_GATEWAY_TIMEOUT, "Recipe generation timed out"),
    (APIConnectionError, status.HTTP_503_SERVICE_UNAVAILABLE, "Cannot reach the recipe service"),
    (OpenAIError, status.HTTP_502_BAD_GATEWAY, "Recipe service failed"),
    (ValidationError, status.HTTP_502_BAD_GATEWAY, "Recipe service returned an invalid recipe"),
    (ValueError, status.HTTP_502_BAD_GATEWAY, "Recipe service returned an unusable recipe"),
]


def _as_http_error(exc: Exception) -> HTTPException:
    """Translate a generation failure into the HTTP status above. Re-raises anything unmapped."""
    for exc_type, code, detail in ERROR_STATUS:
        if isinstance(exc, exc_type):
            headers = None
            if code == status.HTTP_429_TOO_MANY_REQUESTS:
                retry_after = getattr(exc, "response", None) and exc.response.headers.get("retry-after")
                headers = {"Retry-After": retry_after} if retry_after else None
            return HTTPException(status_code=code, detail=detail, headers=headers)
    raise exc


@router.post("", response_model=SavedRecipe, status_code=status.HTTP_201_CREATED)
async def create_recipe(payload: RecipeRequest, session: SessionDep) -> RecipeRow:
    """Generate a recipe from a name and description, save it, and return it with its id."""
    try:
        recipe = await recipes.generate_recipe(payload.name, payload.description)
    except Exception as exc:
        raise _as_http_error(exc) from exc

    row = RecipeRow(
        name=recipe.name,
        description=recipe.description,
        ingredients=[i.model_dump() for i in recipe.ingredients],
        steps=[s.model_dump() for s in recipe.steps],
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


@router.get("", response_model=list[SavedRecipe])
async def list_recipes(session: SessionDep) -> list[RecipeRow]:
    """List every saved recipe, newest first."""
    result = await session.execute(select(RecipeRow).order_by(RecipeRow.id.desc()))
    return list(result.scalars())


@router.get("/{recipe_id}", response_model=SavedRecipe)
async def get_recipe(recipe_id: int, session: SessionDep) -> RecipeRow:
    """Fetch one saved recipe by id."""
    row = await session.get(RecipeRow, recipe_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recipe {recipe_id} not found")
    return row
