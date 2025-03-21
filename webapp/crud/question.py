from typing import List, Tuple

from sqlalchemy import select, func, Subquery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from webapp.logger import logger
from webapp.middleware.metrics import integration_latency
from webapp.models.talents.question import Question
from webapp.models.talents.answer import Answer
from webapp.models.talents.user_answer import UserAnswer


@integration_latency
async def get_all_questions_by_trait_ids(
        session: AsyncSession,
        trait_ids: List[int | None]
) -> List[Question | None]:
    logger.info('Selecting all questions by trait_ids.')

    query = (
            select(Question)
            .options(selectinload(Question.answers))
    )
    if len(trait_ids) != 0:
        query = query.where(Question.trait_id.in_(trait_ids))

    return list((
        await session.scalars(query)).fetchall())


@integration_latency
async def count_questions(
        session: AsyncSession,
        trait_ids: List[int | None]
) -> int | None:
    logger.info('Counting all questions by trait_ids.')

    query = (select(func.count()).select_from(Question))
    if len(trait_ids) != 0:
        query = query.where(Question.trait_id.in_(trait_ids))

    return await session.scalar(query)


@integration_latency
async def count_answered_questions(
        session: AsyncSession,
        answered_query: Subquery,
) -> int | None:
    logger.info('Counting answered questions by trait_ids.')

    return (
        await session.scalar(
            select(func.count())
            .select_from(answered_query)
        )
    )


@integration_latency
async def get_unanswered_questions_with_total(
        session: AsyncSession,
        trait_ids: List[int | None],
        test_id: int
) -> Tuple[List[Question | None], int | None, int | None]:
    logger.info('Selecting unanswered questions by trait_ids.')

    # Subquery to get all question IDs that have been answered in this test
    answered_query = (
        select(Answer.question_id)
        .join(UserAnswer, UserAnswer.answer_id == Answer.id)
        .where(UserAnswer.test_id == test_id)
        .distinct()
    )

    async with session.begin_nested():
        # Count answered questions
        answered_subquery = answered_query.subquery()
        answered = await count_answered_questions(session, answered_subquery)
        # Count total number of questions
        total = await count_questions(session, trait_ids)

        # Main query to get questions that are NOT in the subquery
        unanswered_query = (
            select(Question)
            .options(
                selectinload(Question.answers)
                .load_only(Answer.id, Answer.question_id, Answer.answer_content)
            )
            .where(~Question.id.in_(answered_query))
        )
        if trait_ids:
            unanswered_query = unanswered_query.where(Question.trait_id.in_(trait_ids))

        unanswered_questions = list((await session.scalars(unanswered_query)).fetchall())

    return unanswered_questions, answered, total
