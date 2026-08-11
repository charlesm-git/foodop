"""Recipe generation via OpenAI. Framework-free so it stays runnable as a script."""

import asyncio

from openai import AsyncOpenAI

from config import get_settings
from schemas.recipe_schema import Recipe

client = AsyncOpenAI(api_key=get_settings().openai_api_key or None)

INSTRUCTIONS = """You are a recipe writer. Given a recipe name and description, produce a complete, realistic recipe.

- List every ingredient needed, including staples like salt, pepper, oil and water.
- Give a reasonable quantity for each, sized for 4 servings.
- Express quantities as a number, plus one of exactly three units: "g" for solids,
  "ml" for liquids, "piece" for countable items (eggs, garlic cloves, onions).
  Never use cups, tablespoons, pinches or "to taste" - convert them to g or ml.
- Write the production steps in order, starting at index 1, one clear action per step.
"""


async def generate_recipe(name: str, description: str) -> Recipe:
    """Generate a complete Recipe. Raises ValueError if the model returns nothing usable."""
    settings = get_settings()
    response = await client.responses.parse(
        model=settings.openai_model,
        instructions=INSTRUCTIONS,
        input=f"Recipe name: {name}\nDescription: {description}",
        text_format=Recipe,
    )

    recipe = response.output_parsed
    if recipe is None:
        raise ValueError(f"model returned no parsable recipe (status: {response.status})")
    if not recipe.ingredients or not recipe.steps:
        raise ValueError("model returned a recipe with no ingredients or no steps")

    # The caller's name/description are the contract; never let the model rewrite them.
    return recipe.model_copy(update={"name": name, "description": description})


if __name__ == "__main__":
    name = "Chicken Curry"  # This is an example recipe name; you can change it to test different recipes.
    description = "A classic indian dish with rice and chicken as base"  # This is an example description; you can change it to test different recipes.

    recipe = asyncio.run(generate_recipe(name, description))
    print(recipe.model_dump())  # model_dump() is a Pydantic method that converts the model instance to a Python dictionary.
