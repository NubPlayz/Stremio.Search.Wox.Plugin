import os
import json
import re
import tempfile
from typing import List, Dict, Any, Optional

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "library.json")

_cached_library: Optional[List[Dict[str, Any]]] = None
_cached_mtime: float = 0.0

def clean_title(text: str) -> str:
    return re.sub(r"[^\w\s]", " ", (text or "").lower()).strip()

def normalize_item(raw: Dict[str, Any], source: str = "library") -> Dict[str, Any]:
    item_id = raw.get("_id") or raw.get("id") or ""
    name = raw.get("name") or "Unknown Title"
    media_type = raw.get("type") or "other"
    
    year = raw.get("year")
    if not year and "releaseInfo" in raw:
        year = raw.get("releaseInfo")
    
    poster = raw.get("poster") or ""
    imdb_id = raw.get("imdb_id") or (item_id if str(item_id).startswith("tt") else "")
    
    poster_str = str(poster).strip()
    if "undefined" in poster_str or not poster_str:
        if imdb_id and str(imdb_id).startswith("tt"):
            poster_str = f"https://images.metahub.space/poster/medium/{imdb_id}/img"
            
    name_str = str(name).strip()
    return {
        "id": str(item_id),
        "name": name_str,
        "clean_name": clean_title(name_str),
        "type": str(media_type).lower().strip(),
        "year": str(year).strip() if year else "",
        "poster": poster_str,
        "imdb_id": str(imdb_id).strip(),
        "source": source
    }

def save_cache(items: List[Dict[str, Any]], cache_path: str = CACHE_FILE) -> None:
    global _cached_library, _cached_mtime
    cache_dir = os.path.dirname(cache_path)
    os.makedirs(cache_dir, exist_ok=True)
    
    temp_file = cache_path + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
        
    os.replace(temp_file, cache_path)
    
   
    _cached_library = items
    try:
        _cached_mtime = os.path.getmtime(cache_path)
    except Exception:
        _cached_mtime = 0.0

def load_cache(cache_path: str = CACHE_FILE) -> List[Dict[str, Any]]:
    """Loads cache directly from disk."""
    if not os.path.exists(cache_path):
        return []
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            for item in data:
                if "clean_name" not in item:
                    item["clean_name"] = clean_title(item.get("name", ""))
            return data
    except Exception:
        return []

def get_cached_library(cache_path: str = CACHE_FILE, force_reload: bool = False) -> List[Dict[str, Any]]:
    """
    Returns library items from in-memory cache.
    Only hits disk if not loaded yet or if the file was modified on disk.
    """
    global _cached_library, _cached_mtime

    if not os.path.exists(cache_path):
        _cached_library = []
        _cached_mtime = 0.0
        return []

    try:
        mtime = os.path.getmtime(cache_path)
    except Exception:
        mtime = 0.0

    if _cached_library is not None and not force_reload and mtime == _cached_mtime:
        return _cached_library

    loaded = load_cache(cache_path)
    _cached_library = loaded
    _cached_mtime = mtime
    return _cached_library

def filter_library_items(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    filtered = []
    for item in raw_items:
        if item.get("removed", False):
            continue
        if item.get("temp", False):
            continue
        normalized = normalize_item(item, source="library")
        if normalized["id"] and normalized["name"]:
            filtered.append(normalized)
    return filtered

