from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title="aiInterviewPreparation API", version="1.0.0")

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "API is running"}