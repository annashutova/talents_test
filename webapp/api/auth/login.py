from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.auth.router import auth_router
from webapp.crud.user import get_user_by_creds
from webapp.db.postgres import get_session
from webapp.schema.user import UserLoginRequest, UserLoginResponse
from webapp.auth.jwt import jwt_auth


@auth_router.post(
    '/login',
    response_model=UserLoginResponse,
)
async def login(
    body: UserLoginRequest,
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    user = await get_user_by_creds(session, body)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Wrong email or password.'
        )

    return ORJSONResponse(
        {
            'access_token': jwt_auth.create_token(user.id),
        }
    )
