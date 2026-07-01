from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.category import service as category_service
from src.category.models import Category
from src.database import get_db
from src.exceptions import NotFound

DbDep = Annotated[AsyncSession, Depends(get_db)]


async def valid_category_id(
    category_id: int,
    db: DbDep,
) -> Category:
    """Dependency that validates and returns a category by ID."""
    category = await category_service.get_category_by_id(db, category_id)
    if not category:
        raise NotFound(detail=f"Category with id {category_id} not found")
    return category


CategoryDep = Annotated[Category, Depends(valid_category_id)]
