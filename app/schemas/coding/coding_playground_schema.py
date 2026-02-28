from pydantic import BaseModel


class CodingPlaygroundRequest(BaseModel):
    code: str
    language: str = "python"
    stdin: str = ""