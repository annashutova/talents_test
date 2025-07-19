from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.talents.user_test import UserTest
    from webapp.models.talents.answer import Answer


class UserAnswer(Base):
    __tablename__ = 'user_answer'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    response_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    test_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.user_test.id", ondelete="CASCADE"))
    test: Mapped["UserTest"] = relationship(back_populates="answers")

    answer_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.answer.id"), nullable=False)
    answer: Mapped["Answer"] = relationship(back_populates="tests")
