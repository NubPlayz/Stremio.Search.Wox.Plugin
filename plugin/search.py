import re
from typing import List, Dict, Any, Tuple

def _clean_string(text: str) -> str:
    return re.sub(r"[^\w\s]", " ", (text or "").lower()).strip()

def _fuzzy_score_clean(q: str, t: str) -> float:
    if not q or not t:
        return 0.0
    
    if q == t:
        return 100.0
    if t.startswith(q):
        return 95.0
    if f" {q}" in t:
        return 90.0
    if q in t:
        return 85.0
    
    q_words = q.split()
    t_words = t.split()
    matched_words = 0
    for qw in q_words:
        if any(tw.startswith(qw) for tw in t_words):
            matched_words += 1
        elif any(qw in tw for tw in t_words):
            matched_words += 0.8
            
    word_score = (matched_words / len(q_words)) * 80.0
    
    seq_idx = 0
    matches = 0
    for char in q:
        idx = t.find(char, seq_idx)
        if idx != -1:
            matches += 1
            seq_idx = idx + 1
        else:
            break
            
    seq_score = (matches / len(q)) * 60.0 if matches == len(q) else 0.0
    return max(word_score, seq_score)

def search_items(items: List[Dict[str, Any]], query: str, threshold: float = 55.0) -> List[Dict[str, Any]]:
    clean_q = _clean_string(query)
    if not clean_q:
        return items
    
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for item in items:
        clean_target = item.get("clean_name")
        if not clean_target:
            clean_target = _clean_string(item.get("name", ""))
            
        name_score = _fuzzy_score_clean(clean_q, clean_target)
        year_str = str(item.get("year", "")).lower()
        year_bonus = 5.0 if clean_q in year_str and clean_q else 0.0
        final_score = name_score + year_bonus
        if final_score >= threshold:
            scored.append((final_score, item))
            
    scored.sort(key=lambda x: (-x[0], len(x[1].get("name", ""))))
    return [item for _, item in scored]

