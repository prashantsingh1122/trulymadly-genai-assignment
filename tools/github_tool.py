import os
import time
import requests
from typing import List, Dict, Any


def search_repositories(query: str, limit: int = 3, retries: int = 3, backoff: float = 1.0) -> List[Dict[str, Any]]:
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit
    }

    headers = {}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()

            results = []
            for item in data.get("items", []):
                results.append({
                    "name": item.get("full_name"),
                    "stars": item.get("stargazers_count"),
                    "url": item.get("html_url")
                })

            return results
        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(backoff * attempt)
                continue
            else:
                raise

    # fallback
    raise last_exc
