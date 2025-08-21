from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..utils.loader import basic_search

try:
    from rapidfuzz import fuzz
    HAVE_FUZZ = True
except Exception:
    HAVE_FUZZ = False

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def search(
    request: Request,
    q: str = Query("", description="search query"),
    cuisine: str = Query("", description="optional cuisine filter")
):
    # get coarse hits first
    pool = basic_search(q, cuisine if cuisine else None)

    # fuzzy rank (best effort if rapidfuzz installed)
    results = []
    if HAVE_FUZZ and q:
        scored = []
        for r in pool:
            text = " ".join([r["title"], r["cuisine"]] + r.get("ingredients", []))
            score = max(
                fuzz.partial_ratio(q, r["title"]),
                fuzz.token_set_ratio(q, text)
            )
            scored.append((score, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [ {"title": r["title"], "slug": r["slug"], "time": r["time_total"],
                     "tags": [r["cuisine"], f"{r['servings']} servings"]} for score, r in scored if score >= 55 ]
        # fallback if all filtered out by threshold
        if not results:
            results = [ {"title": r["title"], "slug": r["slug"], "time": r["time_total"],
                         "tags": [r["cuisine"], f"{r['servings']} servings"]} for r in pool ]
    else:
        results = [ {"title": r["title"], "slug": r["slug"], "time": r["time_total"],
                     "tags": [r["cuisine"], f"{r['servings']} servings"]} for r in pool ]

    return templates.TemplateResponse("search_results.html", {"request": request, "q": q, "results": results})
