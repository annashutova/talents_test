from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from starlette import status

from webapp.api.user.router import user_router
from webapp.auth.jwt import JwtTokenT, jwt_auth
from webapp.crud.user import get_user_by_id
from webapp.crud.user_test import get_user_tests
from webapp.db.postgres import get_session
from webapp.logger import logger
from webapp.schema.user_test import UserTestsResponse


@user_router.get('/{user_id}/tests', response_model=UserTestsResponse)
async def get_all_user_tests(
        user_id: int,
        session: AsyncSession = Depends(get_session),
        access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    logger.info('Request to GET /users/%d/tests', user_id)

    if user_id != access_token['user_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You cannot access tests for user with id = {user_id}'
        )

    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id={access_token["user_id"]} not found'
        )

    tests = await get_user_tests(session, user_id)
    return ORJSONResponse({'tests': jsonable_encoder(tests)}, status_code=status.HTTP_200_OK)
