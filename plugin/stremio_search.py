import os
import json
import time
import threading
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Union, Optional

from plugin.index import (
    get_cached_library,
    load_cache,
    save_cache,
    filter_library_items,
    normalize_item,
    CACHE_FILE,
)
from plugin.search import search_items
from plugin.api import fetch_library, search_cinemeta
from plugin.auth import get_auth_key, StremioAuthError
from plugin.deeplink import build_deeplink, build_web_link
from plugin.poster import heal_poster_url

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
ICON_APP = "assets/icon.png"
ICON_MOVIE = "assets/movie.png"
ICON_SERIES = "assets/series.png"
PLUGIN_GITHUB_URL = "https://github.com/NubPlayz/Stremio.Search.Wox.Plugin"
LAST_SYNC_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".last_sync")
AUTO_SYNC_INTERVAL_SECONDS = 300

_sync_lock = threading.Lock()
_sync_thread: Optional[threading.Thread] = None


@dataclass
class StremioMediaItem:
    """Represents a media item (movie/series) found in library or catalog."""
    id: str
    name: str
    title: str
    sub_title: str
    media_type: str
    poster_url: str
    icon_fallback: str
    deeplink: str
    weblink: str
    score: float = 0.0


@dataclass
class StremioInfoItem:
    """Represents an informational or prompt item in search results."""
    id: str
    title: str
    sub_title: str
    icon: str = ICON_APP
    kind: str = "info" 
    target_query: str = ""


StremioSearchResult = Union[StremioMediaItem, StremioInfoItem]


def parse_query(raw_query: str) -> Tuple[str, bool]:
    trimmed = raw_query.strip()
    if trimmed.endswith("?"):
        without_suffix = raw_query[:-1]
        if not without_suffix.endswith(" "):
            return without_suffix.strip(), True
    return trimmed, False


def format_media_item(item: Dict[str, Any], score: float = 0.0) -> StremioMediaItem:
    name = item.get("name", "Unknown")
    year = item.get("year", "")
    media_type = item.get("type", "other")
    source = item.get("source", "library")
    poster_url = item.get("poster", "")
    item_id = str(item.get("id", ""))

    subparts = []
    if year:
        subparts.append(str(year))
    if media_type:
        subparts.append(media_type.capitalize())
    if source == "library":
        subparts.append("In Library")
    else:
        subparts.append("Stremio Catalog")
    subtitle = " | ".join(subparts)

    deeplink = build_deeplink(item)
    weblink = build_web_link(item)
    healed_url = heal_poster_url(poster_url, item_id=item_id)

    if media_type == "movie":
        icon_fallback = ICON_MOVIE
    elif media_type == "series":
        icon_fallback = ICON_SERIES
    else:
        icon_fallback = ICON_APP

    emoji = "🎬" if media_type.lower() == "movie" else "📺"

    return StremioMediaItem(
        id=item_id,
        name=name,
        title=f"{emoji} {name}",
        sub_title=subtitle,
        media_type=media_type,
        poster_url=healed_url if healed_url.startswith("http") else "",
        icon_fallback=icon_fallback,
        deeplink=deeplink,
        weblink=weblink,
        score=score,
    )


def refresh_library() -> Tuple[bool, str]:
    try:
        key = get_auth_key()
        raw_items = fetch_library(key)
        items = filter_library_items(raw_items)
        save_cache(items)
        try:
            with open(LAST_SYNC_FILE, "w", encoding="utf-8") as f:
                f.write(str(time.time()))
        except Exception:
            pass
        return True, f"Synced {len(items)} library titles."
    except StremioAuthError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Failed refreshing library: {e}"


def should_auto_sync(cache_exists: bool) -> bool:
    if not cache_exists:
        return True
    try:
        if not os.path.exists(LAST_SYNC_FILE):
            return True
        with open(LAST_SYNC_FILE, "r", encoding="utf-8") as f:
            last_ts = float(f.read().strip())
        return (time.time() - last_ts) >= AUTO_SYNC_INTERVAL_SECONDS
    except Exception:
        return True


def trigger_background_sync(cache_exists: bool = True) -> None:
    global _sync_thread
    if not should_auto_sync(cache_exists):
        return
    try:
        with open(LAST_SYNC_FILE, "w", encoding="utf-8") as f:
            f.write(str(time.time()))
    except Exception:
        pass

    with _sync_lock:
        if _sync_thread is not None and _sync_thread.is_alive():
            return
        _sync_thread = threading.Thread(target=refresh_library, daemon=True)
        _sync_thread.start()


