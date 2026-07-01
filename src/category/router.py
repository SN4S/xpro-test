import math

from fastapi import APIRouter, Query, status

from src.category import service as category_service
from src.category.dependencies import CategoryDep, DbDep
from src.category.schemas import (
    CategoryCreate,
    CategoryListItem,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)

router = APIRouter(prefix="/category", tags=["category"])


@router.get(
    "",
    response_model=CategoryListResponse,
    summary="Get category list",
    description="Returns a paginated list of categories with full hierarchical paths, "
    "supporting search, filtering, and sorting.",
)
async def get_categories(
    db: DbDep,
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(default=None, description="Search by category name"),
    search_id: int | None = Query(default=None, description="Search by category ID"),
    status: int | None = Query(default=None, ge=0, le=1, description="Filter by status (1=Enabled, 0=Disabled)"),
    sort_by: str = Query(default="name", description="Sort field: name, category_id"),
    sort_order: str = Query(default="asc", description="Sort order: asc (А-Я), desc (Я-А)"),
) -> CategoryListResponse:
    items, total = await category_service.get_category_list(
        db,
        page=page,
        per_page=per_page,
        search=search,
        search_id=search_id,
        status_filter=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pages = math.ceil(total / per_page) if total > 0 else 1

    return CategoryListResponse(
        items=[
            CategoryListItem(
                category_id=item["category_id"],
                name=item["name"],
                status=item["status"],
            )
            for item in items
        ],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category details",
    description="Returns all data about a specific category.",
)
async def get_category(category: CategoryDep) -> CategoryResponse:
    return CategoryResponse.model_validate(category)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
    description="Creates a new category. Set parent_category_id=0 for a root category.",
)
async def create_category(
    data: CategoryCreate,
    db: DbDep,
) -> CategoryResponse:
    category = await category_service.create_category(
        db, data.model_dump()
    )
    return CategoryResponse.model_validate(category)


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update a category",
    description="Partially updates a category. Cannot modify category_id, date_added, date_modify.",
)
async def update_category(
    data: CategoryUpdate,
    category: CategoryDep,
    db: DbDep,
) -> CategoryResponse:
    update_data = data.model_dump(exclude_unset=True)
    category = await category_service.update_category(db, category, update_data)
    return CategoryResponse.model_validate(category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
    description="Deletes a category and all its subcategories recursively.",
)
async def delete_category(
    category: CategoryDep,
    db: DbDep,
) -> None:
    await category_service.delete_category_recursive(db, category.category_id)
