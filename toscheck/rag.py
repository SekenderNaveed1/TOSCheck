from __future__ import annotations
from typing import List, Dict, Tuple
from .patterns import PATTERNS  # dict: {category: List[compiled_regex]}

def _score_sentence(sent: str) -> List[Tuple[str, int]]:
    """
    Return list of (category, hits) for this sentence based on regex patterns.
    """
    hits: List[Tuple[str, int]] = []
    for cat, regs in PATTERNS.items():
        cnt = sum(1 for r in regs if r.search(sent))
        if cnt > 0:
            hits.append((cat, cnt))
    return hits

def rag_select(
    sentences: List[str],
    threshold: float = 0.75,     # kept for API compatibility (not used by regex preselect)
    max_suspects: int = 120
) -> List[Dict]:
    """
    Heuristic/RAG-like preselection:
      - scores each sentence by how many category regexes hit
      - picks up to max_suspects top sentences
      - groups selected sentences by category

    Returns a list of dicts:
      {"category": <str>, "sentence_indexes": [ints], "rationale": <str>, "_src": "heuristic"}
    """
    # 1) score each sentence
    per_idx_hits: List[Tuple[int, int, List[str]]] = []  # (idx, total_hits, cats)
    for i, s in enumerate(sentences):
        hits = _score_sentence(s)
        if hits:
            total = sum(c for _, c in hits)
            cats = [cat for cat, _ in hits]
            per_idx_hits.append((i, total, cats))

    # 2) choose up to max_suspects by total hit count (desc), stable by index
    per_idx_hits.sort(key=lambda x: (-x[1], x[0]))
    chosen = per_idx_hits[:max_suspects]

    # 3) group by category
    by_cat: Dict[str, List[int]] = {}
    for i, _score, cats in chosen:
        for cat in cats:
            by_cat.setdefault(cat, []).append(i)

    # 4) build output
    out: List[Dict] = []
    for cat, idxs in by_cat.items():
        out.append({
            "category": cat,
            "sentence_indexes": sorted(set(idxs)),
            "rationale": "Preselected by policy pattern match.",
            "_src": "heuristic",
        })
    return out
