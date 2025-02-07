"""
Test script for exercising the arxa Research Review FastAPI server.
This script sends requests to the health check endpoint and to the review generation endpoint,
including both a valid request and some error cases.

Notes:
  • The valid request now uses provider "ollama", which in this version returns a dummy review.
  • The second test shows that the server properly rejects an unsupported provider,
    returning a 400 error.
  • The third test triggers a Pydantic validation error since the required "model" field is missing.
"""

import requests

# Base URL where the FastAPI server is running.
BASE_URL = "http://127.0.0.1:8000"

def test_health():
    url = f"{BASE_URL}/health"
    try:
        response = requests.get(url)
        print(f"[Health Check] Status Code: {response.status_code}")
        print("Response:", response.json())
    except Exception as e:
        print("[Health Check] Exception occurred:", e)

def test_generate_review_valid():
    """
    Sends a valid POST request to the /generate-review endpoint.
    Uses the "ollama" provider which now should succeed (returning a dummy review).

    If you want to test with an actual backend (e.g., "anthropic" or "openai"),
    change the "provider" field in the payload and ensure that their API keys are set.
    """
    url = f"{BASE_URL}/generate-review"
    payload = {
        "pdf_text": "This is a sample extracted text from a research paper PDF.",
        "paper_info": {"title": "A Sample Research Paper", "authors": ["Alice Doe", "Bob Smith"]},
        "provider": "openai",  # using dummy behavior for testing.
        "model": "o3-mini"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"\n[Generate Review Valid] Status Code: {response.status_code}")
        print("Response:", response.json())
    except Exception as e:
        print("[Generate Review Valid] Exception occurred:", e)

def test_generate_review_invalid_provider():
    """
    Sends a POST request with an unsupported provider.
    The server should reply with a 400 error indicating that the provider is unsupported.
    """
    url = f"{BASE_URL}/generate-review"
    payload = {
        "pdf_text": "This is a sample extracted text from a research paper PDF.",
        "paper_info": {"title": "Test Paper", "authors": ["Alice Doe", "Bob Smith"]},
        "provider": "unknown",  # This is unsupported and should trigger an error.
        "model": "test-model"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"\n[Generate Review Invalid Provider] Status Code: {response.status_code}")
        print("Response:", response.json())
    except Exception as e:
        print("[Generate Review Invalid Provider] Exception occurred:", e)

def test_generate_review_missing_field():
    """
    Sends a request missing a required field (the "model" field).
    The Pydantic validation error should be triggered and reported back.
    """
    url = f"{BASE_URL}/generate-review"
    payload = {
        "pdf_text": "This text is missing the model field.",
        "paper_info": {"title": "Incomplete Request Paper", "authors": ["Alice Doe"]},
        "provider": "ollama"
        # "model" field is missing intentionally.
    }
    try:
        response = requests.post(url, json=payload)
        print(f"\n[Generate Review Missing Field] Status Code: {response.status_code}")
        print("Response:", response.json())
    except Exception as e:
        print("[Generate Review Missing Field] Exception occurred:", e)

def main():
    print("Starting tests for the arxa Research Review API...\n")
    test_health()
    test_generate_review_valid()
    test_generate_review_invalid_provider()
    test_generate_review_missing_field()

if __name__ == "__main__":
    main()
