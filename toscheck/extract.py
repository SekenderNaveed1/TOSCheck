# toscheck/extract.py
from pathlib import Path
import os
import re

def read_text(input_path: str | None, url: str | None) -> str:
    if url:
        # lazy import to avoid lxml build unless needed
        from trafilatura import extract as trafi_extract, fetch_url
        doc = fetch_url(url)
        txt = trafi_extract(doc) or ""
        return _normalize(txt)

    if input_path:
        p = Path(input_path)

        # ---- NEW: directory ingestion ----
        if p.is_dir():
            parts: list[str] = []
            for fp in sorted(p.rglob("*")):
                if not fp.is_file():
                    continue
                suf = fp.suffix.lower()
                if suf in (".txt", ".md", ".rtf", ".html", ".htm", ".pdf"):
                    txt = _read_any_file(fp)
                    if txt.strip():
                        parts.append(f"\n\n### FILE: {fp.name}\n\n{txt}")
            return _normalize("\n\n".join(parts))

        # ---- single file path ----
        return _normalize(_read_any_file(p))

    raise ValueError("Provide --input FILE|DIR or --url URL")


def _read_any_file(p: Path) -> str:
    suf = p.suffix.lower()
    if suf == ".pdf":
        from pdfminer.high_level import extract_text
        return extract_text(str(p)) or ""
    if suf in (".html", ".htm"):
        # very light HTML fallback; you can improve this later if needed
        try:
            from trafilatura import extract as trafi_extract
            return trafi_extract(p.read_text(encoding="utf-8", errors="ignore")) or ""
        except Exception:
            return p.read_text(encoding="utf-8", errors="ignore")
    # default text-like read
    return p.read_text(encoding="utf-8", errors="ignore")


def _normalize(txt: str) -> str:
    # collapse excess whitespace while preserving paragraphs/headings
    txt = re.sub(r"[ \t]+\n", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()
