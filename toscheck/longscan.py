from __future__ import annotations
from typing import List, Dict
from .llm import infer_flags, heuristic_flags_all
from .rag import load_seeds, rag_flag
from .scoring import number_subset

def scan_windows(sentences: List[str], engine: str, window: int, overlap: int,
                 seeds_path: str, threshold: float, debug: bool=False) -> List[Dict]:
    """Scan long docs in overlapping windows and merge."""
    n = len(sentences)
    if n == 0:
        return []
    start = 0
    all_flags: List[Dict] = []
    while start < n:
        end = min(n, start + window)
        numbered = [f"{i}: {sentences[i]}" for i in range(start, end)]
        if engine == "heuristics":
            flags = heuristic_flags_all(numbered)
        elif engine == "rag":
            flags = rag_flag([sentences[i] for i in range(start, end)],
                             load_seeds(seeds_path), threshold=threshold)
            # re-index to global sentence indexes:
            for f in flags:
                f["sentence_indexes"] = [start + i for i in f["sentence_indexes"]]
        elif engine == "llm":
            flags = infer_flags(numbered, debug=debug, llm_only=True)
        else:  # hybrid: llm + heuristics (and you can mix in RAG by running twice if you want)
            flags = infer_flags(numbered, debug=debug, llm_only=False)
        all_flags.extend(flags)
        # shift with overlap
        if end == n:
            break
        start = max(end - overlap, start + 1)
    # simple merge: combine by category
    merged = {}
    for f in all_flags:
        cat = f.get("category","")
        idxs = f.get("sentence_indexes", [])
        if not cat or not idxs:
            continue
        merged.setdefault(cat, set()).update(idxs)
    out = [{"category": c, "sentence_indexes": sorted(v), "rationale": ""} for c, v in merged.items()]
    return out
