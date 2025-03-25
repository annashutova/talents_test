from datetime import datetime
from typing import Annotated, List

from fastapi import Depends, HTTPException, Query
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from starlette import status

from webapp.api.test.router import test_router
from webapp.auth.jwt import JwtTokenT, jwt_auth
from webapp.crud.user_result import post_test_result
from webapp.crud.question import count_questions, count_answered_questions
from webapp.crud.user_test import get_user_test_by_id, update_test
from webapp.models.talents.user_test import StatusEnum
from webapp.db.postgres import get_session
from webapp.logger import logger
from webapp.schema.user_test import UserTestSchema


@test_router.put('/{test_id}', response_model=UserTestSchema)
async def finish_test(
        test_id: int,
        trait_ids: Annotated[List[int] | None, Query(alias='trait_id')] = None,
        session: AsyncSession = Depends(get_session),
        access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    logger.info('Request to PUT /tests/%d', test_id)

    if trait_ids is None:
        trait_ids = []

    test = await get_user_test_by_id(test_id, session)
    if test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Test with id={test_id} not found'
        )

    # Validate if test belongs to user that makes the request
    if test.user_id != access_token['user_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You cannot access this test'
        )

    if test.status == StatusEnum.finished:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Test with id={test_id} is already finished.'
        )

    # Check if all questions were answered
    answered_questions = await count_answered_questions(session, test_id)
    total_questions = await count_questions(session, trait_ids)
    if answered_questions != total_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Not all questions were answered for test with id={test_id}.'
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
