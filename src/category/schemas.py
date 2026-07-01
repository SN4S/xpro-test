from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    parent_category_id: int = Field(default=0, ge=0)
    seo_keyword: str | None = Field(default=None, max_length=255)
    meta_title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = None
    meta_keyword: str | None = Field(default=None, max_length=255)
    image: str | None = Field(default=None, max_length=512)
    status: int = Field(default=1, ge=0, le=1)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    parent_category_id: int | None = Field(default=None, ge=0)
    seo_keyword: str | None = Field(default=None, max_length=255)
    meta_title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = None
    meta_keyword: str | None = Field(default=None, max_length=255)
    image: str | None = Field(default=None, max_length=512)
    status: int | None = Field(default=None, ge=0, le=1)


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    name: str
    description: str | None = None
    parent_category_id: int | None = None
    seo_keyword: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keyword: str | None = None
    image: str | None = None
    status: int
    date_added: datetime | None = None
    date_modify: datetime | None = None


class CategoryListItem(BaseModel):
    """Category item in list view — includes full path."""

    category_id: int
    name: str  # full path like "Для мотоцикліста > Аксесуари > Рюкзаки"
    status: str  # "Включена" or "Выключена"


class CategoryListResponse(BaseModel):
    items: list[CategoryListItem]
    total: int
    page: int
    per_page: int
    pages: int
