import re
import logging
from PyPDF2 import PdfReader
import arxiv

logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from filenames.
    """
    return re.sub(r'[<>:"/\\|?*]', '', filename).strip()

def download_pdf_from_arxiv(paper: arxiv.Result, output_path: str) -> None:
    """
    Download a PDF of an arXiv paper.
    """
    paper.download_pdf(filename=output_path)
    logger.info(f"Downloaded PDF for arXiv ID {paper.entry_id} to {output_path}")

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF using PyPDF2.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"
    return text
