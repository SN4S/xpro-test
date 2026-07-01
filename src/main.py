from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import settings
from src.database import engine
from src.models import Base

# Import all models so they are registered with the metadata
from src.category.models import Category  # noqa: F401
from src.product.models import (  # noqa: F401
    Manufacturer,
    Product,
    ProductAttribute,
    ProductCategory,
    ProductImage,
    ProductStore,
    Store,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all tables on startup (for development convenience)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


SHOW_DOCS_IN = {"local", "staging"}
app_kwargs = {
    "title": "Category & Product API",
    "description": "API for managing categories, products, and their relations",
    "version": "1.0.0",
    "lifespan": lifespan,
}
if settings.ENVIRONMENT not in SHOW_DOCS_IN:
    app_kwargs["openapi_url"] = None

app = FastAPI(**app_kwargs)

# Include routers
from src.category.router import router as category_router  # noqa: E402
from src.product.router import router as product_router  # noqa: E402

app.include_router(category_router)
app.include_router(product_router)


@app.get("/", tags=["health"])
async def health_check():
    return {"status": "ok", "message": "Category & Product API is running"}
