from pydantic import BaseModel
from typing import List

class QuestionRequest(BaseModel):
    count: int
    level: List[str]   # ["medium","easy"]