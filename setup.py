#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="arxa",  # PyPI Package Name
    version="0.1.9",
    author="Jeremy Richards",
    author_email="jeremy@richards.ai",
    description="A research automation tool for fetching, summarizing, and enhancing arXiv papers.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/binaryninja/arxa",
    packages=find_packages(),
    include_package_data=True,
    license_files = "LICENSE",
    install_requires=[
        "PyPDF2",
        "arxiv",
        "anthropic",
        "ollama",
        "openai",
        "requests",
        "tenacity",
        "tqdm",
        "aiohttp",
        "pyyaml",
        "tiktoken",
        "httpx<1,>=0.23.0",
        "rich" #for pretty markdown

    ],
    entry_points={
        "console_scripts": [
            "arxa=arxa.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
