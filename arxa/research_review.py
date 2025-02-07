#!/usr/bin/env python3
"""
Generate a research review summary from PDF text using an LLM.
This version truncates long PDF content and builds a prompt to be sent
to a chosen LLM backend (anthropic, openai, or ollama).
"""
import re
import json
from typing import Dict, Any
import tiktoken  # used for token counting
import requests

from .llm_backends import anthropic_generate, ollama_generate, openai_generate

MAX_PROMPT_TOKENS = 150000

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
    If the provider is "certit.ai:8000", it is mapped to "openai" to use
    the same backend logic.
    """
    prompt_prefix = """
You are a research assistant tasked with generating comprehensive research notes...
<pdf_content>
""".strip()

    prompt_suffix = f"""`
{json.dumps(paper_info, indent=2)}
</paper_info>
...
Begin your response with <research_notes> and end with </research_notes>.

Always extract the authors github url if they are releasing code.

Use the following template:

## 1. Paper Information
- **Title:**
- **Authors:**
- **ArXiv Link:**
- **Date of Submission:**
- **Field of Study:**
- **Keywords:**
- **Code Repository:**

## 2. Summary
- **Problem Statement:**
- **Main Contributions:**
- **Key Findings:**
- **Methodology Overview:**
- **Conclusion:**

## 3. Background & Related Work
- **Prior Work Referenced:**
- **How It Differs from Existing Research:**
- **Gaps It Addresses:**

## 4. Methodology
- **Approach Taken:**
- **Key Techniques Used:**
- **Datasets / Benchmarks Used:**
- **Implementation Details:**
- **Reproducibility:** (Is there a code repository? Are experiments well-documented?)

## 5. Experimental Evaluation
- **Evaluation Metrics:**
- **Results Summary:**
- **Baseline Comparisons:**
- **Ablation Studies:**
- **Limitations Noted by Authors:**

## 6. Strengths
- **Novelty & Innovation:**
- **Technical Soundness:**
- **Clarity & Organization:**
- **Impact & Potential Applications:**

## 7. Weaknesses & Critiques
- **Unaddressed Assumptions / Flaws:**
- **Possible Biases or Limitations:**
- **Reproducibility Concerns:**
- **Presentation Issues:**

## 8. Future Work & Open Questions
- **Suggested Improvements by Authors:**
- **Potential Extensions / Further Research Directions:**
- **Open Problems in the Field:**

## 9. Personal Review & Rating
- **Overall Impression:** (1-5)
- **Significance of Contributions:** (1-5)
- **Clarity & Organization:** (1-5)
- **Methodological Rigor:** (1-5)
- **Reproducibility:** (1-5)

## 10. Additional Notes
- **Key Takeaways:**
- **Interesting Insights:**
- **Personal Thoughts & Comments:**""".strip()

    enc = tiktoken.get_encoding("cl100k_base")
    prefix_tokens = len(enc.encode(prompt_prefix))
    suffix_tokens = len(enc.encode(prompt_suffix))
    available_tokens_for_pdf = MAX_PROMPT_TOKENS - (prefix_tokens + suffix_tokens)

    pdf_text_truncated = pdf_text
    pdf_text_tokens = len(enc.encode(pdf_text))
    if pdf_text_tokens > available_tokens_for_pdf:
        pdf_text_truncated = truncate_text_to_token_limit(pdf_text, available_tokens_for_pdf, "cl100k_base")

    prompt = f"{prompt_prefix}\n{pdf_text_truncated}\n{prompt_suffix}"

    # Normalize provider if it is certit.ai:8000.
    if provider.lower() == "certit.ai:8000":
        provider = "openai"

    if provider == "anthropic":
        if not llm_client:
            raise ValueError("Anthropic client required when provider is 'anthropic'")
        review = anthropic_generate(llm_client, prompt, model=model)
    elif provider == "openai":
        if not llm_client:
            raise ValueError("OpenAI client required when provider is 'openai'")
        review = openai_generate(llm_client, prompt, model=model)
    else:
        review = ollama_generate(prompt, model=model)

    match = re.search(r"<research_notes>(.*?)</research_notes>", review, re.DOTALL)
    if match:
        return match.group(1).strip()
    return review.strip()
