# toscheck/chunk.py
import re

def dynamic_chunk(
    text: str,
    max_tokens: int = 200,
    soft_min_tokens: int = 80,
    overlap: int = 40,
) -> list[str]:
    """
    Dynamic, clause-aware chunking:
      - Prefer natural boundaries: blank lines, headings, sentence ends, semicolons
      - Avoid tiny chunks (use soft_min_tokens to merge short paragraphs)
      - Provide token overlap to preserve context
    """
    # First split on blank lines to respect paragraphs/sections
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out = []
    buf = []

    def tokens(s: str) -> int:
        # crude token proxy (word count)
        return len(s.split())

    def flush(force=False):
        nonlocal buf
        if not buf:
            return
        joined = " ".join(buf).strip()
        if joined:
            out.append(joined)
        buf = []

    for p in paras:
        # If paragraph is very long, split by sentences and semicolons
        parts = re.split(r"(?<=[.!?;])\s+(?=[A-Z0-9(])", p)
        cur = []
        cur_tok = 0
        for s in parts:
            s_tok = tokens(s)
            if cur_tok + s_tok > max_tokens and cur_tok >= soft_min_tokens:
                # finalize this piece
                piece = " ".join(cur).strip()
                if piece:
                    out.append(piece)
                # apply overlap from the end
                tail = " ".join(piece.split()[-overlap:])
                cur = [tail, s]
                cur_tok = tokens(tail) + s_tok
            else:
                cur.append(s)
                cur_tok += s_tok
        if cur:
            piece = " ".join(cur).strip()
            # if piece is tiny, try to merge into the buffer
            if tokens(piece) < soft_min_tokens and out:
                prev = out.pop()
                merged = (prev + " " + piece).strip()
                if tokens(merged) <= max_tokens + overlap:
                    out.append(merged)
                else:
                    out.append(prev)
                    out.append(piece)
            else:
                out.append(piece)

    # Merge small trailing piece into previous one if needed
    if len(out) >= 2 and tokens(out[-1]) < soft_min_tokens:
        last = out.pop()
        out[-1] = (out[-1] + " " + last).strip()

    # remove dupes/empties
    return [c for i, c in enumerate(out) if c and (i == 0 or c != out[i-1])]


def chunk_text(text: str, max_tokens: int = 500, overlap: int = 150) -> list[str]:
    """
    Backward compatible wrapper. Calls dynamic_chunk with sensible defaults.
    """
    return dynamic_chunk(text, max_tokens=max_tokens, soft_min_tokens=max_tokens//3, overlap=overlap)
