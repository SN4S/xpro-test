from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.product import service as product_service
from src.product.models import (
    Product,
    ProductAttribute,
    ProductCategory,
    ProductImage,
    ProductStore,
)
from src.database import get_db
from src.exceptions import NotFound

DbDep = Annotated[AsyncSession, Depends(get_db)]


async def valid_product_id(
    product_id: int,
    db: DbDep,
) -> Product:
    """Dependency that validates and returns a product by ID."""
    product = await product_service.get_product_by_id(db, product_id)
    if not product:
        raise NotFound(detail=f"Product with id {product_id} not found")
    return product


ProductDep = Annotated[Product, Depends(valid_product_id)]


async def valid_product_image_id(
    product_id: int,
    product_image_id: int,
    db: DbDep,
) -> ProductImage:
    """Dependency that validates product image belongs to product."""
    image = await product_service.get_product_image(db, product_id, product_image_id)
    if not image:
        raise NotFound(
            detail=f"Product image {product_image_id} not found for product {product_id}"
        )
    return image


ProductImageDep = Annotated[ProductImage, Depends(valid_product_image_id)]


async def valid_product_category_id(
    product_id: int,
    product_category_id: int,
    db: DbDep,
) -> ProductCategory:
    """Dependency that validates product category link."""
    pc = await product_service.get_product_category(
        db, product_id, product_category_id
    )
    if not pc:
        raise NotFound(
            detail=f"Product category {product_category_id} not found for product {product_id}"
        )
    return pc


ProductCategoryDep = Annotated[ProductCategory, Depends(valid_product_category_id)]


async def valid_product_attribute_id(
    product_id: int,
    product_attribute_id: int,
    db: DbDep,
) -> ProductAttribute:
    """Dependency that validates product attribute belongs to product."""
    attr = await product_service.get_product_attribute(
        db, product_id, product_attribute_id
    )
    if not attr:
        raise NotFound(
            detail=f"Product attribute {product_attribute_id} not found for product {product_id}"
        )
    return attr


ProductAttributeDep = Annotated[ProductAttribute, Depends(valid_product_attribute_id)]


async def valid_product_store_id(
    product_id: int,
    product_store_id: int,
    db: DbDep,
) -> ProductStore:
    """Dependency that validates product store link."""
    ps = await product_service.get_product_store(
        db, product_id, product_store_id
    )
    if not ps:
        raise NotFound(
            detail=f"Product store {product_store_id} not found for product {product_id}"
        )
    return ps


ProductStoreDep = Annotated[ProductStore, Depends(valid_product_store_id)]
