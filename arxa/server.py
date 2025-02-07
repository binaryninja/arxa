import os
import time
import logging
from typing import Any, Dict
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json

from .research_review import generate_research_review
from . import __version__
from .prompts import PROMPT_PREFIX, PROMPT_SUFFIX

logger = logging.getLogger("arxa_server")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
app = FastAPI(
    title="arxa Research Review API",
    description="Generate research review summaries from PDF text",
    version=__version__
)

# -------------------------
# Rate limiting and blacklisting globals.
RATE_LIMIT_WINDOW = 60       # seconds
MAX_REQUESTS_PER_WINDOW = 60  # e.g., 60 requests per minute allowed
MAX_RATE_VIOLATIONS = 3
MAX_ERRORS_PER_WINDOW = 5

ip_metrics = {}
blacklisted_ips = set()

def cleanup_timestamps(timestamps, window):
    cutoff = time.time() - window
    return [ts for ts in timestamps if ts > cutoff]

# -------------------------
# Middleware for logging and rate limiting.
@app.middleware("http")
async def logging_and_rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    logger.info("Incoming request from %s: %s %s", client_ip, request.method, request.url.path)
    if client_ip in blacklisted_ips:
        logger.warning("Blocked request from blacklisted IP: %s", client_ip)
        return JSONResponse(
            status_code=403,
            content={"detail": "Your IP has been blacklisted due to abusive behavior."}
        )
    try:
        body_bytes = await request.body()
        logger.info("Request body from %s: %s", client_ip, body_bytes.decode("utf-8", errors="replace"))
    except Exception as ex:
        logger.error("Failed to read request body from %s: %s", client_ip, str(ex))
        body_bytes = b""

    async def receive():
        return {"type": "http.request", "body": body_bytes}
    request._receive = receive
    metrics = ip_metrics.setdefault(client_ip, {"requests": [], "violations": [], "errors": []})
    metrics["requests"] = cleanup_timestamps(metrics["requests"], RATE_LIMIT_WINDOW)
    metrics["violations"] = cleanup_timestamps(metrics["violations"], RATE_LIMIT_WINDOW)
    metrics["errors"] = cleanup_timestamps(metrics["errors"], RATE_LIMIT_WINDOW)

    if len(metrics["requests"]) >= MAX_REQUESTS_PER_WINDOW:
        metrics["violations"].append(time.time())
        logger.warning("Rate limit hit for IP %s; violation count: %d", client_ip, len(metrics["violations"]))
        if len(metrics["violations"]) >= MAX_RATE_VIOLATIONS:
            blacklisted_ips.add(client_ip)
            logger.error("Blacklisting IP %s due to excessive rate limit violations.", client_ip)
            return JSONResponse(
                status_code=403,
                content={"detail": "Your IP has been blacklisted due to abusive request activity."}
            )
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."}
        )

    metrics["requests"].append(time.time())
    try:
        response = await call_next(request)
    except Exception as e:
        metrics["errors"].append(time.time())
        logger.error("Exception handling request from %s: %s", client_ip, str(e), exc_info=True)
        raise

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    logger.info("Response to %s: status code=%d, body=%s", client_ip, response.status_code, response_body.decode("utf-8", errors="replace"))
    if response.status_code >= 400:
        metrics["errors"].append(time.time())
        if len(metrics["errors"]) >= MAX_ERRORS_PER_WINDOW:
            blacklisted_ips.add(client_ip)
            logger.error("Blacklisting IP %s due to excessive error responses.", client_ip)

    new_response = Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )
    return new_response

# -------------------------
# Pydantic models.
class ReviewRequest(BaseModel):
    pdf_text: str
    paper_info: Dict[str, Any]
    provider: str = "anthropic"
    model: str

class ReviewResponse(BaseModel):
    review: str

def get_llm_client(provider: str):
    provider = provider.lower()
    if provider == "anthropic":
        try:
            from anthropic import Anthropic
        except ImportError:
            raise HTTPException(status_code=500, detail="Anthropic client library not installed.")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY environment variable not set.")
        return Anthropic(api_key=api_key)
    elif provider == "openai":
        try:
            import openai
        except ImportError:
            raise HTTPException(status_code=500, detail="OpenAI client library not installed.")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable not set.")
        openai.api_key = api_key
        return openai
    elif provider == "deepseek":
        try:
            import openai
        except ImportError:
            raise HTTPException(status_code=500, detail="OpenAI client library not installed (required for DeepSeek).")
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="DEEPSEEK_API_KEY environment variable not set.")
        openai.api_key = api_key
        openai.api_base = "https://api.deepseek.com"
        return openai
    elif provider == "fireworks":
        # For Fireworks, no client instance is needed. We simply check that the API key is set.
        if not os.getenv("FIREWORKS_API_KEY"):
            raise HTTPException(status_code=500, detail="FIREWORKS_API_KEY environment variable not set.")
        return None
    elif provider == "ollama":
        return None
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider {provider}.")

# -------------------------
# Startup event: print useful information.
@app.on_event("startup")
async def startup_event():
    logger.info("Starting arxa server, version %s", __version__)
    logger.info("Forcefully using OpenAI with model o3-mini for all requests.")
    template_preview = (PROMPT_PREFIX + "\n" + PROMPT_SUFFIX).split("\n")[:10]
    logger.info("Prompt template (first 10 lines):\n%s", "\n".join(template_preview))
    logger.info("Server health endpoint available at /health")

# -------------------------
# Endpoints.
@app.post("/generate-review", response_model=ReviewResponse)
async def generate_review_endpoint(request: ReviewRequest):
    try:
        logger.info("Received review generation request. Overriding provider/model to openai/o3-mini.")
        # For the server we force using openai/o3-mini
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
        logger.info("Review generated successfully for request.")
        return ReviewResponse(review=review)
    except Exception as e:
        logger.error("Error generating review: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating review: {str(e)}")

@app.get("/health")
async def health_check():
    logger.info("Health check requested.")
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("arxa.server:app", host="0.0.0.0", port=8000, reload=True)
