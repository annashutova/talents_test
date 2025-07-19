from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.talents.question import Question
    from webapp.models.talents.user_answer import UserAnswer


class Answer(Base):
    __tablename__ = 'answer'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    answer_content: Mapped[str] = mapped_column(Text, nullable=False)

    a_param: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    b_param: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    c_param: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    question_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DEFAULT_SCHEMA}.question.id"), nullable=False
    )
    question: Mapped["Question"] = relationship(back_populates="answers")

    tests: Mapped[List["UserAnswer"]] = relationship(back_populates="answer")
