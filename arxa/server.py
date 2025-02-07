#!/usr/bin/env python3
"""
A FastAPI server for generating research reviews.
This server accepts a POST request to generate a research review using the
existing LLM backends (Anthropic, OpenAI, Ollama) logic from arxa/research_review.py.
"""

import os
import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import the review generation function.
from .research_review import generate_research_review

# Set up logging.
logger = logging.getLogger("arxa_server")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the FastAPI app.
app = FastAPI(title="arxa Research Review API", description="Generate research review summaries from PDF text", version="0.1")

# Request model for generating a review.
class ReviewRequest(BaseModel):
    pdf_text: str
    paper_info: Dict[str, Any]
    # Specify which LLM backend to use. For now use the same available options:
    provider: str = "anthropic"  # one of "anthropic", "openai", or "ollama"
    # The model version/identifier required by the LLM service.
    model: str

# Response model (you could expand this as needed).
class ReviewResponse(BaseModel):
    review: str

def get_llm_client(provider: str):
    """
    Initializes and returns an LLM client based on the provider.
    The clients are instantiated using environment variables.
    """
    if provider.lower() == "anthropic":
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise HTTPException(status_code=500, detail="Anthropic client library not installed.")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY environment variable not set.")
        return Anthropic(api_key=api_key)
    elif provider.lower() == "openai":
        try:
            import openai
        except ImportError as e:
            raise HTTPException(status_code=500, detail="OpenAI client library not installed.")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable not set.")
        openai.api_key = api_key
        return openai
    # For the Ollama provider, we assume no client is needed since we use HTTP requests.
    elif provider.lower() == "ollama":
        return None
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider {provider}.")

@app.post("/generate-review", response_model=ReviewResponse)
async def generate_review_endpoint(request: ReviewRequest):
    """
    Generate a research review summary.
    Expects a JSON payload with the PDF text, paper info, provider, and model.
    """
    try:
        client = get_llm_client(request.provider)
        # Call our review generation function.
        review = generate_research_review(
            pdf_text=request.pdf_text,
            paper_info=request.paper_info,
            provider=request.provider,
            model=request.model,
            llm_client=client
        )
        return ReviewResponse(review=review)
    except Exception as e:
        logger.error("Error generating review: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating review: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}

# To run the server, you could use:
#    uvicorn arxa.server:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("arxa.server:app", host="0.0.0.0", port=8000, reload=True)
