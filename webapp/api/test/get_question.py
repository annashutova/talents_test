from typing import List, Annotated

from fastapi import Depends, HTTPException, Query
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from starlette import status

from webapp.api.test.router import test_router
from webapp.crud.user_test import get_user_test_by_id
from webapp.crud.question import get_all_questions_by_trait_ids, get_unanswered_questions_with_total
from webapp.models.talents.user_test import StatusEnum
from webapp.db.postgres import get_session
from webapp.logger import logger
from webapp.schema.question import TestQuestionResponse, QuestionSchema


@test_router.get('/{test_id}/question', response_model=TestQuestionResponse)
async def get_question(
        test_id: int,
        trait_ids: Annotated[List[int] | None, Query(alias='trait_id')] = None,
        session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    logger.info('Request to GET /tests/%d/question', test_id)
    questions = []
    test_progress = {}
    if trait_ids is None:
        trait_ids = []

    test = await get_user_test_by_id(test_id, session)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Test with id={test_id} not found'
        )

    if test.status == StatusEnum.finished:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Test with id={test_id} is already finished.'
        )

    if test.status == StatusEnum.started:
        questions = await get_all_questions_by_trait_ids(session, trait_ids)
        # TODO: сохранять questions в redis после удаления вопроса
        test_progress = {
            'current': 1,
            'total': len(questions),
        }

    if test.status == StatusEnum.in_progress:
        questions, answered, total = await get_unanswered_questions_with_total(session, trait_ids, test_id)
        test_progress = {
            'current': answered + 1 if answered else answered,
            'total': total,
        }

    if len(questions) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No questions found for this request.'
        )

    return_question = QuestionSchema.model_validate(questions.pop(0))

    return ORJSONResponse(
        {
            'question': jsonable_encoder(return_question),
            'progress': test_progress,
        },
        status_code=status.HTTP_200_OK,
    )
