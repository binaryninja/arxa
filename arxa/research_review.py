# arxa/arxa/research_review.py

#!/usr/bin/env python3
"""
Generate a research review summary from PDF text using an LLM.
This version truncates long PDF content and builds a prompt using the template defined
in the prompts module.
"""

import re
import json
import logging  # NEW: import logging for token count reporting
from typing import Dict, Any
import tiktoken  # used for token counting

from .llm_backends import (
    anthropic_generate,
    ollama_generate,
    openai_generate,
    deepseek_generate,
    fireworks_generate,
)
from .prompts import PROMPT_PREFIX, PROMPT_SUFFIX    # <== new import

MAX_PROMPT_TOKENS = 150000

# NEW: Create a logger for this module.
logger = logging.getLogger(__name__)

def truncate_text_to_token_limit(text: str, max_tokens: int, encoding_name: str = "cl100k_base") -> str:
    """
    Truncate text so that its token count does not exceed max_tokens.
    """
    enc = tiktoken.get_encoding(encoding_name)
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated_tokens = tokens[:max_tokens]
    return enc.decode(truncated_tokens)

def generate_research_review(
    pdf_text: str,
    paper_info: Dict[str, Any],
    provider: str = "anthropic",
    model: str = None,
    llm_client = None
) -> str:
    """
    Generate a research review summary based on PDF text and paper info.
    The provider value is used as-is.
    """
    # Calculate token availability.
    enc = tiktoken.get_encoding("cl100k_base")
    prefix_tokens = len(enc.encode(PROMPT_PREFIX))
    suffix_tokens = len(enc.encode(PROMPT_SUFFIX.format(paper_info=json.dumps(paper_info, indent=2))))
    available_tokens_for_pdf = MAX_PROMPT_TOKENS - (prefix_tokens + suffix_tokens)

    # Compute the number of tokens in the full PDF text.
    pdf_text_tokens = len(enc.encode(pdf_text))
    logger.info("PDF text contains %d tokens.", pdf_text_tokens)
    logger.info("Available tokens for PDF text: %d", available_tokens_for_pdf)

    # If the PDF text token count exceeds the available tokens, truncate it.
    pdf_text_truncated = pdf_text
    if pdf_text_tokens > available_tokens_for_pdf:
        pdf_text_truncated = truncate_text_to_token_limit(pdf_text, available_tokens_for_pdf, "cl100k_base")
        truncated_tokens = len(enc.encode(pdf_text_truncated))
        logger.info("PDF text truncated to %d tokens.", truncated_tokens)
    else:
        logger.info("PDF text does not require truncation.")

    # Build the prompt by inserting the JSON of paper_info in the PROMPT_SUFFIX.
    prompt = f"{PROMPT_PREFIX}\n{pdf_text_truncated}\n{PROMPT_SUFFIX.format(paper_info=json.dumps(paper_info, indent=2))}"

    if provider == "anthropic":
        if not llm_client:
            raise ValueError("Anthropic client required when provider is 'anthropic'")
        review = anthropic_generate(llm_client, prompt, model=model)
    elif provider == "openai":
        if not llm_client:
            raise ValueError("OpenAI client required when provider is 'openai'")
        review = openai_generate(llm_client, prompt, model=model)
    elif provider == "deepseek":
        if not llm_client:
            raise ValueError("DeepSeek client required when provider is 'deepseek'")
        review = deepseek_generate(llm_client, prompt, model=model)
    elif provider == "fireworks":
        # Fireworks does not require a client instance.
        review = fireworks_generate(prompt, model=model or "accounts/fireworks/models/deepseek-v3")
    else:
        review = ollama_generate(prompt, model=model)

    match = re.search(r"<research_notes>(.*?)</research_notes>", review, re.DOTALL)
    if match:
        return match.group(1).strip()
    return review.strip()
