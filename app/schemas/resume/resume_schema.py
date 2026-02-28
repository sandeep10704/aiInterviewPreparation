from pydantic import BaseModel
from typing import List

class Project(BaseModel):
    project_name: str
    project_stack: List[str]
    project_description: str

class WorkExperience(BaseModel):
    company: str
    role: str
    duration: str
    description: str

class ResumeSchema(BaseModel):
    name: str
    phone: str
    email: str
    skills: List[str]
    work_experience: List[WorkExperience]
    certifications: List[str]
    achievements: List[str]
    projects: List[Project]