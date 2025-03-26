from typing import Any, Dict, Sequence

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger
from webapp.middleware.metrics import integration_latency
from webapp.models.talents.user_test import UserTest, StatusEnum


@integration_latency
async def get_user_test_by_id(test_id: int, session: AsyncSession) -> UserTest | None:
    logger.info('Selecting test with id = %d', test_id)
    return (
        await session.scalars(
            select(UserTest)
            .where(UserTest.id == test_id)
        )
    ).one_or_none()


@integration_latency
async def get_user_tests(session: AsyncSession, user_id: int) -> Sequence[UserTest]:
    logger.info('Selecting user_tests for user with id = %d', user_id)
    return (
        await session.scalars(
            select(UserTest)
            .where(UserTest.user_id == user_id)
        )
    ).fetchall()


@integration_latency
async def get_unfinished_test(user_id: int, session: AsyncSession) -> UserTest | None:
    logger.info('Selecting unfinished test for user_id = %d', user_id)
    return (
        await session.scalars(
            select(UserTest)
            .where(UserTest.user_id == user_id)
            .where(UserTest.status != StatusEnum.finished)
        )
    ).one_or_none()


@integration_latency
async def post_test(user_id: int, session: AsyncSession) -> UserTest:
    logger.info('Creating new test for user_id = %d', user_id)

    result = (await session.scalar(
            insert(UserTest)
            .values(user_id=user_id, status=StatusEnum.started)
            .returning(UserTest)
    ))
    await session.commit()

    return result


@integration_latency
async def update_test_status(test_id: int, new_status: StatusEnum, session: AsyncSession) -> None:
    logger.info('Updating test status for test with id = %d on status = %s', test_id, new_status)

    await session.execute(
        update(UserTest)
        .where(UserTest.id == test_id)
        .values(status=new_status)
    )
    await session.commit()


@integration_latency
async def update_test(test_id: int, test_data: Dict[str, Any], session: AsyncSession) -> UserTest:
    logger.info('Updating test with id = %d.', test_id)

    result = await session.scalar(
        update(UserTest)
        .where(UserTest.id == test_id)
        .values(**test_data)
        .returning(UserTest)
    )
    await session.commit()

    return result
