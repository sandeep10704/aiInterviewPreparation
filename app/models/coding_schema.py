from pydantic import BaseModel
from typing import List


class TestCase(BaseModel):
    input: str
    output: str


class CodingQuestion(BaseModel):
    difficulty: str
    title: str
    function_signature: str
    problem_statement: str
    input_format: str
    output_format: str
    constraints: str
    test_cases: List[TestCase]


class CodingQuestionSet(BaseModel):
    questions: List[CodingQuestion]