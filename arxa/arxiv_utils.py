#!/usr/bin/env python3
import arxiv
from typing import List
import logging

logger = logging.getLogger(__name__)

def search_arxiv_by_author(author: str, max_results: int = 10) -> List[arxiv.Result]:
    """
    Search arXiv by author name.

    Args:
        author (str): The author name to search for.
        max_results (int): Maximum number of results (default is 10).

    Returns:
        List[arxiv.Result]: The list of matching arXiv papers.
    """
    query = f'au:"{author}"'
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    results = list(search.results())
    logger.debug("Found %d results for author '%s'", len(results), author)
    return results

def search_arxiv_by_keyword(keyword: str, max_results: int = 10) -> List[arxiv.Result]:
    """
    Search arXiv by keyword in the paper title.

    Args:
        keyword (str): The keyword to search for in the title.
        max_results (int): Maximum number of results (default is 10).

    Returns:
        List[arxiv.Result]: The list of matching arXiv papers.
    """
    query = f"ti:{keyword}"
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    results = list(search.results())
    logger.debug("Found %d results for keyword '%s'", len(results), keyword)
    return results

def search_arxiv_by_id_list(id_list: list) -> List[arxiv.Result]:
    """
    Search arXiv by a list of specific IDs.

    Args:
        id_list (list): A list of arXiv IDs (e.g., ['2301.00123v1', '2209.01234v2']).

    Returns:
        List[arxiv.Result]: The list of matching arXiv papers.
    """
    if not id_list:
        return []
    results = []
    # arXiv API typically allows about 100 IDs per query.
    for i in range(0, len(id_list), 100):
        batch = id_list[i : i + 100]
        search = arxiv.Search(id_list=batch)
        batch_results = list(search.results())
        logger.debug("Fetched %d results for batch starting at index %d", len(batch_results), i)
        results.extend(batch_results)
    return results
