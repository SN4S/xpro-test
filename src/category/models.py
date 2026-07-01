from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, TimestampMixin





class Category(Base, TimestampMixin):
    __tablename__ = "category"

    category_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_category_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("category.category_id", ondelete="CASCADE"),
        nullable=True,
        default=None,
    )
    seo_keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[int] = mapped_column(
        Integer, default=1
    )

    # Self-referential relationships
    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side=[category_id],
        back_populates="children",
        lazy="selectin",
    )
    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
