from datetime import datetime

from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from starlette import status

from webapp.api.test.router import test_router
from webapp.crud.user_result import post_test_result
from webapp.crud.user_test import get_user_test_by_id, update_test
from webapp.models.talents.user_test import StatusEnum
from webapp.db.postgres import get_session
from webapp.logger import logger
from webapp.schema.user_test import UserTestSchema


@test_router.put('/{test_id}', response_model=UserTestSchema)
async def finish_test(
        test_id: int,
        session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    logger.info('Request to PUT /tests/%d', test_id)

    # TODO: сейчас тест можно завершить преждевременно не ответив на все вопросы!!!

    test = await get_user_test_by_id(test_id, session)
    if test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Test with id={test_id} not found'
        )

    if test.status == StatusEnum.finished:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Test with id={test_id} is already finished.'
        )

    test_data = {
        "status": StatusEnum.finished,
        "end_time": datetime.utcnow()
    }
    await post_test_result(test_id, session)
    updated_test = await update_test(test_id, test_data, session)
    return ORJSONResponse(
        jsonable_encoder(UserTestSchema.model_validate(updated_test)),
        status_code=status.HTTP_200_OK,
    )
