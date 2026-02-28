from pydantic import BaseModel


class CodingRunRequest(BaseModel):
    coding_set_id: str
    question_no: int
    code: str
    language: str = "python"