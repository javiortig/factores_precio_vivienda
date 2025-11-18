from pathlib import Path
import requests, time, io

def download_bytes(url: str, timeout=60, retries=3, backoff=2, headers=None) -> bytes:
    headers = headers or {"User-Agent": "tfg-data-fetcher/1.0 (+https://example.invalid)"}
    for i in range(retries):
        try:
            r = requests.get(url, timeout=timeout, headers=headers)
            r.raise_for_status()
            return r.content
        except Exception as e:
            if i + 1 == retries:
                raise
            time.sleep(backoff * (i + 1))
    # If retries is 0 or the loop completes without returning, raise an explicit error.
    raise RuntimeError(f"Failed to download {url} after {retries} attempts")

def read_csv_auto_from_bytes(b: bytes):
    # Try common encodings and separators
    text_guesses = [("utf-8", ","), ("utf-8", ";"), ("latin-1", ";"), ("latin-1", "\t"), ("utf-8", "\t")]
    for enc, sep in text_guesses:
        try:
            s = b.decode(enc)
            df = __import__("pandas").read_csv(io.StringIO(s), sep=sep, dtype=str)
            # if dataframe has multiple columns, assume success
            if df.shape[1] > 1:
                return df
        except Exception:
            continue
    # Last attempt: let pandas infer
    try:
        s = b.decode("utf-8", errors="ignore")
        return __import__("pandas").read_csv(io.StringIO(s), dtype=str)
    except Exception:
        raise
