"""Free, keyless web search (DuckDuckGo) used to ground general-knowledge answers in
real, current sources instead of the local model's memorized (and often stale or wrong)
parametric knowledge.
"""

import logging
from urllib.parse import urlparse

from ddgs import DDGS

logger = logging.getLogger("rag_chatbot")


def search_web(query: str, max_results: int = 5) -> list[dict]:
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
    except Exception:
        logger.exception("Web search failed for query: %s", query)
        return []

    results = []
    for r in raw_results:
        url = r.get("href", "")
        results.append(
            {
                "title": r.get("title") or urlparse(url).netloc or "Web result",
                "url": url,
                "domain": urlparse(url).netloc,
                "snippet": r.get("body", ""),
            }
        )
    return results
