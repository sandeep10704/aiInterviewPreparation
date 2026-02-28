from pydantic import BaseModel
from typing import List


class QuestionItem(BaseModel):
    question_no: int
    question: str
    answer: str


class QuestionSet(BaseModel):
    questions: List[QuestionItem]