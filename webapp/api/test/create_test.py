from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from starlette import status

from webapp.api.test.router import test_router
from webapp.crud.user_test import get_unfinished_test, post_test
from webapp.crud.user import get_user_by_id
from webapp.db.postgres import get_session
from webapp.logger import logger
from webapp.schema.user_test import StartUserTestRequest, StartUserTestResponse, ProgressEnum, UserTestSchema


@test_router.post('', response_model=StartUserTestResponse)
async def start_test(
        start_test_data: StartUserTestRequest,
        session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    logger.info('Request to POST /tests')

    user = await get_user_by_id(session, start_test_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id={start_test_data.user_id} not found'
        )

    unfinished_test = await get_unfinished_test(start_test_data.user_id, session)
    if unfinished_test:
        return ORJSONResponse(
            {
                'test': jsonable_encoder(UserTestSchema.model_validate(unfinished_test)),
                'test_progress': ProgressEnum.unfinished
            },
            status_code=status.HTTP_201_CREATED,
        )

    created_test = await post_test(start_test_data.user_id, session)
    return ORJSONResponse(
        {
            'test': jsonable_encoder(UserTestSchema.model_validate(created_test)),
            'test_progress': ProgressEnum.new
        },
        status_code=status.HTTP_201_CREATED,
    )
