from pydantic import BaseModel


class CodingSubmitRequest(BaseModel):
    coding_set_id: str
    question_index: int
    code: str