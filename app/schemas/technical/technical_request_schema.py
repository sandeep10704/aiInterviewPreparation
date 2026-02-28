from pydantic import BaseModel
from typing import Dict


class TechnicalAnswerRequest(BaseModel):
    technical_set_id: str
    answers: Dict[str, str]