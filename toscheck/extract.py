from __future__ import annotations
from trafilatura import extract as trafi_extract, fetch_url
from pypdf import PdfReader

def read_text(path_or_url: str) -> str:
    p = path_or_url.lower()
    if p.startswith(("http://", "https://")):
        return extract_from_url(path_or_url)
    if p.endswith(".pdf"):
        return extract_from_pdf(path_or_url)
    return extract_from_txt(path_or_url)

def extract_from_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join([(page.extract_text() or "") for page in reader.pages])

def extract_from_url(url: str) -> str:
    downloaded = fetch_url(url)
    if not downloaded:
        return ""
    return trafi_extract(downloaded, include_comments=False, include_tables=False) or ""
