from datetime import datetime

from pydantic import BaseModel


class AnswerSchema(BaseModel):

    id: int
    question_id: int
    answer_content: str

    class Config:
        from_attributes = True


class Responses(BaseModel):
    email: str
    first_name: str
    last_name: str
    surname: str | None
    gender: str
    date_of_birth: datetime
    answers: list[dict[str, int]]
