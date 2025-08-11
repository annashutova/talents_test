from typing import Tuple, Sequence

from sqlalchemy import select, insert, func, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import and_

from webapp.logger import logger
from webapp.infrastructure.middleware.metrics import integration_latency
from webapp.models.talents.question import Question
from webapp.models.talents.trait import Trait
from webapp.models.talents.answer import Answer
from webapp.models.talents.user_answer import UserAnswer
from webapp.models.talents.user_result import UserResult
from webapp.models.talents.interpretation import Interpretation, TraitDegreeEnum


@integration_latency
async def get_parameters_sum(
        test_id: int, session: AsyncSession
) -> Sequence[Row[Tuple[float, float, float, int]]]:
    logger.info('Summarizing a, b, c params for test with id = %d', test_id)

    return (await session.execute(
        select(
            func.sum(Answer.a_param),
            func.sum(Answer.b_param),
            func.sum(Answer.c_param),
            Question.trait_id
        )
        .join(Answer.question)
        .join(UserAnswer, UserAnswer.answer_id == Answer.id)
        .where(UserAnswer.test_id == test_id)
        .group_by(Question.trait_id)
    )).fetchall()


@integration_latency
async def post_test_result(test_id: int, session: AsyncSession) -> Sequence[UserResult]:
    logger.info('Recording results for test with id = %d', test_id)

    params_by_trait_ids = await get_parameters_sum(test_id, session)

    user_results_data = []
    for record in params_by_trait_ids:
        user_results_data.append(
            {
                'trait_id': record[3],
                'test_id': test_id,
                'a_param': record[0] / 14,
                'b_param': record[1] / 14,
                'c_param': record[2] / 14,
            }
        )

    result = (await session.scalars(insert(UserResult).returning(UserResult), user_results_data)).fetchall()
    await session.commit()

    return result


@integration_latency
async def get_trait_degree_interpretation(
        test_id: int,
        trait_degree: TraitDegreeEnum,
        session: AsyncSession
) -> Sequence[Row[Tuple[int, str, float, str, str]]]:
    logger.info('Selecting result interpretation for test %d and trait_degree = %s', test_id, trait_degree)

    param = None
    trait_degree_title = None
    match trait_degree:
        case TraitDegreeEnum.trait_lack:
            param = UserResult.a_param
            trait_degree_title = Trait.trait_lack
        case TraitDegreeEnum.trait_virtue:
            param = UserResult.b_param
            trait_degree_title = Trait.trait_virtue
        case TraitDegreeEnum.trait_excess:
            param = UserResult.c_param
            trait_degree_title = Trait.trait_excess

    return (await session.execute(
        select(
            UserResult.trait_id,
            trait_degree_title,
            param,
            Interpretation.short_description,
            Interpretation.long_description,
        )
        .join(Interpretation, Interpretation.trait_id == UserResult.trait_id)
        .join(Trait, Trait.id == UserResult.trait_id)
        .where(UserResult.test_id == test_id)
        .where(Interpretation.trait_degree == trait_degree)
        .where(
            and_(
                param >= Interpretation.lower_bound,
                param < Interpretation.upper_bound,
            )
        )

    )).fetchall()


async def parse_test_result(test_id: int, session: AsyncSession) -> dict:
    result_interpretation = {}
    for trait_degree in TraitDegreeEnum:
        trait_interpretations = await get_trait_degree_interpretation(test_id, trait_degree, session)
        for trait_interpretation in trait_interpretations:
            if result_interpretation.get(f'trait_{trait_interpretation[0]}') is None:
                result_interpretation[f'trait_{trait_interpretation[0]}'] = {}
            trait_data = result_interpretation[f'trait_{trait_interpretation[0]}']
            trait_data['trait_id'] = trait_interpretation[0]
            trait_data[trait_degree.value] = {
                'title': trait_interpretation[1],
                'percent': trait_interpretation[2] * 100 // 1,
                'short_description': trait_interpretation[3],
                'long_description': trait_interpretation[4],
            }

    return {'traits': (list(result_interpretation.values()))}
