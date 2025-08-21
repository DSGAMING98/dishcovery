import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter

DATA_FILE = Path("data/seed_recipes.json")

# 🔥 one source of truth: region per slug (works even if JSON isn't updated)
REGION_BY_SLUG: Dict[str, str] = {
    # North
    "butter-chicken":"North Indian","chole-bhature":"North Indian","rogan-josh":"North Indian",
    "rajma-chawal":"North Indian","nihari":"North Indian","aloo-paratha":"North Indian",
    "laal-maas":"North Indian","dal-baati-churma":"North Indian","chicken-biryani":"North Indian",
    # South
    "masala-dosa":"South Indian","idli-sambar":"South Indian","hyderabadi-biryani":"South Indian",
    "kerala-fish-curry":"South Indian","appam-stew":"South Indian","chettinad-chicken":"South Indian",
    "pongal":"South Indian","prawns-ghee-roast":"South Indian",
     "ragi-ball": "South Indian",

    # West
    "pav-bhaji":"West Indian","vada-pav":"West Indian","misal-pav":"West Indian",
    "dhokla":"West Indian","thepla":"West Indian","goan-fish-curry":"West Indian","poha":"West Indian",
    # East
    "macher-jhol":"East Indian","pakhala-bhata":"East Indian","litti-chokha":"East Indian",
    # Northeast
    "assamese-fish-curry":"Northeast Indian","bamboo-shoot-curry":"Northeast Indian","smoked-pork-bamboo-shoot":"Northeast Indian",
    # Central / Pan
    "bhutte-ka-kees":"Central Indian","indian-thali":"Pan-Indian",
}

RECIPES_LIST: List[dict] = []
RECIPES: Dict[str, dict] = {}

def _normalize_list(data) -> List[dict]:
    # allow {"recipes":[...]} or [...]
    if isinstance(data, dict) and "recipes" in data:
        data = data["recipes"]
    if not isinstance(data, list):
        raise ValueError("seed_recipes.json must be a JSON array or an object with a 'recipes' array")
    uniq: Dict[str, dict] = {}
    for r in data:
        if not isinstance(r, dict):
            continue
        slug = (r.get("slug") or "").strip()
        if not slug:
            continue
        # apply region override if present
        region = REGION_BY_SLUG.get(slug)
        if region:
            r["cuisine"] = region
        # store a normalized copy for matching
        r["slug"] = slug
        r["cuisine_norm"] = (r.get("cuisine") or "").strip().lower()
        uniq[slug] = r
    return list(uniq.values())

def _refresh() -> None:
    global RECIPES_LIST, RECIPES
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    RECIPES_LIST = _normalize_list(raw)
    RECIPES = {r["slug"]: r for r in RECIPES_LIST}

def reload_data() -> int:
    _refresh()
    return len(RECIPES_LIST)

# initial load
_refresh()

def _dedupe(items: List[dict]) -> List[dict]:
    return list({r["slug"]: r for r in items}.values())

def get_all_recipes() -> List[dict]:
    return RECIPES_LIST

def get_recipes_by_cuisine(cuisine: str) -> List[dict]:
    """Exact match first (case/space-insensitive), then partial contains as fallback."""
    c = (cuisine or "").strip().lower()
    exact = [r for r in RECIPES_LIST if r.get("cuisine_norm","") == c]
    if exact:
        return _dedupe(exact)
    # partial contains (so 'north' or 'indian' still returns stuff)
    part = [r for r in RECIPES_LIST if c and c in r.get("cuisine_norm","")]
    return _dedupe(part)

def get_all_cuisines() -> List[str]:
    return sorted({r.get("cuisine","") for r in RECIPES_LIST if r.get("cuisine")})

def basic_search(q: str, cuisine: Optional[str] = None) -> List[dict]:
    ql = (q or "").lower().strip()
    pool = get_recipes_by_cuisine(cuisine) if cuisine else RECIPES_LIST
    if not ql:
        return pool
    hits = []
    for r in pool:
        hay = " ".join([r.get("title",""), r.get("cuisine","")] + r.get("ingredients", [])).lower()
        if ql in hay:
            hits.append(r)
    return _dedupe(hits)

# handy stats (used by /recipes/__stats)
def cuisine_counts() -> Dict[str, int]:
    return dict(Counter([r.get("cuisine","") for r in RECIPES_LIST]))
