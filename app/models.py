from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.types import JSON
from .database import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(128), unique=True, index=True, nullable=False)
    title = Column(String(256), nullable=False)
    cuisine = Column(String(64), index=True)
    time_total = Column(Integer)
    servings = Column(Integer)
    ingredients = Column(JSON)   # list[str]
    steps = Column(JSON)         # list[str]
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
