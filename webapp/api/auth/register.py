from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.auth.router import auth_router
from webapp.crud.user import get_user_by_email, create_user
from webapp.db.postgres import get_session
from webapp.schema.user import UserRegisterRequest, UserSchema
from webapp.auth.password import hash_password


@auth_router.post(
    '/register',
    response_model=UserSchema
)
async def register(
    body: UserRegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    existing_user = await get_user_by_email(session, body.email)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this email already exists.'
        )

    body.password = hash_password(body.password)

    user = await create_user(body, session)

    return ORJSONResponse(
        {'user': jsonable_encoder(UserSchema.model_validate(user))},
        status_code=status.HTTP_201_CREATED,
    )
