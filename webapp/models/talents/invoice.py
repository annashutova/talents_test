import enum
from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, Double
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from webapp.models.meta import Base, DEFAULT_SCHEMA


class InvoiceStatusEnum(enum.Enum):
    paid = "paid"
    not_paid = "not_paid"


class Invoice(Base):
    __tablename__ = 'invoice'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    amount: Mapped[float] = mapped_column(Double, nullable=False, unique=True)

    status: Mapped[enum.Enum] = mapped_column(ENUM(InvoiceStatusEnum), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow)

    test_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.user_test.id"), nullable=False, unique=True)
