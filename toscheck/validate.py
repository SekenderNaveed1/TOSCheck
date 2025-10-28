from __future__ import annotations
import re
from typing import List, Dict

CATEGORY_PATTERNS = {
    "Arbitration / class-action waiver": [
        r"\barbitration\b", r"\bclass[- ]?action\b", r"\bjury trial\b", r"\bdispute(s)?\b",
    ],
    "Unilateral changes": [
        r"\b(change|modify|amend)\b.*\b(any time|without (notice|consent))\b",
        r"\bwe may (update|revise) (these|the) (terms|policy)\b",
    ],
    "Termination for convenience": [
        r"\bterminate\b.*\b(sole discretion|any reason|no reason)\b",
    ],
    "Warranty disclaimer": [
        r"\b(as is|as\-is)\b", r"\bno warranties\b",
    ],
    "Limitation of liability": [
        r"\b(limit|limitation)\b.*\bliabilit(y|ies)\b",
        r"\b(indirect|consequential|incidental) damages\b",
    ],
    "Indemnification": [
        r"\bindemnif(y|ication)\b", r"\bhold (us|harmless)\b",
    ],
    "Automatic renewal / negative option": [
        r"\b(auto(matic)?(ally)?|automatic)\b.*\brenew(al)?\b",
        r"\bnegative option\b", r"\bunless canceled\b",
    ],
    "Price / fee changes": [
        r"\b(prices?|fees?)\b.*\b(change|increase|subject to change)\b",
    ],
    "Refund exclusions": [
        r"\bnon[- ]?refundable\b", r"\bno refunds?\b",
    ],
    "Broad license to user content": [
        r"\b(perpetual|irrevocable|worldwide|royalty[- ]?free)\b",
        r"\blicense to (use|modify|distribute)\b",
    ],
    "Data collection (personal)": [
        r"\bcollect\b.*\b(personal|information|data)\b",
    ],
    "Location / device data": [
        r"\b(location|camera|microphone|device)\b",
    ],
    "Data sharing / sale": [
        r"\bshare\b.*\b(third[- ]?part(y|ies)|partners?|affiliates?)\b",
        r"\bsell\b.*\bdata\b",
    ],
    "Targeted ads / profiling": [
        r"\b(behavioral|targeted)\b.*\b(ad(s)?|advertising)\b", r"\bprofiling\b",
    ],
    "Third-party trackers / cookies": [
        r"\b(cookies?|tracking pixels?)\b", r"\bthird[- ]?party (cookies?|trackers?)\b", r"\bdo not track|DNT\b",
    ],
    "International transfers": [
        r"\btransfer(red)?\b.*\b(internationally|outside (your|the) (country|jurisdiction))\b",
    ],
    "Data retention / deletion": [
        r"\b(retain|retention|delete|deletion)\b", r"\b(as long as necessary)\b",
    ],
    "User rights (GDPR/CCPA/CPRA)": [
        r"\b(access|delete|restrict|opt[- ]?out|correct)\b.*\b(personal|information|data)\b",
        r"\b(GDPR|CCPA|CPRA)\b",
    ],
    "Notice by posting only": [
        r"\b(notice|notify)\b.*\b(post(ing)?|this page)\b",
    ],
    "Opt-out hard to find": [
        r"\b(print|mail|written request)\b",
    ],
    "Governing law / venue": [
        r"\bgoverning law\b", r"\bvenue\b", r"\b(state|province|jurisdiction)\b",
    ],
    "Children's data (COPPA / minors)": [
        r"\b(children|minors?|under (13|16))\b", r"\bparental consent\b",
    ],
}

def _matches_any(patterns, text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t, flags=re.I) for p in patterns)

def validate_flags(sentences: List[str], flags: List[Dict]) -> List[Dict]:
    out: List[Dict] = []
    for f in flags or []:
        cat = (f.get("category") or "").strip()
        idxs = f.get("sentence_indexes") or []
        if not cat or not idxs:
            continue
        pats = CATEGORY_PATTERNS.get(cat)
        if not pats:
            out.append(f)
            continue
        keep = []
        for i in idxs:
            if 0 <= int(i) < len(sentences):
                if _matches_any(pats, sentences[int(i)]):
                    keep.append(int(i))
        if keep:
            g = dict(f)
            g["sentence_indexes"] = sorted(dict.fromkeys(keep))
            out.append(g)
    return out
