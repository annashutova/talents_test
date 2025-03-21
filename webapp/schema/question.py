from typing import List

from pydantic import BaseModel

from webapp.schema.answer import AnswerSchema


class ProgressData(BaseModel):
    current: int
    total: int


class QuestionSchema(BaseModel):
    id: int
    trait_id: int
    question_content: str
    answers: List[AnswerSchema]

    class Config:
        from_attributes = True


class TestQuestionResponse(BaseModel):
    question: QuestionSchema
    progress: ProgressData
