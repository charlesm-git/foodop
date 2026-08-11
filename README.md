## AI Recipes Interview Task

Generate a recipe based on a provided name and description using OpenAI's API.

### Constraints
- Use only the `gpt-5-mini` model for this task.
- The assigned OpenAI API key has a hard cap of $10 in credits.
- You are not allowed to change the structure of the Pydantic models (except the type for `quantity`; see tasks below).

### Task 1: Set up AI functionality
Create a recipe that includes:
1. A comprehensive list of ingredients.
2. Reasonable quantities for each ingredient.
3. A step-by-step production process.

Note: We are looking for implementation, not the perfect prompt.

### Task 2: Set up an API endpoint
Turn the solution into an API endpoint that takes a recipe name and description as input and returns a completed recipe.

### Task 3: Handle exceptions and HTTP status codes
Handle realistic errors and decide how to handle different HTTP status codes returned by OpenAI's API.

### Task 4: Save recipes
Save completed recipes to persistent storage (a local file system, a small local DB, etc.). Create a method to retrieve saved recipes (endpoint, script, etc.).

### Task 5 (Bonus): Unify quantities
Ensure ingredient quantities always use the same unit. You may change the type of `quantity` in the `Ingredient` schema if needed.

### Task 6 (Bonus): Recipe with user-defined ingredients and production steps as input
Consider how you would change the code if the input was a `Recipe` object instead of just a name and a description. The `Recipe` may contain some user-inputted ingredients and production steps already.

### Evaluation rubric (0-10)
Each criterion is scored `0` (weak), `1` (acceptable), or `2` (strong).

| Criterion | Weak | Acceptable | Strong |
|---|---|---|---|
| Core correctness | Does not return a valid `Recipe` reliably | Returns valid `Recipe` on happy path | Consistently valid output with clear mapping to schema |
| API design and contract | Endpoint is unclear or inconsistent | Basic request/response works | Clean contract, validation, and sensible status codes |
| Robustness and error handling | Crashes or returns vague failures | Handles some failures | Handles OpenAI and validation failures clearly and gracefully |
| Persistence | Missing or broken save/retrieve flow | Basic save and fetch works | Reliable persistence design and retrieval approach |
| Engineering quality | Hard to follow and no tests | Reasonably clear code with minimal tests | Clear structure, separation of concerns, and meaningful tests |

### Repository guide
- `recipe_schema.py`: Defines the Pydantic schema contract for recipe output. Keep the structure as-is.
- `recipes.py`: Main implementation entry point. Complete using OpenAI and return a valid `Recipe`.
- Expected output: A valid `Recipe` object (or JSON from it) with realistic quantities and ordered production steps.

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="<your-api-key>"
```
