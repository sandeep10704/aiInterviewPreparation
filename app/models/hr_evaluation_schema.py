from pydantic import BaseModel
from typing import List


class HREvaluationItem(BaseModel):
    question_no: int
    score: int
    technical_feedback: str
    motivation: str


class HREvaluationSet(BaseModel):
    evaluations: List[HREvaluationItem]
    overall_score: int
    overall_feedback: str