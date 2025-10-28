from __future__ import annotations
import json, re, time
from typing import List, Dict, Optional, Tuple
import ollama
from .utils import MODEL, NUM_CTX, TEMPERATURE, TOP_P
from .patterns import CATEGORIES, PATTERNS

SYSTEM = (
    "You are TOSCheck, a terse compliance spotter. "
    "Use ONLY the provided categories. Be precise; if none apply, return []. "
    "Output MUST be a JSON list (no prose)."
)

FEW_SHOT = """
Sentences:
0: We may change these terms at any time without notice.
1: We may share your information with partners and affiliates.
2: Disputes will be handled by binding arbitration and you waive class actions.

Expected JSON:
[
  {"category": "Unilateral changes", "sentence_indexes": [0], "rationale": "Terms may be changed without notice."},
  {"category": "Data sharing / sale", "sentence_indexes": [1], "rationale": "Sharing with partners/affiliates."},
  {"category": "Arbitration / class-action waiver", "sentence_indexes": [2], "rationale": "Arbitration + class-action waiver."}
]
"""

def _categories_block() -> str:
    return "\n".join([f"- {c}" for c in CATEGORIES])

USER_TEMPLATE = """You are given numbered sentences from a Terms/Privacy document.

Categories (use exact names):
{categories}

{few_shot}

Return ONLY a JSON list like:
[
  {{
    "category": "<one of the above>",
    "sentence_indexes": [<ints>],
    "rationale": "<short reason>"
  }}
]

Sentences:
{sentences}
"""

def _extract_json_list(text: str) -> Optional[str]:
    m = re.search(r"\[[\s\S]*\]", text)
    return m.group(0) if m else None

def _parse_numbered(ns: List[str]) -> List[Tuple[int, str]]:
    out = []
    for line in ns:
        m = re.match(r"\s*(\d+)\s*:\s*(.*)", line)
        if m:
            out.append((int(m.group(1)), m.group(2)))
    return out

def heuristic_flags_all(numbered_sentences: List[str]) -> List[Dict]:
    pairs = _parse_numbered(numbered_sentences)
    by_cat: Dict[str, set] = {cat: set() for cat in CATEGORIES}
    for idx, sent in pairs:
        for cat, regs in PATTERNS.items():
            if any(r.search(sent) for r in regs):
                by_cat.setdefault(cat, set()).add(idx)
    out = []
    for cat, idxs in by_cat.items():
        if idxs:
            out.append({
                "category": cat,
                "sentence_indexes": sorted(idxs),
                "rationale": "Matched policy heuristics."
            })
    return out

def infer_flags(numbered_sentences: List[str], debug: bool = False, llm_only: bool = False) -> List[Dict]:
    prompt = USER_TEMPLATE.format(
        categories=_categories_block(),
        few_shot=FEW_SHOT,
        sentences="\n".join(numbered_sentences),
    )
    llm_flags: List[Dict] = []
    for attempt in range(2):
        res = ollama.chat(
            model=MODEL,
            messages=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],
            options={"num_ctx": NUM_CTX, "temperature": 0.0, "top_p": TOP_P, "format": "json"},
            stream=False,
        )
        txt = res["message"]["content"]
        if debug:
            print("----- DEBUG model raw -----")
            print(txt)
            print("----- /DEBUG -----")
        blob = txt.strip() or _extract_json_list(txt) or ""
        if not blob:
            time.sleep(0.05)
            continue
        try:
            data = json.loads(blob)
            if isinstance(data, list):
                llm_flags = data
                break
        except Exception:
            cleaned = re.sub(r",\s*\]", "]", blob)
            try:
                data = json.loads(cleaned)
                if isinstance(data, list):
                    llm_flags = data
                    break
            except Exception:
                time.sleep(0.05)
                continue

    if llm_only:
        return llm_flags

    heur = heuristic_flags_all(numbered_sentences)
    bucket: Dict[str, set] = {}
    note: Dict[str, str] = {}
    for src in (llm_flags, heur):
        for f in src:
            cat = f.get("category", "")
            idxs = set(f.get("sentence_indexes", []))
            if not cat or not idxs:
                continue
            bucket.setdefault(cat, set()).update(idxs)
            if cat not in note or not note[cat]:
                note[cat] = f.get("rationale", "")
    return [{"category": c, "sentence_indexes": sorted(idxs), "rationale": note.get(c, "")}
            for c, idxs in bucket.items()]

# ---- LLM rationale polisher (keeps categories & indexes) ----
REFINE_SYSTEM = (
    "You are TOSCheck. Improve rationales for flagged clauses concisely. "
    "Do not change categories or indexes. Output JSON list with same objects."
)

REFINE_USER_TMPL = """You will receive the original sentences and a list of flags.
For each flag, keep the same "category" and "sentence_indexes". Only rewrite "rationale" into a short, clear reason (<= 14 words).
Return ONLY a JSON list.

Sentences:
{sentences}

Flags:
{flags}
"""

def llm_refine_rationales(sentences: List[str], flags: List[Dict]) -> List[Dict]:
    if not flags:
        return flags
    numbered = [f"{i}: {sentences[i]}" for i in range(len(sentences))]
    payload = json.dumps(flags, ensure_ascii=False)
    prompt = REFINE_USER_TMPL.format(sentences="\n".join(numbered), flags=payload)
    res = ollama.chat(
        model=MODEL,
        messages=[{"role":"system","content":REFINE_SYSTEM},{"role":"user","content":prompt}],
        options={"num_ctx": NUM_CTX, "temperature": 0.0, "top_p": TOP_P, "format": "json"},
        stream=False,
    )
    txt = res["message"]["content"].strip()
    # try parse robustly
    try:
        data = json.loads(txt)
        if isinstance(data, list):
            # keep evidence if model dropped it
            by_key = {(f["category"], tuple(f["sentence_indexes"])): f for f in flags}
            out = []
            for f in data:
                cat = f.get("category")
                idxs = f.get("sentence_indexes", [])
                rat = f.get("rationale", "")
                base = by_key.get((cat, tuple(idxs)))
                if base:
                    merged = dict(base)
                    merged["rationale"] = rat or base.get("rationale", "")
                    out.append(merged)
                else:
                    out.append(f)
            return out
    except Exception:
        pass
    return flags
