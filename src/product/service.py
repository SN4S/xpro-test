from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.category import service as category_service
from src.product.models import (
    Product,
    ProductAttribute,
    ProductCategory,
    ProductImage,
    ProductStore,
)


# ─── Product CRUD ───────────────────────────────────────────────────────────────


async def get_product_list(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    category_id: int | None = None,
    price_from: float | None = None,
    price_to: float | None = None,
    sort_by: str = "name",
    sort_order: str = "asc",
) -> tuple[list[dict], int]:
    """Get paginated product list with category names."""
    # Build base query
    stmt = select(Product)

    # Filter by category
    if category_id is not None:
        stmt = stmt.join(ProductCategory).where(
            ProductCategory.category_id == category_id
        )

    # Filter by price range
    if price_from is not None:
        stmt = stmt.where(Product.price >= price_from)
    if price_to is not None:
        stmt = stmt.where(Product.price <= price_to)

    result = await db.execute(stmt)
    products = list(result.scalars().unique().all())

    # Build category paths for all products
    all_categories = await category_service.get_all_categories(db)
    full_paths = category_service.build_full_paths(all_categories)

    items = []
    for product in products:
        # Get first category name (full path)
        cat_name = None
        if product.categories:
            first_cat = product.categories[0]
            cat_name = full_paths.get(first_cat.category_id, "")

        items.append(
            {
                "product_id": product.product_id,
                "name": product.name,
                "category_name": cat_name,
                "price": product.price,
            }
        )

    # Sort
    reverse = sort_order.lower() == "desc"
    if sort_by == "name":
        items.sort(key=lambda x: (x["name"] or "").lower(), reverse=reverse)
    elif sort_by == "price":
        items.sort(key=lambda x: x["price"] or 0, reverse=reverse)
    elif sort_by == "category":
        items.sort(key=lambda x: (x["category_name"] or "").lower(), reverse=reverse)

    total = len(items)

    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    paginated = items[start:end]

    return paginated, total


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
    """Get a single product by ID with all relationships."""
    result = await db.execute(
        select(Product).where(Product.product_id == product_id)
    )
    return result.scalars().unique().first()


async def create_product(db: AsyncSession, data: dict) -> Product:
    """Create a product with optional nested data (categories, attributes, images)."""
    categories_data = data.pop("categories", None) or []
    attributes_data = data.pop("attributes", None) or []
    images_data = data.pop("images", None) or []

    product = Product(**data)
    db.add(product)
    await db.flush()

    # Add categories
    for cat_id in categories_data:
        pc = ProductCategory(product_id=product.product_id, category_id=cat_id)
        db.add(pc)

    # Add attributes
    for attr in attributes_data:
        pa = ProductAttribute(
            product_id=product.product_id,
            **attr if isinstance(attr, dict) else attr.model_dump(),
        )
        db.add(pa)

    # Add images
    for img in images_data:
        pi = ProductImage(
            product_id=product.product_id,
            **img if isinstance(img, dict) else img.model_dump(),
        )
        db.add(pi)

    await db.commit()
    await db.refresh(product)
    return product


async def update_product(
    db: AsyncSession, product: Product, data: dict
) -> Product:
    """Update a product."""
    for key, value in data.items():
        if value is not None:
            setattr(product, key, value)

    product.date_modify = datetime.utcnow()
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product: Product) -> None:
    """Delete a product and all its relations (cascade)."""
    await db.delete(product)
    await db.commit()


# ─── Product Images ─────────────────────────────────────────────────────────────


async def get_product_images(
    db: AsyncSession, product_id: int
) -> list[ProductImage]:
    result = await db.execute(
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.sort_order)
    )
    return list(result.scalars().all())


async def get_product_image(
    db: AsyncSession, product_id: int, product_image_id: int
) -> ProductImage | None:
    result = await db.execute(
        select(ProductImage).where(
            ProductImage.product_id == product_id,
            ProductImage.product_image_id == product_image_id,
        )
    )
    return result.scalars().first()


async def create_product_image(
    db: AsyncSession, product_id: int, data: dict
) -> ProductImage:
    img = ProductImage(product_id=product_id, **data)
    db.add(img)
    await db.commit()
    await db.refresh(img)
    return img


async def update_product_image(
    db: AsyncSession, image: ProductImage, sort_order: int
) -> ProductImage:
    image.sort_order = sort_order
    await db.commit()
    await db.refresh(image)
    return image


async def delete_product_image(db: AsyncSession, image: ProductImage) -> None:
    await db.delete(image)
    await db.commit()


# ─── Product Categories ─────────────────────────────────────────────────────────


async def get_product_categories(
    db: AsyncSession, product_id: int
) -> list[ProductCategory]:
    result = await db.execute(
        select(ProductCategory).where(ProductCategory.product_id == product_id)
    )
    return list(result.scalars().unique().all())


async def get_product_category(
    db: AsyncSession, product_id: int, product_category_id: int
) -> ProductCategory | None:
    result = await db.execute(
        select(ProductCategory).where(
            ProductCategory.product_id == product_id,
            ProductCategory.product_category_id == product_category_id,
        )
    )
    return result.scalars().first()


async def create_product_category(
    db: AsyncSession, product_id: int, category_id: int
) -> ProductCategory:
    pc = ProductCategory(product_id=product_id, category_id=category_id)
    db.add(pc)
    await db.commit()
    await db.refresh(pc)
    return pc


async def delete_product_category(
    db: AsyncSession, pc: ProductCategory
) -> None:
    await db.delete(pc)
    await db.commit()


# ─── Product Attributes ─────────────────────────────────────────────────────────


async def get_product_attributes(
    db: AsyncSession, product_id: int
) -> list[ProductAttribute]:
    result = await db.execute(
        select(ProductAttribute)
        .where(ProductAttribute.product_id == product_id)
        .order_by(ProductAttribute.sort_order)
    )
    return list(result.scalars().all())


async def get_product_attribute(
    db: AsyncSession, product_id: int, product_attribute_id: int
) -> ProductAttribute | None:
    result = await db.execute(
        select(ProductAttribute).where(
            ProductAttribute.product_id == product_id,
            ProductAttribute.product_attribute_id == product_attribute_id,
        )
    )
    return result.scalars().first()


async def create_product_attribute(
    db: AsyncSession, product_id: int, data: dict
) -> ProductAttribute:
    attr = ProductAttribute(product_id=product_id, **data)
    db.add(attr)
    await db.commit()
    await db.refresh(attr)
    return attr


async def update_product_attribute(
    db: AsyncSession, attribute: ProductAttribute, data: dict
) -> ProductAttribute:
    for key, value in data.items():
        if value is not None:
            setattr(attribute, key, value)
    await db.commit()
    await db.refresh(attribute)
    return attribute


async def delete_product_attribute(
    db: AsyncSession, attribute: ProductAttribute
) -> None:
    await db.delete(attribute)
    await db.commit()


# ─── Product Stores ──────────────────────────────────────────────────────────────


async def get_product_stores(
    db: AsyncSession, product_id: int
) -> list[ProductStore]:
    result = await db.execute(
        select(ProductStore).where(ProductStore.product_id == product_id)
    )
    return list(result.scalars().unique().all())


async def get_product_store(
    db: AsyncSession, product_id: int, product_store_id: int
) -> ProductStore | None:
    result = await db.execute(
        select(ProductStore).where(
            ProductStore.product_id == product_id,
            ProductStore.product_store_id == product_store_id,
        )
    )
    return result.scalars().first()
