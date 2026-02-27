from fastapi import APIRouter
from app.api import resume, technical, coding, feedback,hr_router

api_router = APIRouter()

api_router.include_router(resume.router, prefix="/resume", tags=["Resume"])
api_router.include_router(technical.router, prefix="/technical", tags=["Technical"])
api_router.include_router(coding.router, prefix="/coding", tags=["Coding"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(hr_router.router, prefix="/hr", tags=["HR"])