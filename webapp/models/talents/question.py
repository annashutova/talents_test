from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List, TYPE_CHECKING

from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.talents.trait import Trait
    from webapp.models.talents.answer import Answer


class Question(Base):
    __tablename__ = 'question'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    question_content: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    trait_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.trait.id"), nullable=False)
    trait: Mapped["Trait"] = relationship(back_populates="questions")

    answers: Mapped[List["Answer"]] = relationship(back_populates="question")
