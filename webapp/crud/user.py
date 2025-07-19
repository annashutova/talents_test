from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger
from webapp.infrastructure.middleware.metrics import integration_latency
from webapp.models.talents.user import User
from webapp.schema.user import UserLoginRequest, UserRegisterRequest
from webapp.auth.password import hash_password


@integration_latency
async def get_user_by_creds(session: AsyncSession, user_info: UserLoginRequest) -> User | None:
    logger.info('Selecting user by email: %s', user_info.email)
    return (
        await session.scalars(
            select(User)
            .where(
                User.email == user_info.email,
                User.password == hash_password(user_info.password),
            )
        )
    ).one_or_none()


@integration_latency
async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    logger.info('Selecting user by email: %s', email)
    return (
        await session.scalars(
            select(User)
            .where(User.email == email)
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


@integration_latency
async def create_user(user_data: UserRegisterRequest, session: AsyncSession) -> User | None:
    logger.info('Creating user.')
    user = (
        await session.scalars(
            insert(User)
            .values(
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                surname=user_data.surname,
                email=user_data.email,
                date_of_birth=user_data.date_of_birth,
                password=user_data.password,
                gender=user_data.gender,
            )
            .returning(User)
        )
    ).one_or_none()

    await session.commit()

    return user
