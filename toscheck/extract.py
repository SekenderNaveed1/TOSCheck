from __future__ import annotations
import os
from typing import Optional
from trafilatura import extract as trafi_extract
from trafilatura import fetch_url
from pypdf import PdfReader




def read_text(path_or_url: str) -> str:
    if path_or_url.lower().startswith(("http://", "https://")):
        return extract_from_url(path_or_url)
    if path_or_url.lower().endswith(".pdf"):
        return extract_from_pdf(path_or_url)
    return extract_from_txt(path_or_url)




def extract_from_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()https://github.com/SekenderNaveed1/TOSCheck




def extract_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)




def extract_from_url(url: str) -> str:
    downloaded = fetch_url(url)
    if not downloaded:
        return ""
    txt = trafi_extract(downloaded, include_comments=False, include_tables=False) or ""
    return txt