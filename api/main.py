from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import AIAgent

app = FastAPI(
    title="AI Sourcing Agent API",
    description="AI-powered recruitment agent for automated candidate sourcing and outreach",
    version="1.0.0"
)

class JobRequest(BaseModel):
    job_description: str
    candidate_names: List[str]

class JobResponse(BaseModel):
    status: str
    job_id: str
    candidates_found: int
    execution_time: float
    top_candidates: List[dict]
    message: str = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🚀 AI Sourcing Agent API", 
        "version": "1.0.0",
        "description": "AI-powered recruitment automation",
        "endpoints": {
            "POST /source-candidates": "Source and score candidates",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "synapse-sourcing-agent"}

@app.post("/source-candidates", response_model=JobResponse)
async def source_candidates(request: JobRequest):
    """
    Source, score, and generate outreach messages for candidates
    
    - **job_description**: The job posting text
    - **candidate_names**: List of candidate names to search for
    """
    try:
        # Validate input
        if not request.job_description.strip():
            raise HTTPException(status_code=400, detail="Job description cannot be empty")
        
        if not request.candidate_names or len(request.candidate_names) == 0:
            raise HTTPException(status_code=400, detail="At least one candidate name is required")
        
        # Initialize and run the agent
        agent = AIAgent()
        results = agent.run_full_pipeline(
            request.job_description, 
            request.candidate_names
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Pipeline execution failed: {str(e)}"
        )

@app.get("/sample-request")
async def sample_request():
    """Get a sample request format for testing"""
    return {
        "sample_request": {
            "job_description": "Software Engineer, ML Research at Windsurf. Looking for candidates with experience in LLMs, Python, and production ML systems.",
            "candidate_names": [
                "Andrej Karpathy",
                "Shreya Shankar", 
                "Sebastian Ruder"
            ]
        },
        "usage": "POST this JSON to /source-candidates endpoint"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)