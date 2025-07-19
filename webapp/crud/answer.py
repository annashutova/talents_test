from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger
from webapp.infrastructure.middleware.metrics import integration_latency
from webapp.models.talents.answer import Answer


@integration_latency
async def get_answer_by_id(answer_id: int, session: AsyncSession) -> Answer:
    logger.info('Selecting answer with id = %d', answer_id)

    return (await session.execute(
        select(Answer)
        .where(Answer.id == answer_id)
    )).scalar_one()
