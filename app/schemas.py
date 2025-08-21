from typing import List, Optional
from pydantic import BaseModel, Field

class RecipeBase(BaseModel):
    slug: str = Field(..., regex=r"^[a-z0-9-]+$")
    title: str
    cuisine: str
    time_total: int
    servings: int
    ingredients: List[str]
    steps: List[str]

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    cuisine: Optional[str] = None
    time_total: Optional[int] = None
    servings: Optional[int] = None
    ingredients: Optional[List[str]] = None
    steps: Optional[List[str]] = None

class RecipeOut(RecipeBase):
    id: int

    class Config:
        orm_mode = True
