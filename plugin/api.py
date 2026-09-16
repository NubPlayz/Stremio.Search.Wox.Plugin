import json
import urllib.request
import urllib.parse
import concurrent.futures
from typing import List, Dict, Any

STREMIO_API_URL = "https://api.strem.io/api/datastoreGet"
CINEMETA_CATALOG_URL = "https://v3-cinemeta.strem.io/catalog"
USER_AGENT = "Stremio/5.0.0"

class StremioApiError(Exception):
    pass

def fetch_library(auth_key: str, timeout: int = 10) -> List[Dict[str, Any]]:
    payload = json.dumps({
        "authKey": auth_key,
        "collection": "libraryItem",
        "all": True
    }).encode("utf-8")
    
    req = urllib.request.Request(
        STREMIO_API_URL,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if not isinstance(data, dict):
                return []
            result = data.get("result", [])
            return result if isinstance(result, list) else []
    except Exception as e:
        raise StremioApiError(f"Network error while fetching library: {e}")

def _fetch_cinemeta_catalog(media_type: str, encoded_query: str, timeout: int) -> List[Dict[str, Any]]:
    """Fetch a single Cinemeta catalog endpoint. Returns metas list or empty on error."""
    url = f"{CINEMETA_CATALOG_URL}/{media_type}/top/search={encoded_query}.json"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            metas = data.get("metas", [])
            if isinstance(metas, list):
                return metas
    except Exception:
        pass
    return []

def search_cinemeta(query: str, timeout: int = 8) -> List[Dict[str, Any]]:
    encoded_query = urllib.parse.quote(query)
    media_types = ("movie", "series")
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(_fetch_cinemeta_catalog, m_type, encoded_query, timeout): m_type
            for m_type in media_types
        }
        type_to_results: Dict[str, List[Dict[str, Any]]] = {}
        for future in concurrent.futures.as_completed(futures):
            m_type = futures[future]
            try:
                type_to_results[m_type] = future.result()
            except Exception:
                type_to_results[m_type] = []

        for m_type in media_types:
            results.extend(type_to_results.get(m_type, []))

    return results

