from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    name: str
    interests: List[str]
    stage: str
    goal: str
    resume_id: str