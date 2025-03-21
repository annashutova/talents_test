from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.talents.user_test import UserTest
    from webapp.models.talents.trait import Trait


class UserResult(Base):
    __tablename__ = 'user_result'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    a_param: Mapped[float] = mapped_column(Float, nullable=False)

    b_param: Mapped[float] = mapped_column(Float, nullable=False)

    c_param: Mapped[float] = mapped_column(Float, nullable=False)

    test_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.user_test.id", ondelete="CASCADE"))
    test: Mapped["UserTest"] = relationship(back_populates="results")

    trait_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.trait.id"), nullable=False)
    trait: Mapped["Trait"] = relationship(back_populates="results")
