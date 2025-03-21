from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from starlette import status

from webapp.api.test.router import test_router
from webapp.crud.user_answer import is_question_answered, post_user_answer
from webapp.crud.user_test import update_test_status, get_user_test_by_id
from webapp.db.postgres import get_session
from webapp.logger import logger
from webapp.schema.user_answer import UserAnswerRequest, UserAnswerSchema
from webapp.models.talents.user_test import StatusEnum


@test_router.post('/answer', response_model=UserAnswerSchema)
async def answer_question(
        answer_data: UserAnswerRequest,
        session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    logger.info('Request to POST /tests/answer')

    test = await get_user_test_by_id(answer_data.test_id, session)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Test with id={answer_data.test_id} not found'
        )

    if test.status == StatusEnum.finished:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Test with id={answer_data.test_id} is already finished.'
        )

    if await is_question_answered(answer_data, session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Question is already answered.')

    user_answer = await post_user_answer(answer_data, session)
    await update_test_status(answer_data.test_id, StatusEnum.in_progress, session)
    return ORJSONResponse(
        jsonable_encoder(UserAnswerSchema.model_validate(user_answer)),
        status_code=status.HTTP_201_CREATED
    )
