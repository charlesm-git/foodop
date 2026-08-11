# Design notes

## Task 6 — accepting a partial `Recipe` as input

Not implemented; this is the design answer. It is a small change, deliberately deferred.

### What changes

Only the input schema and the prompt. `POST /recipes` currently takes `RecipeRequest`
(`name` + `description`). It would instead take a partial recipe:

```python
class RecipeRequest(BaseModel):
    name: str
    description: str
    ingredients: list[Ingredient] = []   # user-supplied, must be preserved
    steps: list[ProductionStep] = []
```

That is `Recipe` with both lists left at their existing defaults, so the empty case stays
byte-identical to today's contract — existing callers keep working, no versioning needed.

### What the generator does with it

`generate_recipe(name, description)` becomes `generate_recipe(request)` and serialises any
supplied ingredients/steps into the prompt, with instructions to treat them as fixed:

- keep every given ingredient, with the user's quantity, unchanged
- add only what is missing to make the recipe complete
- keep the given steps in their relative order, renumbering `index` contiguously once the
  generated steps are interleaved

The response schema, persistence, and error mapping are all untouched.

### The part that actually needs thought

The model will not reliably respect "do not modify what I gave you" from the prompt alone.
Prompt instructions are a request, not a constraint, so the guarantee has to be enforced in
code after parsing — the same way `name`/`description` are already overwritten from the
request in [recipes.py](recipes.py) rather than trusted from the model:

- reconcile by ingredient name: for any name the user supplied, discard the model's version
  and splice the user's back in
- if the model dropped a user ingredient entirely, re-insert it
- renumber `steps[].index` from 1 in code, never trusting the model's numbering

Two open questions I would want answered before building it:

1. **Is a user ingredient a hard constraint or a hint?** "I have 300 g of chicken" (use
   exactly this) is a different feature from "chicken should be in it" (any quantity).
   I would start with hard constraint — it is the one you can actually verify.
2. **What if the partial input is contradictory** (steps referencing ingredients that are
   not listed, or an ingredient that makes no sense for the description)? Cheapest honest
   answer is to let the model resolve it and add the missing ingredients, rather than
   trying to validate coherence up front.

### Cost

One schema change, ~15 lines of reconciliation, one extra test asserting a user-supplied
ingredient survives generation with its quantity intact. The reconciliation is the only
part worth reviewing carefully.

## Other decisions

- **`quantity` is a nested `Quantity` model** (`value: float`, `unit: "g" | "ml" | "piece"`)
  rather than a single unit. One unit cannot honestly cover solids, liquids and countable
  items — "2 eggs" as `110.0 g` is worse data, not unified data. The enum is closed, so the
  model cannot invent "tbsp", which is what Task 5 is actually asking for.
- **Ingredients and steps are stored as JSON columns**, not child tables. There is one
  entity here and no query crosses it. Normalise when something needs to search by
  ingredient across recipes.
- **No Alembic.** One table, `create_all` on startup is the schema authority. Adding
  migrations means maintaining two sources of truth for a schema that changes once.
- **OpenAI errors are mapped to HTTP status in the router only**, so `recipes.py` stays
  framework-free and runnable as a script, as the README's repo guide describes it.
