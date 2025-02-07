#!/usr/bin/env python3
import os
import sys
import argparse
import tempfile
import logging
import subprocess

# Import rich’s logging handler for better log formatting.
try:
    from rich.logging import RichHandler
except ImportError:
    RichHandler = None

from .config import load_config
from .arxiv_utils import search_arxiv_by_id_list
from .pdf_utils import download_pdf_from_arxiv, extract_text_from_pdf, sanitize_filename
from .research_review import generate_research_review
from .repo_utils import extract_github_url, clone_repo

def configure_logging(quiet: bool) -> None:
    """
    Configure logging to use rich formatting by default unless quiet is True.
    """
    if not quiet and RichHandler is not None:
        handler = RichHandler(markup=True)
    else:
        handler = logging.StreamHandler()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[handler]
    )

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description="arxa: Generate research reviews from arXiv papers or local PDFs."
    )
    # Add mutually exclusive arguments for arXiv id or local PDF.
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-aid", help="arXiv ID of the paper (e.g. 1234.5678)")
    group.add_argument("-pdf", help="Path to a local PDF file")

    parser.add_argument("-o", "--output", required=True, help="Output markdown file for the review")
    parser.add_argument(
        "-p",
        "--provider",
        default="anthropic",
        choices=["anthropic", "openai", "ollama"],
        help="LLM provider to use (default: anthropic)"
    )
    # Update: -m is now required when -p is provided.
    parser.add_argument(
        "-m",
        "--model",
        required=True,
        help="Model identifier/version (e.g., 'o3-mini') - required when using -p"
    )
    parser.add_argument("-g", "--github", action="store_true", help="Enable GitHub cloning if a GitHub URL is found in the review")
    parser.add_argument("-c", "--config", help="Path to configuration YAML file")
    # New flag to disable rich formatting
    parser.add_argument("--quiet", action="store_true", help="Disable rich output formatting")

    args = parser.parse_args()

    # After args are parsed, configure logging
    configure_logging(args.quiet)

    # (Optional additional safety-check: if -p is specified without -m, exit.)
    if not args.model:
        logger.error("Error: The model identifier (-m) is required when using the provider (-p) argument.")
        sys.exit(1)

    config = {}
    if args.config:
        try:
            config = load_config(args.config)
        except Exception as e:
            logger.error("Error loading config: %s", str(e))
            sys.exit(1)

    papers_dir = config.get("papers_directory", tempfile.gettempdir())
    output_dir = config.get("output_directory", os.getcwd())

    llm_client = None
    if args.provider.lower() == "anthropic":
        from anthropic import Anthropic
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY environment variable not set.")
            sys.exit(1)
        llm_client = Anthropic(api_key=anthropic_api_key)
    elif args.provider.lower() == "openai":
        import openai
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OPENAI_API_KEY environment variable not set.")
            sys.exit(1)
        openai.api_key = openai_api_key
        llm_client = openai

    pdf_path = None
    paper_info = {}

    if args.aid:
        aid = args.aid.strip()
        results = search_arxiv_by_id_list([aid])
        if not results:
            logger.error("Paper with arXiv ID %s not found.", aid)
            sys.exit(1)
        paper = results[0]
        paper_info = {
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "abstract": paper.summary,
            "doi": paper.doi,
            "journal_ref": paper.journal_ref,
            "published": paper.published.isoformat() if paper.published else None,
            "arxiv_link": paper.entry_id,
        }
        pdf_filename = sanitize_filename(f"{aid}.pdf")
        pdf_path = os.path.join(papers_dir, pdf_filename)
        if not os.path.exists(pdf_path):
            logger.info("Downloading PDF for arXiv ID %s ...", aid)
            download_pdf_from_arxiv(paper, pdf_path)
        else:
            logger.info("Using existing PDF file at %s", pdf_path)
    else:
        pdf_path = args.pdf
        paper_info = {
            "title": os.path.basename(pdf_path),
            "authors": [],
            "abstract": "",
            "arxiv_link": "",
        }
        if not os.path.exists(pdf_path):
            logger.error("PDF file %s not found.", pdf_path)
            sys.exit(1)

    try:
        pdf_text = extract_text_from_pdf(pdf_path)
    except Exception as e:
        logger.error("Failed to extract text from PDF: %s", str(e))
        sys.exit(1)

    try:
        review = generate_research_review(
            pdf_text,
            paper_info,
            provider=args.provider,
            model=args.model,
            llm_client=llm_client
        )
    except Exception as e:
        logger.error("Error generating research review: %s", str(e))
        sys.exit(1)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(review)
        logger.info("Review written to %s", args.output)
    except Exception as e:
        logger.error("Failed to write review to file: %s", str(e))
        sys.exit(1)

    if args.github:
        github_url = None
        try:
            from .repo_utils import extract_github_url
            github_url = extract_github_url(review)
        except Exception as e:
            logger.error("Error extracting GitHub URL: %s", str(e))
        if github_url:
            try:
                clone_repo(github_url, output_dir)
                logger.info("Repository cloned from %s", github_url)
            except Exception as e:
                logger.error("Error during GitHub cloning: %s", str(e))
        else:
            logger.info("No GitHub URL found in the review.")

if __name__ == "__main__":
    main()
