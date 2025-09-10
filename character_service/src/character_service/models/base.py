"""Base model with common fields."""
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, MetaData, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Convention for constraint naming
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


class UTCDateTime(TypeDecorator):
    """Custom DateTime type that always stores UTC."""
    
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.astimezone(UTC).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return datetime.fromisoformat(value.isoformat()).replace(tzinfo=UTC)
        return value


class Base(DeclarativeBase):
    """Base model class with common fields."""
    
    metadata = metadata
    
    id: Mapped[UUID] = mapped_column(
        PGUUID, 
        primary_key=True, 
        default=uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        nullable=False,
    default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        nullable=False,
    default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )
    deleted_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        nullable=True
    )
