from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List, TYPE_CHECKING

from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.talents.interpretation import Interpretation
    from webapp.models.talents.question import Question
    from webapp.models.talents.user_result import UserResult


class Trait(Base):
    __tablename__ = 'trait'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    trait_lack: Mapped[str] = mapped_column(String(50), nullable=False)

    trait_virtue: Mapped[str] = mapped_column(String(50), nullable=False)

    trait_excess: Mapped[str] = mapped_column(String(50), nullable=False)

    questions: Mapped[List["Question"]] = relationship(back_populates="trait")

    interpretations: Mapped[List["Interpretation"]] = relationship(back_populates="trait")

    results: Mapped[List["UserResult"]] = relationship(back_populates="trait")
