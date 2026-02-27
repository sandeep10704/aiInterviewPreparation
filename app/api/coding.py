from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


class CodingQuestion(BaseModel):
    coding_question_id: str
    title: str
    description: str


class CodingQuestionSetResponse(BaseModel):
    coding_set_id: str
    questions: List[CodingQuestion]


class CodingAnswerRequest(BaseModel):
    coding_set_id: str
    answers: dict  # {coding_question_id: code}


# -------------------------
# Normal Coding Questions
# -------------------------

@router.get("/normal", response_model=CodingQuestionSetResponse)
def get_normal_coding_questions():
    return {
        "coding_set_id": "normal_001",
        "questions": [
            {
                "coding_question_id": "nc1",
                "title": "Two Sum",
                "description": "Find two numbers that add to target."
            }
        ]
    }


@router.post("/normal/answers")
def submit_normal_coding_answers(payload: CodingAnswerRequest):
    return {"message": "Normal coding answers submitted"}


# -------------------------
# Resume-Based Coding
# -------------------------

@router.get("/resume/{resume_id}", response_model=CodingQuestionSetResponse)
def get_resume_based_coding_questions(resume_id: str):
    return {
        "coding_set_id": "resume_001",
        "questions": [
            {
                "coding_question_id": "rc1",
                "title": "React State Optimization",
                "description": "Optimize a large component rendering."
            }
        ]
    }


@router.post("/resume/answers")
def submit_resume_coding_answers(payload: CodingAnswerRequest):
    return {"message": "Resume coding answers submitted"}


# -------------------------
# Job Role-Based Coding
# -------------------------

@router.get("/job/{role}", response_model=CodingQuestionSetResponse)
def get_job_role_coding_questions(role: str):
    return {
        "coding_set_id": "job_001",
        "questions": [
            {
                "coding_question_id": "jc1",
                "title": "Backend Rate Limiter",
                "description": "Design a rate limiter system."
            }
        ]
    }


@router.post("/job/answers")
def submit_job_role_coding_answers(payload: CodingAnswerRequest):
    return {"message": "Job role coding answers submitted"}