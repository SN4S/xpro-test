from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, TimestampMixin





class Product(Base, TimestampMixin):
    __tablename__ = "product"

    product_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    seo_keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[int] = mapped_column(
        Integer, default=0
    )
    price: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacturer_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("manufacturer.manufacturer_id", ondelete="SET NULL"),
        nullable=True,
    )
    rating: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    viewed: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    categories: Mapped[list["ProductCategory"]] = relationship(
        "ProductCategory",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attributes: Mapped[list["ProductAttribute"]] = relationship(
        "ProductAttribute",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    stores: Mapped[list["ProductStore"]] = relationship(
        "ProductStore",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    manufacturer: Mapped["Manufacturer | None"] = relationship(
        "Manufacturer",
        back_populates="products",
        lazy="selectin",
    )


class ProductCategory(Base):
    __tablename__ = "product_category"
    __table_args__ = (
        UniqueConstraint("product_id", "category_id", name="uq_product_category"),
    )

    product_category_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("category.category_id", ondelete="CASCADE"),
        nullable=False,
    )

    product: Mapped["Product"] = relationship(
        "Product", back_populates="categories", lazy="selectin"
    )
    category: Mapped["Category"] = relationship(
        "Category", lazy="selectin"
    )


class ProductImage(Base):
    __tablename__ = "product_image"

    product_image_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    image: Mapped[str] = mapped_column(String(512), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship(
        "Product", back_populates="images", lazy="selectin"
    )


class ProductAttribute(Base):
    __tablename__ = "product_attribute"

    product_attribute_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    group_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship(
        "Product", back_populates="attributes", lazy="selectin"
    )


class Manufacturer(Base):
    __tablename__ = "manufacturer"

    manufacturer_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="manufacturer", lazy="selectin"
    )


class Store(Base):
    __tablename__ = "store"

    store_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    product_stores: Mapped[list["ProductStore"]] = relationship(
        "ProductStore", back_populates="store", lazy="selectin"
    )


class ProductStore(Base):
    __tablename__ = "product_store"
    __table_args__ = (
        UniqueConstraint("product_id", "store_id", name="uq_product_store"),
    )

    product_store_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    store_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("store.store_id", ondelete="CASCADE"),
        nullable=False,
    )

    product: Mapped["Product"] = relationship(
        "Product", back_populates="stores", lazy="selectin"
    )
    store: Mapped["Store"] = relationship(
        "Store", back_populates="product_stores", lazy="selectin"
    )


# Import Category for relationship resolution
from src.category.models import Category  # noqa: E402, F401
