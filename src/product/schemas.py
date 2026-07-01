from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ─── Product ────────────────────────────────────────────────────────────────────


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    seo_keyword: str | None = Field(default=None, max_length=255)
    meta_title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = None
    meta_keyword: str | None = Field(default=None, max_length=255)
    image: str | None = Field(default=None, max_length=512)
    status: int = Field(default=0, ge=0, le=1)
    price: float | None = Field(default=0.0, ge=0)
    model: str | None = Field(default=None, max_length=255)
    manufacturer_id: int | None = None
    rating: float | None = Field(default=0.0, ge=0, le=5)
    viewed: int = Field(default=0, ge=0)

    # Nested arrays for bulk creation
    categories: list[int] | None = Field(
        default=None, description="List of category IDs"
    )
    attributes: list["ProductAttributeCreate"] | None = None
    images: list["ProductImageCreate"] | None = None


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    seo_keyword: str | None = Field(default=None, max_length=255)
    meta_title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = None
    meta_keyword: str | None = Field(default=None, max_length=255)
    image: str | None = Field(default=None, max_length=512)
    status: int | None = Field(default=None, ge=0, le=1)
    price: float | None = Field(default=None, ge=0)
    model: str | None = Field(default=None, max_length=255)
    manufacturer_id: int | None = None
    rating: float | None = Field(default=None, ge=0, le=5)
    viewed: int | None = Field(default=None, ge=0)


class ManufacturerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    manufacturer_id: int
    name: str


class ProductCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_category_id: int
    product_id: int
    category_id: int
    category_name: str | None = None  # full path


class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_image_id: int
    product_id: int
    image: str
    sort_order: int


class ProductAttributeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_attribute_id: int
    product_id: int
    group_name: str | None = None
    name: str
    value: str | None = None
    sort_order: int


class ProductStoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_store_id: int
    product_id: int
    store_id: int
    store_name: str | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    name: str
    description: str | None = None
    seo_keyword: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keyword: str | None = None
    image: str | None = None
    status: int
    price: float | None = None
    model: str | None = None
    manufacturer_id: int | None = None
    rating: float | None = None
    viewed: int = 0
    date_added: datetime | None = None
    date_modify: datetime | None = None


class ProductDetailResponse(ProductResponse):
    """Full product detail with all related data."""

    categories: list[ProductCategoryResponse] = []
    attributes: list[ProductAttributeResponse] = []
    images: list[ProductImageResponse] = []
    stores: list[ProductStoreResponse] = []
    manufacturer: ManufacturerResponse | None = None


class ProductListItem(BaseModel):
    product_id: int
    name: str
    category_name: str | None = None  # full path of primary category
    price: float | None = None


class ProductListResponse(BaseModel):
    items: list[ProductListItem]
    total: int
    page: int
    per_page: int
    pages: int


# ─── Sub-resource creation schemas ──────────────────────────────────────────────


class ProductImageCreate(BaseModel):
    image: str = Field(max_length=512)
    sort_order: int = Field(default=0, ge=0)


class ProductImageUpdate(BaseModel):
    sort_order: int = Field(ge=0)


class ProductCategoryCreate(BaseModel):
    category_id: int


class ProductAttributeCreate(BaseModel):
    group_name: str | None = Field(default=None, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    value: str | None = None
    sort_order: int = Field(default=0, ge=0)


class ProductAttributeUpdate(BaseModel):
    group_name: str | None = Field(default=None, max_length=255)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    value: str | None = None
    sort_order: int | None = Field(default=None, ge=0)
