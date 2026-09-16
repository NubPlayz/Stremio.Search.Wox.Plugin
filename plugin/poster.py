def heal_poster_url(url: str, item_id: str = "") -> str:
    cleaned_url = (url or "").strip()
    cleaned_id = (item_id or "").strip()
    
    imdb_id = cleaned_id if cleaned_id.startswith("tt") else ""
    
    if "undefined" in cleaned_url:
        if imdb_id:
            return f"https://images.metahub.space/poster/medium/{imdb_id}/img"
        return ""

    if not cleaned_url or not cleaned_url.startswith("http"):
        if imdb_id:
            return f"https://images.metahub.space/poster/medium/{imdb_id}/img"
        return ""
        
    return cleaned_url

def get_poster_path(url: str, item_id: str = "") -> str:
    return heal_poster_url(url, item_id=item_id)
