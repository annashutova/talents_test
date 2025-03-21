from sqlalchemy import Integer, String, DateTime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
import enum
from typing import List, TYPE_CHECKING

from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.talents.user_test import UserTest


class GenderEnum(enum.Enum):
    male = 'male'
    female = 'female'
    other = 'other'


class User(Base):
    __tablename__ = 'user'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)

    first_name: Mapped[str] = mapped_column(String(50), nullable=True)

    last_name: Mapped[str] = mapped_column(String(50), nullable=True)

    surname: Mapped[str] = mapped_column(String(50), nullable=True)

    date_of_birth: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    gender: Mapped[enum.Enum] = mapped_column(ENUM(GenderEnum), nullable=False)

    tests: Mapped[List["UserTest"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
