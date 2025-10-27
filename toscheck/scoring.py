from __future__ import annotations
from typing import List, Dict
import re
from .patterns import PATTERNS

def _regex_sent_tokenize(text: str) -> List[str]:
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p and p.strip()]

def split_sentences(text: str) -> List[str]:
    try:
        from nltk.tokenize import sent_tokenize
        return [s.strip() for s in sent_tokenize(text) if s.strip()]
    except Exception:
        return _regex_sent_tokenize(text)

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
    out, n = [], len(sents)
    for f in flags:
        idxs = sorted({i for i in f.get("sentence_indexes", []) if 0 <= i < n})
        if idxs:
            out.append({"category": f.get("category",""), "sentence_indexes": idxs, "rationale": f.get("rationale","")})
    return out
