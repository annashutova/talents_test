from pydantic import BaseModel


class UserInfo(BaseModel):
    username: str


class UserData(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    data: UserData
