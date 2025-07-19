import enum
from datetime import datetime
from typing import List

from pydantic import BaseModel

from webapp.models.talents.user_test import StatusEnum


class StartUserTestRequest(BaseModel):
    user_id: int


class UserTestSchema(BaseModel):
    id: int
    user_id: int
    status: StatusEnum
    start_time: datetime
    end_time: datetime | None

    class Config:
        from_attributes = True


class UserTestsResponse(BaseModel):
    tests: List[UserTestSchema]


class ProgressEnum(enum.Enum):
    new = 'new'
    unfinished = 'unfinished'


class StartUserTestResponse(BaseModel):
    test: UserTestSchema
    test_progress: ProgressEnum
