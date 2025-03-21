from fastapi import Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from starlette import status

from webapp.api.trait.router import trait_router
from webapp.crud.trait import get_traits
from webapp.db.postgres import get_session
from webapp.logger import logger
from webapp.schema.trait import TraitsResponse


@trait_router.get('', response_model=TraitsResponse)
async def get_all_traits(session: AsyncSession = Depends(get_session)) -> ORJSONResponse:
    logger.info('Request to GET /traits')

    traits = await get_traits(session)
    return ORJSONResponse({'traits': jsonable_encoder(traits)}, status_code=status.HTTP_200_OK)
