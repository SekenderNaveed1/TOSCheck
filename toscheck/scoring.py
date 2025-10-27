from __future__ import annotations
from typing import List, Dict, Tuple
from nltk.tokenize import sent_tokenize
from .patterns import PATTERNS




def split_sentences(text: str) -> List[str]:
    sents = [s.strip() for s in sent_tokenize(text) if s.strip()]
    return sents




def heuristic_hit_categories(sent: str) -> List[str]:
    hits = []
for cat, regs in PATTERNS.items():
    if any(r.search(sent) for r in regs):
        hits.append(cat)
    return hits




def select_candidate_indexes(sents: List[str]) -> List[int]:
    cand = set()
    for i, s in enumerate(sents):
        if heuristic_hit_categories(s):
            cand.update({max(0, i-1), i, min(len(sents)-1, i+1)})
        if not cand:
            cand = set(range(min(12, len(sents))))
    return sorted(cand)




def number_subset(sents: List[str], idxs: List[int]) -> List[str]:
    return [f"{i}: {sents[i]}" for i in idxs]




def merge_llm_flags(sents: List[str], flags: List[Dict]) -> List[Dict]:
# normalize + clip indexes
    out = []
    n = len(sents)
    for f in flags:
        idxs = sorted({i for i in f.get("sentence_indexes", []) if 0 <= i < n})
    if not idxs:
        continue
    out.append({
    "category": f.get("category", ""),
    "sentence_indexes": idxs,
    "rationale": f.get("rationale", ""),
    })
    return out