def deduplicate_catalog(catalog_items: List[Dict[str, Any]], library_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    lib_ids = set()
    for it in library_items:
        if it.get("id"):
            lib_ids.add(str(it["id"]).lower())
        if it.get("imdb_id"):
            lib_ids.add(str(it["imdb_id"]).lower())

    deduped = []
    for raw in catalog_items:
        norm = normalize_item(raw, source="catalog")
        nid = norm.get("id", "").lower()
        n_imdb = norm.get("imdb_id", "").lower()
        if nid and nid in lib_ids:
            continue
        if n_imdb and n_imdb in lib_ids:
            continue
        deduped.append(norm)
    return deduped


def get_empty_library_suggestion() -> List[StremioSearchResult]:
    return [
        StremioInfoItem(
            id="sync_prompt",
            title="Sync Stremio Library",
            sub_title="Your library is currently empty · Press Enter to sync now",
            icon=ICON_APP,
            kind="sync_prompt",
        )
    ]


def handle_query(raw_query: str, power_user_mode: bool = False) -> List[StremioSearchResult]:
    query, is_explicit_online = parse_query(raw_query)
    cached_library = get_cached_library()

    if power_user_mode:
        if is_explicit_online:
            if not query:
                return [
                    StremioInfoItem(
                        id="hint_online",
                        title="Search Stremio catalogue online",
                        sub_title="Type a title followed by ? (example: sm dune?)",
                        icon=ICON_APP,
                        kind="info",
                    )
                ]
            try:
                catalog_raw = search_cinemeta(query)
                catalog_items = deduplicate_catalog(catalog_raw, cached_library)
                catalog_items = search_items(catalog_items, query, threshold=40.0)
                if not catalog_items:
                    return [
                        StremioInfoItem(
                            id="no_online_matches",
                            title=f'No online matches found for "{query}"',
                            sub_title="Check spelling or try a broader search",
                            icon=ICON_APP,
                            kind="info",
                        )
                    ]
                items_to_show = catalog_items[:30]
                return [format_media_item(item, score=100.0 - i) for i, item in enumerate(items_to_show)]
            except Exception:
                return [
                    StremioInfoItem(
                        id="online_error",
                        title="Unable to search Stremio catalogue",
                        sub_title="Check your internet connection",
                        icon=ICON_APP,
                        kind="info",
                    )
                ]

        if not query:
            trigger_background_sync(cache_exists=bool(cached_library))
            if not cached_library:
                return get_empty_library_suggestion()
            items_to_show = cached_library[:50]
            return [format_media_item(item, score=100.0 - i) for i, item in enumerate(items_to_show)]

        matches = search_items(cached_library, query)
        if not matches:
            return [
                StremioInfoItem(
                    id="query_hint",
                    title="Search Stremio catalogue online",
                    sub_title=f"Type a title followed by ? (example: sm {query}?)",
                    icon=ICON_APP,
                    kind="query_hint",
                    target_query=f"sm {query}?",
                )
            ]
        items_to_show = matches[:30]
        return [format_media_item(item, score=100.0 - i) for i, item in enumerate(items_to_show)]

   
    if not query:
        trigger_background_sync(cache_exists=bool(cached_library))
        if not cached_library:
            return get_empty_library_suggestion()
        items_to_show = cached_library[:50]
        return [format_media_item(item, score=100.0 - i) for i, item in enumerate(items_to_show)]

    lib_matches = search_items(cached_library, query)

    catalog_items = []
    catalog_error = False
    try:
        catalog_raw = search_cinemeta(query)
        catalog_items = deduplicate_catalog(catalog_raw, cached_library)
        catalog_items = search_items(catalog_items, query, threshold=40.0)
    except Exception:
        catalog_error = True

    combined = lib_matches[:20] + catalog_items[:20]
    all_results: List[StremioSearchResult] = [
        format_media_item(item, score=100.0 - i) for i, item in enumerate(combined)
    ]

    if not all_results:
        if catalog_error:
            return [
                StremioInfoItem(
                    id="offline_catalog_error",
                    title=f'No library matches for "{query}"',
                    sub_title="Cannot reach Stremio catalogue — you appear to be offline",
                    icon=ICON_APP,
                    kind="info",
                )
            ]
        return [
            StremioInfoItem(
                id="no_matches",
                title=f'No matches found for "{query}"',
                sub_title="No results in your library or Stremio catalogue",
                icon=ICON_APP,
                kind="info",
            )
        ]

    return all_results

