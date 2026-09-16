import os
import glob
import shutil
import tempfile
import re

class StremioAuthError(Exception):
    pass

def find_storage_path() -> str:
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    app_data = os.environ.get("APPDATA", "")
    roots = [os.path.join(local_app_data, "Programs"), local_app_data, app_data]
    
    for root in roots:
        if not root or not os.path.exists(root):
            continue
        for candidate in glob.glob(os.path.join(root, "*[Ss]tremio*"), recursive=False):
            leveldb_dirs = glob.glob(os.path.join(candidate, "**", "EBWebView", "Default", "Local Storage", "leveldb"), recursive=True)
            for ldb in leveldb_dirs:
                if os.path.isdir(ldb):
                    return ldb
            flat = glob.glob(os.path.join(candidate, "**", "leveldb"), recursive=True)
            for ldb in flat:
                if os.path.isdir(ldb):
                    return ldb
    return ""

def _extract_from_bytes(content: bytes) -> str:
    patterns = [
        rb'"auth"\s*:\s*\{\s*"key"\s*:\s*"([^"]+)"',
        rb'auth["\x00-\x1f:]*key["\x00-\x1f:]*([a-zA-Z0-9_\-\.=/+]{20,})',
        rb'"authKey"\s*:\s*"([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1).decode("utf-8", errors="ignore")
    return ""

def get_auth_key() -> str:
    db_path = find_storage_path()
    if not db_path:
        raise StremioAuthError("Stremio storage directory could not be located.")
    
    temp_dir = tempfile.mkdtemp(prefix="stremio_auth_")
    try:
        for fname in os.listdir(db_path):
            if fname.endswith((".log", ".ldb")):
                try:
                    shutil.copy2(os.path.join(db_path, fname), os.path.join(temp_dir, fname))
                except Exception:
                    continue
        
        extracted_key = ""
        for fname in sorted(os.listdir(temp_dir), reverse=True):
            fpath = os.path.join(temp_dir, fname)
            try:
                with open(fpath, "rb") as f:
                    key = _extract_from_bytes(f.read())
                    if key:
                        extracted_key = key
                        break
            except Exception:
                continue
        
        if not extracted_key:
            raise StremioAuthError("Stremio authentication key was not found in storage.")
        return extracted_key
    except StremioAuthError:
        raise
    except Exception:
        raise StremioAuthError("Failed reading Stremio local storage.")
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
