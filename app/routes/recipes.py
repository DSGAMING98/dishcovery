from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# ✅ relative imports only
from ..utils.loader import (
    RECIPES,
    get_all_recipes,
    get_recipes_by_cuisine,
    get_all_cuisines,
    reload_data,
    cuisine_counts,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ---------- Helpers ----------

def _browse_context(request: Request, recipes: list[dict], heading: str) -> dict:
    """Common context for browse pages."""
    return {
        "request": request,
        "recipes": recipes,
        "cuisines": get_all_cuisines(),
        "heading": heading,
    }


# ---------- Routes ----------

@router.get("", response_class=HTMLResponse)
def list_all(request: Request):
    """Browse ALL recipes (grid)."""
    recipes = get_all_recipes()
    return templates.TemplateResponse("browse.html", _browse_context(request, recipes, "Browse All Recipes"))


@router.get("/cuisine/{cuisine}", response_class=HTMLResponse)
def list_by_cuisine(cuisine: str, request: Request):
    """
    Browse by cuisine/region (e.g. 'north indian', 'south indian').
    Loader does exact-match first, then partial fallback (so 'indian' still shows stuff).
    """
    recipes = get_recipes_by_cuisine(cuisine)
    heading = f"{cuisine.title()} Recipes"
    return templates.TemplateResponse("browse.html", _browse_context(request, recipes, heading))


@router.get("/__reload")
def dev_reload():
    """Hot-reload JSON from disk without restarting uvicorn (dev QoL)."""
    count = reload_data()
    return JSONResponse({"reloaded": count})


@router.get("/__stats")
def stats():
    """Quick counts per cuisine for sanity checks."""
    counts = cuisine_counts()
    return JSONResponse({"cuisines": counts, "total": sum(counts.values())})


@router.get("/{slug}", response_class=HTMLResponse)
def recipe_detail(slug: str, request: Request):
    """Single recipe page."""
    recipe = RECIPES.get(slug)
    if not recipe:
        return templates.TemplateResponse(
            "recipe_detail.html",
            {
                "request": request,
                "r": {
                    "title": "Not Found",
                    "cuisine": "-",
                    "time_total": 0,
                    "servings": 0,
                    "ingredients": [],
                    "steps": ["This recipe does not exist."],
                },
            },
            status_code=404,
        )
    return templates.TemplateResponse("recipe_detail.html", {"request": request, "r": recipe})


@router.get("/{slug}/cook", response_class=HTMLResponse)
def recipe_cook(slug: str, request: Request):
    """Fullscreen Cook Mode (stepper + timer)."""
    recipe = RECIPES.get(slug)
    if not recipe:
        return templates.TemplateResponse("cook_mode.html", {"request": request, "r": None}, status_code=404)
    return templates.TemplateResponse("cook_mode.html", {"request": request, "r": recipe})
