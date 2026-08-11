from typing import Literal

from pydantic import BaseModel, Field


class Quantity(BaseModel):
    value: float = Field(..., description="The numeric amount of the ingredient")
    unit: Literal["g", "ml", "piece"] = Field(..., description="The unit of the amount: grams for solids, millilitres for liquids, pieces for countable items")

class Ingredient(BaseModel):
    name: str = Field(..., description="The name of the ingredient")
    quantity: Quantity = Field(..., description="The quantity of the ingredient required for the recipe")

class IngredientList(BaseModel):
    ingredients: list[Ingredient] = Field(default=[], description="A comprehensive list of ingredients with reasonable quantities")

class ProductionStep(BaseModel):
    index: int = Field(..., description="The step number in the recipe")
    instruction: str = Field(..., description="The instruction for this step")

class ProductionSteps(BaseModel):
    steps: list[ProductionStep] = Field(default=[], description="A step-by-step production process for the recipe")

class Recipe(IngredientList, ProductionSteps):
    name: str = Field(..., description="The name of the recipe")
    description: str = Field(..., description="A brief description of the recipe")
