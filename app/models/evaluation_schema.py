from pydantic import BaseModel
from typing import List


class EvaluatedQuestion(BaseModel):
    question_no: int
    question: str
    correct_answer: str
    user_answer: str
    score: int  # 0-10
    technical_feedback: str
    motivation: str


class EvaluationSet(BaseModel):
    evaluations: List[EvaluatedQuestion]
    overall_score: int
    overall_feedback: str