from datetime import datetime

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from webapp.models.talents.user import GenderEnum


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserLoginResponse(BaseModel):
    access_token: str


class UserRegisterRequest(BaseModel):
    first_name: str
    last_name: str
    surname: str
    email: str
    date_of_birth: datetime
    gender: GenderEnum
    password: str
    retry_password: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.retry_password:
            raise ValueError('Passwords do not match')
        return self
