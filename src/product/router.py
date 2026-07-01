import math

from fastapi import APIRouter, Query, status

from src.category import service as category_service
from src.product import service as product_service
from src.product.dependencies import (
    DbDep,
    ProductAttributeDep,
    ProductCategoryDep,
    ProductDep,
    ProductImageDep,
    ProductStoreDep,
)
from src.product.schemas import (
    ManufacturerResponse,
    ProductAttributeCreate,
    ProductAttributeResponse,
    ProductAttributeUpdate,
    ProductCategoryCreate,
    ProductCategoryResponse,
    ProductCreate,
    ProductDetailResponse,
    ProductImageCreate,
    ProductImageResponse,
    ProductImageUpdate,
    ProductListItem,
    ProductListResponse,
    ProductResponse,
    ProductStoreResponse,
    ProductUpdate,
)

router = APIRouter(prefix="/product", tags=["product"])


# ─── Product CRUD ───────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=ProductListResponse,
    summary="Get product list",
    description="Returns a paginated list of products with filtering, sorting.",
)
async def get_products(
    db: DbDep,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    category_id: int | None = Query(default=None, description="Filter by category"),
    price_from: float | None = Query(default=None, ge=0, description="Min price"),
    price_to: float | None = Query(default=None, ge=0, description="Max price"),
    sort_by: str = Query(default="name", description="Sort by: name, price, category"),
    sort_order: str = Query(default="asc", description="asc or desc"),
) -> ProductListResponse:
    items, total = await product_service.get_product_list(
        db,
        page=page,
        per_page=per_page,
        category_id=category_id,
        price_from=price_from,
        price_to=price_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pages = math.ceil(total / per_page) if total > 0 else 1

    return ProductListResponse(
        items=[ProductListItem(**item) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Get product details",
    description="Returns full product data with all categories, attributes, images, stores, manufacturer.",
)
async def get_product(
    product: ProductDep,
    db: DbDep,
) -> ProductDetailResponse:
    # Build category full paths
    all_categories = await category_service.get_all_categories(db)
    full_paths = category_service.build_full_paths(all_categories)

    # Build category responses with names
    cat_responses = []
    for pc in product.categories:
        cat_responses.append(
            ProductCategoryResponse(
                product_category_id=pc.product_category_id,
                product_id=pc.product_id,
                category_id=pc.category_id,
                category_name=full_paths.get(pc.category_id, ""),
            )
        )

    # Build store responses with names
    store_responses = []
    for ps in product.stores:
        store_responses.append(
            ProductStoreResponse(
                product_store_id=ps.product_store_id,
                product_id=ps.product_id,
                store_id=ps.store_id,
                store_name=ps.store.name if ps.store else None,
            )
        )

    # Manufacturer
    manufacturer = None
    if product.manufacturer:
        manufacturer = ManufacturerResponse.model_validate(product.manufacturer)

    return ProductDetailResponse(
        product_id=product.product_id,
        name=product.name,
        description=product.description,
        seo_keyword=product.seo_keyword,
        meta_title=product.meta_title,
        meta_description=product.meta_description,
        meta_keyword=product.meta_keyword,
        image=product.image,
        status=product.status,
        price=product.price,
        model=product.model,
        manufacturer_id=product.manufacturer_id,
        rating=product.rating,
        viewed=product.viewed,
        date_added=product.date_added,
        date_modify=product.date_modify,
        categories=cat_responses,
        attributes=[
            ProductAttributeResponse.model_validate(a) for a in product.attributes
        ],
        images=[
            ProductImageResponse.model_validate(i) for i in product.images
        ],
        stores=store_responses,
        manufacturer=manufacturer,
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product",
    description="Creates a product. Optionally accepts arrays of categories, attributes, and images.",
)
async def create_product(
    data: ProductCreate,
    db: DbDep,
) -> ProductResponse:
    product = await product_service.create_product(db, data.model_dump())
    return ProductResponse.model_validate(product)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update a product",
    description="Partially updates a product. Cannot modify product_id, date_added, date_modify.",
)
async def update_product(
    data: ProductUpdate,
    product: ProductDep,
    db: DbDep,
) -> ProductResponse:
    update_data = data.model_dump(exclude_unset=True)
    product = await product_service.update_product(db, product, update_data)
    return ProductResponse.model_validate(product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    description="Deletes a product and all its relations.",
)
async def delete_product(
    product: ProductDep,
    db: DbDep,
) -> None:
    await product_service.delete_product(db, product)


# ─── Product Images ─────────────────────────────────────────────────────────────


@router.get(
    "/{product_id}/image",
    response_model=list[ProductImageResponse],
    summary="Get product images",
    description="Returns all additional images for a product.",
)
async def get_product_images(
    product: ProductDep,
    db: DbDep,
) -> list[ProductImageResponse]:
    images = await product_service.get_product_images(db, product.product_id)
    return [ProductImageResponse.model_validate(i) for i in images]


@router.get(
    "/{product_id}/image/{product_image_id}",
    response_model=ProductImageResponse,
    summary="Get a product image",
)
async def get_product_image(
    image: ProductImageDep,
) -> ProductImageResponse:
    return ProductImageResponse.model_validate(image)


@router.post(
    "/{product_id}/image",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a product image",
)
async def create_product_image(
    data: ProductImageCreate,
    product: ProductDep,
    db: DbDep,
) -> ProductImageResponse:
    image = await product_service.create_product_image(
        db, product.product_id, data.model_dump()
    )
    return ProductImageResponse.model_validate(image)


@router.patch(
    "/{product_id}/image/{product_image_id}",
    response_model=ProductImageResponse,
    summary="Update product image sort order",
)
async def update_product_image(
    data: ProductImageUpdate,
    image: ProductImageDep,
    db: DbDep,
) -> ProductImageResponse:
    image = await product_service.update_product_image(db, image, data.sort_order)
    return ProductImageResponse.model_validate(image)


@router.delete(
    "/{product_id}/image/{product_image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product image",
)
async def delete_product_image(
    image: ProductImageDep,
    db: DbDep,
) -> None:
    await product_service.delete_product_image(db, image)


# ─── Product Categories ─────────────────────────────────────────────────────────


@router.get(
    "/{product_id}/category",
    response_model=list[ProductCategoryResponse],
    summary="Get product categories",
    description="Returns all categories linked to a product, with category names.",
)
async def get_product_categories(
    product: ProductDep,
    db: DbDep,
) -> list[ProductCategoryResponse]:
    pcs = await product_service.get_product_categories(db, product.product_id)
    all_categories = await category_service.get_all_categories(db)
    full_paths = category_service.build_full_paths(all_categories)

    return [
        ProductCategoryResponse(
            product_category_id=pc.product_category_id,
            product_id=pc.product_id,
            category_id=pc.category_id,
            category_name=full_paths.get(pc.category_id, ""),
        )
        for pc in pcs
    ]


@router.get(
    "/{product_id}/category/{product_category_id}",
    response_model=ProductCategoryResponse,
    summary="Get a product category link",
)
async def get_product_category(
    pc: ProductCategoryDep,
    db: DbDep,
) -> ProductCategoryResponse:
    all_categories = await category_service.get_all_categories(db)
    full_paths = category_service.build_full_paths(all_categories)

    return ProductCategoryResponse(
        product_category_id=pc.product_category_id,
        product_id=pc.product_id,
        category_id=pc.category_id,
        category_name=full_paths.get(pc.category_id, ""),
    )


@router.post(
    "/{product_id}/category",
    response_model=ProductCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a category to product",
)
async def create_product_category(
    data: ProductCategoryCreate,
    product: ProductDep,
    db: DbDep,
) -> ProductCategoryResponse:
    pc = await product_service.create_product_category(
        db, product.product_id, data.category_id
    )
    all_categories = await category_service.get_all_categories(db)
    full_paths = category_service.build_full_paths(all_categories)

    return ProductCategoryResponse(
        product_category_id=pc.product_category_id,
        product_id=pc.product_id,
        category_id=pc.category_id,
        category_name=full_paths.get(pc.category_id, ""),
    )


@router.delete(
    "/{product_id}/category/{product_category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove category from product",
)
async def delete_product_category(
    pc: ProductCategoryDep,
    db: DbDep,
) -> None:
    await product_service.delete_product_category(db, pc)


# ─── Product Attributes ─────────────────────────────────────────────────────────


@router.get(
    "/{product_id}/attribute",
    response_model=list[ProductAttributeResponse],
    summary="Get product attributes",
)
async def get_product_attributes(
    product: ProductDep,
    db: DbDep,
) -> list[ProductAttributeResponse]:
    attrs = await product_service.get_product_attributes(db, product.product_id)
    return [ProductAttributeResponse.model_validate(a) for a in attrs]


@router.get(
    "/{product_id}/attribute/{product_attribute_id}",
    response_model=ProductAttributeResponse,
    summary="Get a product attribute",
)
async def get_product_attribute(
    attr: ProductAttributeDep,
) -> ProductAttributeResponse:
    return ProductAttributeResponse.model_validate(attr)


@router.post(
    "/{product_id}/attribute",
    response_model=ProductAttributeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a product attribute",
)
async def create_product_attribute(
    data: ProductAttributeCreate,
    product: ProductDep,
    db: DbDep,
) -> ProductAttributeResponse:
    attr = await product_service.create_product_attribute(
        db, product.product_id, data.model_dump()
    )
    return ProductAttributeResponse.model_validate(attr)


@router.patch(
    "/{product_id}/attribute/{product_attribute_id}",
    response_model=ProductAttributeResponse,
    summary="Update a product attribute",
    description="Updates an attribute. Cannot modify product_attribute_id and product_id.",
)
async def update_product_attribute(
    data: ProductAttributeUpdate,
    attr: ProductAttributeDep,
    db: DbDep,
) -> ProductAttributeResponse:
    update_data = data.model_dump(exclude_unset=True)
    attr = await product_service.update_product_attribute(db, attr, update_data)
    return ProductAttributeResponse.model_validate(attr)


@router.delete(
    "/{product_id}/attribute/{product_attribute_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product attribute",
)
async def delete_product_attribute(
    attr: ProductAttributeDep,
    db: DbDep,
) -> None:
    await product_service.delete_product_attribute(db, attr)


# ─── Product Stores ──────────────────────────────────────────────────────────────


@router.get(
    "/{product_id}/store",
    response_model=list[ProductStoreResponse],
    summary="Get product stores",
    description="Returns all stores linked to this product.",
)
async def get_product_stores(
    product: ProductDep,
    db: DbDep,
) -> list[ProductStoreResponse]:
    pss = await product_service.get_product_stores(db, product.product_id)
    return [
        ProductStoreResponse(
            product_store_id=ps.product_store_id,
            product_id=ps.product_id,
            store_id=ps.store_id,
            store_name=ps.store.name if ps.store else None,
        )
        for ps in pss
    ]


@router.get(
    "/{product_id}/store/{product_store_id}",
    response_model=ProductStoreResponse,
    summary="Get a product store",
)
async def get_product_store(
    ps: ProductStoreDep,
) -> ProductStoreResponse:
    return ProductStoreResponse(
        product_store_id=ps.product_store_id,
        product_id=ps.product_id,
        store_id=ps.store_id,
        store_name=ps.store.name if ps.store else None,
    )
