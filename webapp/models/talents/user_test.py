from typing import List, TYPE_CHECKING
import enum
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.talents.user import User
    from webapp.models.talents.user_answer import UserAnswer
    from webapp.models.talents.user_result import UserResult


class StatusEnum(enum.Enum):
    started = 'started'
    in_progress = 'in_progress'
    finished = 'finished'


class UserTest(Base):
    __tablename__ = 'user_test'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    status: Mapped[enum.Enum] = mapped_column(ENUM(StatusEnum), nullable=False)

    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.user.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="tests")

    answers: Mapped[List["UserAnswer"]] = relationship(back_populates="test")

    results: Mapped[List["UserResult"]] = relationship(
        back_populates="test",
        cascade="all, delete",
        passive_deletes=True,
    )
