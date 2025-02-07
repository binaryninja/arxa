#!/usr/bin/env python3
"""
A FastAPI server for generating research reviews.
This server accepts a POST request to generate a research review using an LLM backend.
All requests are forced to use OpenAI with the o3-mini model.
"""
import os
import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .research_review import generate_research_review

logger = logging.getLogger("arxa_server")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(
    title="arxa Research Review API",
    description="Generate research review summaries from PDF text",
    version="0.1"
)

class ReviewRequest(BaseModel):
    pdf_text: str
    paper_info: Dict[str, Any]
    provider: str = "anthropic"
    model: str

class ReviewResponse(BaseModel):
    review: str

def get_llm_client(provider: str):
    """
    Initializes and returns an LLM client based on the provider.
    For "ollama", returns None since HTTP requests are used.
    """
    if provider.lower() == "anthropic":
        try:
            from anthropic import Anthropic
        except ImportError:
            raise HTTPException(status_code=500, detail="Anthropic client library not installed.")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY environment variable not set.")
        return Anthropic(api_key=api_key)
    elif provider.lower() == "openai":
        try:
            import openai
        except ImportError:
            raise HTTPException(status_code=500, detail="OpenAI client library not installed.")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable not set.")
        openai.api_key = api_key
        return openai
    elif provider.lower() == "ollama":
        return None
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider {provider}.")

@app.post("/generate-review", response_model=ReviewResponse)
async def generate_review_endpoint(request: ReviewRequest):
    """
    Generate a research review summary.
    All requests are forced to use OpenAI with the o3-mini model.
    """
    try:
        logger.info("Received review generation request. Overriding provider/model to openai/o3-mini.")
        # Force remote requests to always use OpenAI with the o3-mini model.
        request.provider = "openai"
        request.model = "o3-mini"

        client = get_llm_client(request.provider)
        review = generate_research_review(
            pdf_text=request.pdf_text,
            paper_info=request.paper_info,
            provider=request.provider,
            model=request.model,
            llm_client=client
        )
        logger.info("Review generated successfully")
        return ReviewResponse(review=review)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Error generating review: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating review: {str(e)}")

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("arxa.server:app", host="0.0.0.0", port=8000, reload=True)
