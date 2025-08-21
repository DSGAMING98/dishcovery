# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from .routes import recipes, search
try:
    from .routes import pantry
    HAS_PANTRY = True
except Exception:
    HAS_PANTRY = False

from .utils.loader import get_recipes_by_cuisine

app = FastAPI(
    title="Dishcovery",
    description="Step-by-step recipes with search & cook mode.",
    version="1.0.0",
    contact={"name": "Prajwal"},
    license_info={"name": "© 2025 Developed by Prajwal"},
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    north = get_recipes_by_cuisine("north indian")
    south = get_recipes_by_cuisine("south indian")
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "title": "Dishcovery",
            "north_recipes": north,
            "south_recipes": south,
        },
    )

app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(search.router,  prefix="/search",  tags=["search"])
if HAS_PANTRY:
    app.include_router(pantry.router, prefix="/pantry", tags=["pantry"])
