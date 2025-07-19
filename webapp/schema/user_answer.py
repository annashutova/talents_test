from datetime import datetime

from pydantic import BaseModel


class UserAnswerRequest(BaseModel):
    test_id: int
    answer_id: int


class UserAnswerSchema(BaseModel):
    id: int
    test_id: int
    answer_id: int
    response_date: datetime

    class Config:
        from_attributes = True
