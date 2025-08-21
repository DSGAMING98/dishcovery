from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
def ping():
    return {"ok": True, "feature": "pantry-to-plate (stub)"}
