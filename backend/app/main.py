"""FastAPI Application Main Entrypoint for Clinical Lab Analyzer."""

import os
import logging
from contextlib import asynccontextmanager
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import (
    LabAnalysisRequest,
    LabAnalysisResponse,
    HealthResponse
)
from .agent import run_lab_analysis_agent

# Load environment configuration
load_dotenv()

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("clinical_app")

# Determine CORS origins from environment
cors_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
allowed_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    logger.info("Initializing Clinical Lab Analyzer backend...")
    yield
    logger.info("Shutting down Clinical Lab Analyzer backend...")


app = FastAPI(
    title="Clinical Lab Results Analyzer API",
    description="Full-stack GenAI & MCP clinical laboratory results classification, routing, and explanation engine.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["System"])
async def root():
    """Root endpoint returning API service information and status."""
    return {
        "service": "Clinical Lab Results Analyzer API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze_labs": "POST /analyze_labs",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint to verify backend service readiness."""
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    is_llm_ready = bool(gemini_key and gemini_key != "your_gemini_api_key_here")

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        mcp_server="ready",
        llm_configured=is_llm_ready
    )


@app.post(
    "/analyze_labs",
    response_model=LabAnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analysis"]
)
async def analyze_labs(request: LabAnalysisRequest):
    """
    Analyze, classify, prioritize (route), and explain clinical laboratory test results.

    Flow:
    1. Validate input payload (handled by Pydantic LabAnalysisRequest).
    2. Lookup reference ranges & classify results (Normal / Warning / Critical).
    3. Route results (Critical first, Warning second, Normal last).
    4. Generate clinical explanation & actionable next steps via LLM/MCP.
    5. Return complete structured response with severity counts and safety disclaimer.
    """
    if not request.labs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'labs' array cannot be empty. Please provide at least one laboratory test."
        )

    try:
        logger.info(f"Processing analysis request for {len(request.labs)} lab tests.")
        response = await run_lab_analysis_agent(request.labs)
        return response
    except ValueError as ve:
        logger.warning(f"Validation error during lab processing: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected error analyzing lab results: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal error occurred while analyzing the lab results."
        )
