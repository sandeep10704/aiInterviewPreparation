from pydantic import BaseModel
from typing import List


class HRQuestionItem(BaseModel):
    question_no: int
    question: str
    answer: str


class HRQuestionSet(BaseModel):
    questions: List[HRQuestionItem]