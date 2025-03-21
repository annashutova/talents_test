import enum
from typing import TYPE_CHECKING

from sqlalchemy import Integer, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.talents.trait import Trait


class TraitDegreeEnum(enum.Enum):
    trait_lack = "trait_lack"
    trait_virtue = "trait_virtue"
    trait_excess = "trait_excess"


class Interpretation(Base):
    __tablename__ = 'interpretation'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    trait_degree: Mapped[enum.Enum] = mapped_column(ENUM(TraitDegreeEnum), nullable=False)

    lower_bound: Mapped[float] = mapped_column(Float, nullable=False)

    upper_bound: Mapped[float] = mapped_column(Float, nullable=False)

    short_description: Mapped[str] = mapped_column(Text, nullable=False)

    long_description: Mapped[str] = mapped_column(Text, nullable=False)

    trait_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.trait.id"), nullable=False)
    trait: Mapped["Trait"] = relationship(back_populates="interpretations")
