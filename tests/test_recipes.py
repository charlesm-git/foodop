import httpx
import pytest
from fastapi.testclient import TestClient
from openai import RateLimitError

import recipes
from main import app
from schemas.recipe_schema import Ingredient, ProductionStep, Quantity, Recipe

FAKE_RECIPE = Recipe(
    name="ignored by the endpoint",
    description="ignored by the endpoint",
    ingredients=[
        Ingredient(name="spaghetti", quantity=Quantity(value=400, unit="g")),
        Ingredient(name="egg", quantity=Quantity(value=4, unit="piece")),
    ],
    steps=[
        ProductionStep(index=1, instruction="Boil the pasta."),
        ProductionStep(index=2, instruction="Mix in the eggs off the heat."),
    ],
)


@pytest.fixture(scope="module")
def client():
    # The context manager is what runs lifespan, which is what creates the tables.
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def fake_generator(monkeypatch):
    """Replace the OpenAI call. No test ever spends credits."""

    async def _generate(name: str, description: str) -> Recipe:
        return FAKE_RECIPE.model_copy(update={"name": name, "description": description})

    monkeypatch.setattr(recipes, "generate_recipe", _generate)


def test_create_then_retrieve_recipe(client, fake_generator):
    created = client.post("/recipes", json={"name": "Carbonara", "description": "Classic pasta"})
    assert created.status_code == 201

    body = created.json()
    assert body["name"] == "Carbonara"
    assert body["description"] == "Classic pasta"
    assert body["ingredients"][0] == {"name": "spaghetti", "quantity": {"value": 400.0, "unit": "g"}}
    assert [s["index"] for s in body["steps"]] == [1, 2]

    # Round trips through SQLite, not just through memory.
    fetched = client.get(f"/recipes/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == body

    listed = client.get("/recipes")
    assert listed.status_code == 200
    assert body["id"] in [r["id"] for r in listed.json()]


def test_unknown_recipe_returns_404(client):
    assert client.get("/recipes/999999").status_code == 404


def test_empty_name_is_rejected_before_calling_openai(client):
    assert client.post("/recipes", json={"name": "", "description": "x"}).status_code == 422


def test_openai_rate_limit_maps_to_429(client, monkeypatch):
    async def _rate_limited(name: str, description: str) -> Recipe:
        raise RateLimitError(
            "slow down",
            response=httpx.Response(429, request=httpx.Request("POST", "https://api.openai.com")),
            body=None,
        )

    monkeypatch.setattr(recipes, "generate_recipe", _rate_limited)
    r = client.post("/recipes", json={"name": "Carbonara", "description": "Classic pasta"})
    assert r.status_code == 429
