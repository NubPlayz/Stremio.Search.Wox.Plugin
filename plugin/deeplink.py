import urllib.parse
from typing import Dict, Any

STREMIO_DEEPLINK_PREFIX = "stremio:///detail"
STREMIO_WEB_PREFIX = "https://web.stremio.com/#/detail"

def build_deeplink(item: Dict[str, Any]) -> str:
    media_type = item.get("type", "movie")
    item_id = item.get("id") or item.get("imdb_id") or ""
    encoded_id = urllib.parse.quote(str(item_id))
    return f"{STREMIO_DEEPLINK_PREFIX}/{media_type}/{encoded_id}"

def build_web_link(item: Dict[str, Any]) -> str:
    media_type = item.get("type", "movie")
    item_id = item.get("id") or item.get("imdb_id") or ""
    encoded_id = urllib.parse.quote(str(item_id))
    return f"{STREMIO_WEB_PREFIX}/{media_type}/{encoded_id}"
