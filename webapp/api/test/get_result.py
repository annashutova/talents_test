from typing import List, Annotated

from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from starlette import status

from webapp.api.test.router import test_router
from webapp.crud.user_test import get_user_test_by_id
from webapp.crud.user_result import get_trait_degree_interpretation
from webapp.models.talents.user_test import StatusEnum
from webapp.models.talents.interpretation import TraitDegreeEnum
from webapp.db.postgres import get_session
from webapp.logger import logger
from webapp.schema.user_result import ResultInterpretationResponse


@test_router.get('/{test_id}/result', response_model=ResultInterpretationResponse)
async def get_test_result(
        test_id: int,
        session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    logger.info('Request to GET /tests/%d/result', test_id)

    test = await get_user_test_by_id(test_id, session)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Test with id={test_id} not found'
        )

    if test.status != StatusEnum.finished:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Test with id={test_id} is not finished yet.'
        )

    result_interpretation = {}
    for trait_degree in TraitDegreeEnum:
        traits_interpretation = await get_trait_degree_interpretation(test_id, trait_degree, session)
        for traits_interpretation in traits_interpretation:
            if result_interpretation.get(f'trait_{traits_interpretation[0]}') is None:
                result_interpretation[f'trait_{traits_interpretation[0]}'] = {}
            trait_data = result_interpretation[f'trait_{traits_interpretation[0]}']
            trait_data['trait_id'] = traits_interpretation[0]
            trait_data[trait_degree.value] = {
                'title': traits_interpretation[1],
                'coefficient': traits_interpretation[2],
                'short_description': traits_interpretation[3],
                'long_description': traits_interpretation[4],
            }

    return ORJSONResponse(
        {'traits': jsonable_encoder(list(result_interpretation.values()))},
        status_code=status.HTTP_200_OK,
    )
