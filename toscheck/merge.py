from __future__ import annotations
from typing import List, Dict, DefaultDict
from collections import defaultdict

def _valid_idx(i: int, n: int) -> bool:
    return isinstance(i, int) and 0 <= i < n

def merge_flags(sentences: List[str], flags: List[Dict]) -> List[Dict]:
    """
    Strictly merge by category:
      - Keep only indexes that were explicitly cited for that same category.
      - Drop out-of-range indexes.
      - Deduplicate per category, preserve sorted order.
      - Prefer the first non-empty rationale per category (later runs can polish).
    """
    n = len(sentences)
    idxs_by_cat: DefaultDict[str, list] = defaultdict(list)
    seen_by_cat: DefaultDict[str, set] = defaultdict(set)
    rationale_by_cat: Dict[str, str] = {}

    for f in flags or []:
        cat = (f.get("category") or "").strip()
        if not cat:
            continue
        raw = f.get("sentence_indexes") or []
        clean = [int(i) for i in raw if _valid_idx(int(i), n)]
        if not clean:
            continue

        # add indexes (preserve order, dedupe within category)
        for i in clean:
            if i not in seen_by_cat[cat]:
                idxs_by_cat[cat].append(i)
                seen_by_cat[cat].add(i)

        # pick the first non-empty rationale for this category
        r = (f.get("rationale") or "").strip()
        if r and not rationale_by_cat.get(cat):
            rationale_by_cat[cat] = r

    # Build merged list
    out: List[Dict] = []
    for cat, idxs in idxs_by_cat.items():
        out.append({
            "category": cat,
            "sentence_indexes": sorted(idxs),
            "rationale": rationale_by_cat.get(cat, ""),
        })

    # Stable ordering: by category name
    out.sort(key=lambda x: x["category"].lower())
    return out
