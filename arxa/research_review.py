import re
import json
from typing import Dict, Any
import tiktoken  # used for token counting

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
    Generate a research review summary from the PDF text using an LLM.
    """
    prompt_prefix = """
You are a research assistant tasked with generating comprehensive research notes...
<pdf_content>
""".strip()

    prompt_suffix = f"""`
{json.dumps(paper_info, indent=2)}
</paper_info>
Begin your response with <research_notes> and end with </research_notes>.
[Use the template provided to organize your review.]
""".strip()

    enc = tiktoken.get_encoding("cl100k_base")
    prefix_tokens = len(enc.encode(prompt_prefix))
    suffix_tokens = len(enc.encode(prompt_suffix))
    available_tokens_for_pdf = MAX_PROMPT_TOKENS - (prefix_tokens + suffix_tokens)

    pdf_text_truncated = pdf_text
    pdf_text_tokens = len(enc.encode(pdf_text))
    if pdf_text_tokens > available_tokens_for_pdf:
        pdf_text_truncated = truncate_text_to_token_limit(pdf_text, available_tokens_for_pdf, "cl100k_base")

    prompt = f"{prompt_prefix}\n{pdf_text_truncated}\n{prompt_suffix}"

    if provider == "anthropic":
        if not llm_client:
            raise ValueError("Anthropic client required when provider is 'anthropic'")
        response = anthropic_generate(llm_client, prompt, model=model)
    elif provider == "openai":
        if not llm_client:
            raise ValueError("OpenAI client required when provider is 'openai'")
        response = openai_generate(llm_client, prompt, model=model)
    else:
        response = ollama_generate(prompt, model=model)

    match = re.search(r"<research_notes>(.*?)</research_notes>", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return "Error: Research notes not found in the response."
