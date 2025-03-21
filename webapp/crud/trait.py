from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger
from webapp.middleware.metrics import integration_latency
from webapp.models.talents.trait import Trait


@integration_latency
async def get_traits(session: AsyncSession) -> Sequence[Trait]:
    logger.info('Selecting all traits')
    return (
        await session.scalars(select(Trait))
    ).fetchall()
