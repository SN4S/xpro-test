from datetime import datetime

from sqlalchemy import MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

MYSQL_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

metadata = MetaData(naming_convention=MYSQL_NAMING_CONVENTION)


class Base(DeclarativeBase):
    metadata = metadata


class TimestampMixin:
    """Mixin that adds date_added and date_modify columns."""

    date_added: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )
    date_modify: Mapped[datetime | None] = mapped_column(
        default=None,
        onupdate=func.now(),
        server_onupdate=func.now(),
    )
