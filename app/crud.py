from typing import List, Iterable, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models, schemas
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---- DB CRUD ----
def get_recipe_by_slug(db: Session, slug: str) -> models.Recipe | None:
    return db.execute(select(models.Recipe).where(models.Recipe.slug == slug)).scalar_one_or_none()

def get_recipes(db: Session, skip: int = 0, limit: int = 50) -> List[models.Recipe]:
    return list(db.execute(select(models.Recipe).offset(skip).limit(limit)).scalars())

def create_recipe(db: Session, data: schemas.RecipeCreate) -> models.Recipe:
    obj = models.Recipe(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_recipe(db: Session, slug: str, data: schemas.RecipeUpdate) -> models.Recipe | None:
    obj = get_recipe_by_slug(db, slug)
    if not obj:
        return None
    for k, v in data.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

def delete_recipe(db: Session, slug: str) -> bool:
    obj = get_recipe_by_slug(db, slug)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

# ---- Search helpers (no DB needed) ----
def _norm(s: str) -> str:
    return s.lower().strip()

def search_in_memory(recipes: Iterable[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    q = _norm(query)
    hits = []
    for r in recipes:
        hay = " ".join([
            r.get("title", ""),
            r.get("cuisine", ""),
            " ".join(r.get("ingredients", []))
        ]).lower()
        if q in hay:
            hits.append(r)
    return hits

# ---- Pantry helpers ----
def ingredients_missing(recipe: Dict[str, Any], pantry: Iterable[str]) -> List[str]:
    """Loose matching: if any pantry item is a substring of an ingredient, it's considered covered."""
    pset = {_norm(x) for x in pantry}
    missing = []
    for ing in recipe.get("ingredients", []):
        ing_norm = _norm(ing)
        if not any(p in ing_norm for p in pset):
            missing.append(ing)
    return missing
def dedupe_by_slug(items):
    seen, out = set(), []
    for r in items:
        s = r.get("slug")
        if s in seen:
            continue
        seen.add(s)
        out.append(r)
    return out
# --- Dedupe + region helpers -----------------------------------------------
from pathlib import Path
import json

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RECIPES_PATH = DATA_DIR / "seed_recipes.json"
CUISINES_PATH = DATA_DIR / "cuisines.json"

def load_recipes():
    return json.loads(RECIPES_PATH.read_text(encoding="utf-8"))

def load_cuisines():
    return json.loads(CUISINES_PATH.read_text(encoding="utf-8"))

def index_by_slug(recipes):
    return {r["slug"]: r for r in recipes}

def list_for_region(region_key: str, recipes=None, cuisines=None, idx=None):
    recipes = recipes or load_recipes()
    cuisines = cuisines or load_cuisines()
    idx = idx or index_by_slug(recipes)
    slugs = cuisines["dishes_by_region"].get(region_key, [])
    # drives strictly by cuisines.json; no dupes possible
    return [idx[s] for s in slugs if s in idx]
