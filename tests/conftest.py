# tests/conftest.py
# makes project root importable (so we can do: from main import app, import utils.loader, etc.)
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient

# ✅ no "app." prefix anywhere
from main import app
import utils.loader as loader_mod
import routes.recipes as recipes_routes


@pytest.fixture(scope="session")
def fake_data():
    # small, predictable dataset spanning regions
    return [
        {
            "slug": "butter-chicken",
            "title": "Butter Chicken",
            "cuisine": "North Indian",
            "time_total": 60,
            "servings": 4,
            "ingredients": ["chicken", "tomato", "butter", "cream"],
            "steps": ["s1", "s2", "s3"],
        },
        {
            "slug": "masala-dosa",
            "title": "Masala Dosa",
            "cuisine": "South Indian",
            "time_total": 90,
            "servings": 4,
            "ingredients": ["dosa batter", "potato", "mustard", "curry leaves"],
            "steps": ["s1", "s2", "s3"],
        },
        {
            "slug": "ragi-ball",
            "title": "Ragi Ball (Ragi Mudde)",
            "cuisine": "South Indian",
            "time_total": 20,
            "servings": 3,
            "ingredients": ["ragi flour", "water", "salt"],
            "steps": ["s1", "s2", "s3"],
        },
        {
            "slug": "pav-bhaji",
            "title": "Pav Bhaji",
            "cuisine": "West Indian",
            "time_total": 45,
            "servings": 4,
            "ingredients": ["pav", "potato", "tomato", "butter"],
            "steps": ["s1", "s2", "s3"],
        },
    ]


@pytest.fixture(autouse=True)
def monkeypatch_loader(monkeypatch, fake_data):
    """
    Patch loader + routes to use in-memory fake data (no disk, no CRUD).
    We patch BOTH the loader module and the names already imported into routes.
    """
    # build maps from fake data
    recipes_list = list(fake_data)
    recipes_dict = {r["slug"]: r for r in recipes_list}

    # ---- patch loader module (source of truth during tests) ----
    monkeypatch.setattr(loader_mod, "RECIPES_LIST", recipes_list, raising=False)
    monkeypatch.setattr(loader_mod, "RECIPES", recipes_dict, raising=False)

    def _get_all():
        return loader_mod.RECIPES_LIST

    def _by_cuisine(c):
        c = (c or "").lower()
        seen = {}
        for r in loader_mod.RECIPES_LIST:
            if r.get("cuisine", "").lower() == c:
                seen[r["slug"]] = r
        return list(seen.values())

    def _cuisines():
        return sorted({r.get("cuisine", "") for r in loader_mod.RECIPES_LIST})

    def _search(q, cuisine=None):
        ql = (q or "").lower().strip()
        pool = _by_cuisine(cuisine) if cuisine else loader_mod.RECIPES_LIST
        if not ql:
            return pool
        hits = []
        for r in pool:
            hay = " ".join([r["title"], r["cuisine"]] + r.get("ingredients", [])).lower()
            if ql in hay:
                hits.append(r)
        # de-dupe by slug
        return list({r["slug"]: r for r in hits}.values())

    def _reload():
        # pretend reload succeeded; return count
        return len(loader_mod.RECIPES_LIST)

    def _counts():
        from collections import Counter
        return dict(Counter([r["cuisine"] for r in loader_mod.RECIPES_LIST]))

    monkeypatch.setattr(loader_mod, "get_all_recipes", _get_all, raising=False)
    monkeypatch.setattr(loader_mod, "get_recipes_by_cuisine", _by_cuisine, raising=False)
    monkeypatch.setattr(loader_mod, "get_all_cuisines", _cuisines, raising=False)
    monkeypatch.setattr(loader_mod, "basic_search", _search, raising=False)
    monkeypatch.setattr(loader_mod, "reload_data", _reload, raising=False)
    monkeypatch.setattr(loader_mod, "cuisine_counts", _counts, raising=False)

    # ---- patch attributes already imported inside routes.recipes ----
    monkeypatch.setattr(recipes_routes, "RECIPES", recipes_dict, raising=False)
    monkeypatch.setattr(recipes_routes, "get_all_recipes", _get_all, raising=False)
    monkeypatch.setattr(recipes_routes, "get_recipes_by_cuisine", _by_cuisine, raising=False)
    monkeypatch.setattr(recipes_routes, "get_all_cuisines", _cuisines, raising=False)
    monkeypatch.setattr(recipes_routes, "reload_data", _reload, raising=False)
    monkeypatch.setattr(recipes_routes, "cuisine_counts", _counts, raising=False)


@pytest.fixture()
def client():
    return TestClient(app)
