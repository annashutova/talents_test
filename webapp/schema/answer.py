from pydantic import BaseModel


class AnswerSchema(BaseModel):

    id: int
    question_id: int
    answer_content: str

    class Config:
        from_attributes = True
