from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger
from webapp.middleware.metrics import integration_latency
from webapp.models.talents.user import User
from webapp.schema.user import UserInfo


@integration_latency
async def get_user(session: AsyncSession, username: str) -> User | None:
    logger.info('Selecting user by username: %s', username)
    return (
        await session.scalars(
            select(User).where(
                User.username == username,
            )
        )
    ).one_or_none()


@integration_latency
async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    logger.info('Selecting user by id: %d', user_id)
    return (
        await session.scalars(
            select(User)
            .where(User.id == user_id)
        )
    ).one_or_none()
