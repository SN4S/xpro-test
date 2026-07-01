from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.category.models import Category


async def get_all_categories(db: AsyncSession) -> list[Category]:
    """Load all categories from the database."""
    result = await db.execute(select(Category))
    return list(result.scalars().unique().all())


def build_full_paths(categories: list[Category]) -> dict[int, str]:
    """Build a mapping of category_id -> full path string.

    Example: {3: "Для мотоцикліста > Аксесуари > Рюкзаки"}
    """
    cat_map: dict[int, Category] = {c.category_id: c for c in categories}
    path_cache: dict[int, str] = {}

    def _get_path(cat_id: int) -> str:
        if cat_id in path_cache:
            return path_cache[cat_id]

        cat = cat_map.get(cat_id)
        if cat is None:
            return ""

        parent_id = cat.parent_category_id
        if parent_id and parent_id != 0 and parent_id in cat_map:
            parent_path = _get_path(parent_id)
            path = f"{parent_path} > {cat.name}" if parent_path else cat.name
        else:
            path = cat.name

        path_cache[cat_id] = path
        return path

    for cat in categories:
        _get_path(cat.category_id)

    return path_cache


async def get_category_list(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    search_id: int | None = None,
    status_filter: int | None = None,
    sort_by: str = "name",
    sort_order: str = "asc",
) -> tuple[list[dict], int]:
    """Get paginated category list with full paths.

    Returns (items, total_count).
    """
    all_categories = await get_all_categories(db)
    full_paths = build_full_paths(all_categories)

    # Build list items
    items = []
    for cat in all_categories:
        full_name = full_paths.get(cat.category_id, cat.name)
        status_label = "Включена" if cat.status == 1 else "Выключена"

        items.append(
            {
                "category_id": cat.category_id,
                "name": full_name,
                "status": status_label,
                "raw_status": cat.status,
            }
        )

    # Apply search filter
    if search:
        search_lower = search.lower()
        items = [i for i in items if search_lower in i["name"].lower()]

    if search_id is not None:
        items = [i for i in items if i["category_id"] == search_id]

    # Apply status filter
    if status_filter is not None:
        items = [i for i in items if i["raw_status"] == status_filter]

    # Sort
    reverse = sort_order.lower() == "desc"
    if sort_by == "name":
        items.sort(key=lambda x: x["name"].lower(), reverse=reverse)
    elif sort_by == "category_id":
        items.sort(key=lambda x: x["category_id"], reverse=reverse)

    total = len(items)

    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    paginated = items[start:end]

    return paginated, total


async def get_category_by_id(db: AsyncSession, category_id: int) -> Category | None:
    """Get a single category by ID."""
    result = await db.execute(
        select(Category).where(Category.category_id == category_id)
    )
    return result.scalars().first()


async def create_category(db: AsyncSession, data: dict) -> Category:
    """Create a new category."""
    # Convert parent_category_id=0 to None for FK constraint
    if data.get("parent_category_id") == 0:
        data["parent_category_id"] = None

    category = Category(**data)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession, category: Category, data: dict
) -> Category:
    """Update a category with the given data."""
    for key, value in data.items():
        if value is not None:
            if key == "parent_category_id" and value == 0:
                setattr(category, key, None)
            else:
                setattr(category, key, value)

    category.date_modify = datetime.utcnow()
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category_recursive(db: AsyncSession, category_id: int) -> None:
    """Delete a category and all its subcategories recursively."""
    category = await get_category_by_id(db, category_id)
    if category is None:
        return

    # Collect all descendant IDs
    descendant_ids = []
    await _collect_descendants(db, category_id, descendant_ids)

    # Delete descendants bottom-up (children first)
    for desc_id in reversed(descendant_ids):
        desc = await get_category_by_id(db, desc_id)
        if desc:
            await db.delete(desc)

    # Delete the category itself
    await db.delete(category)
    await db.commit()


async def _collect_descendants(
    db: AsyncSession, parent_id: int, result: list[int]
) -> None:
    """Recursively collect all descendant category IDs."""
    stmt = select(Category.category_id).where(
        Category.parent_category_id == parent_id
    )
    res = await db.execute(stmt)
    child_ids = [row[0] for row in res.fetchall()]

    for child_id in child_ids:
        result.append(child_id)
        await _collect_descendants(db, child_id, result)
