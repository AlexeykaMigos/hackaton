from typing import List, Dict, Any
from app.services.search_index import search_index


def search_stes(query: str) -> List[Dict[str, Any]]:
    if not query.strip():
        return []
    return search_index.search(query)
