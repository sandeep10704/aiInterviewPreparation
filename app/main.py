from fastapi import FastAPI
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------
# FastAPI Application Initialization
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

# ---------------------------------------------------------
# CORS Middleware (MUST BE BEFORE ROUTERS)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Register Routers
# ---------------------------------------------------------
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
    return {"message": "API is running"}