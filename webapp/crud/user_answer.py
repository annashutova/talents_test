from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger
from webapp.middleware.metrics import integration_latency
from webapp.models.talents.user_answer import UserAnswer
from webapp.models.talents.answer import Answer
from webapp.schema.user_answer import UserAnswerRequest
from webapp.crud.answer import get_answer_by_id


@integration_latency
async def is_question_answered(answer_data: UserAnswerRequest, session: AsyncSession) -> bool:
    answer = await get_answer_by_id(answer_data.answer_id, session)

    logger.info(
        'Checking if question with id = %d is already answered for test = %d',
        answer.question_id,
        answer_data.test_id,
    )
    return (await session.scalar(
        select(func.count())
        .select_from(UserAnswer)
        .join(Answer, Answer.id == UserAnswer.answer_id)
        .where(UserAnswer.test_id == answer_data.test_id)
        .where(Answer.question_id == answer.question_id)
    )) != 0


@integration_latency
async def post_user_answer(user_answer_data: UserAnswerRequest, session: AsyncSession) -> UserAnswer:
    logger.info(
        'Creating new user_answer for test_id = %d, answer_id = %d',
        user_answer_data.test_id,
        user_answer_data.answer_id
    )

    result = (await session.scalar(
            insert(UserAnswer)
            .values(test_id=user_answer_data.test_id, answer_id=user_answer_data.answer_id)
            .returning(UserAnswer)
    ))
    await session.commit()

    return result
