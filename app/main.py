from fastapi import FastAPI
from app.api.router import api_router

# ---------------------------------------------------------
# FastAPI Application Initialization
# ---------------------------------------------------------
# This application provides APIs for:
# - Resume Analysis
# - Technical Interview Preparation
# - HR Interview Simulation
# - Coding Practice & Evaluation
# - Coding Playground Execution
# ---------------------------------------------------------

app = FastAPI(
    title="AI Interview Preparation API",
    version="1.0.0",
    description="""
AI Interview Preparation Platform API

This backend provides intelligent interview preparation features including:

 Resume parsing and analysis  
 Technical interview question generation  
 HR interview simulation  
 Coding interview practice  
 Code execution playground  
 Automated evaluation & feedback

Authentication:
Most endpoints require Firebase Bearer Token authentication.
""",
)

# Register all application routers
app.include_router(api_router)


# ---------------------------------------------------------
# Root Endpoint (Health Check)
# ---------------------------------------------------------
@app.get(
    "/",
    summary="Health Check",
    description="Checks whether the API server is running successfully.",
    tags=["System"]
)
def root():
    """
    Health check endpoint.

    Returns:
        dict: API running status message.
    """
    return {"message": "API is running"}