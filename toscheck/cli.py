from __future__ import annotations
import argparse, json
from typing import List, Dict

from .extract import read_text
from .scoring import split_sentences
from .rag import rag_select
from .llm import infer_flags, llm_refine_rationales
from .report import render_flags, save_report
from .validate import validate_flags


# ---------------------------------------------------------------------
# Merge helper: prefer better sources for rationales
# Order: llm_polish > llm > heuristic > any non-empty > fallback
# ---------------------------------------------------------------------
def _merge_flags(flags_list: List[Dict]) -> List[Dict]:
    buckets: Dict[str, Dict] = {}

    def score(flag: Dict) -> int:
        src = flag.get("_src", "")
        if src == "llm_polish": return 3
        if src == "llm":        return 2
        if src == "heuristic":  return 1
        return 0

    for f in flags_list or []:
        cat = (f.get("category") or "").strip()
        idxs = f.get("sentence_indexes") or []
        if not cat or not idxs:
            continue

        b = buckets.setdefault(cat, {
            "category": cat,
            "sentence_indexes": set(),
            "rationale": "",
            "_score": -1,
        })
        b["sentence_indexes"].update(int(i) for i in idxs)

        rat = (f.get("rationale") or "").strip()
        sc = score(f)
        if rat:
            if sc > b["_score"]:
                b["_score"] = sc
                b["rationale"] = rat
            elif sc == b["_score"] and not b["rationale"]:
                b["rationale"] = rat

    out = []
    for cat, b in buckets.items():
        rationale = b["rationale"].strip() or "Matched policy heuristics."
        out.append({
            "category": cat,
            "sentence_indexes": sorted(b["sentence_indexes"]),
            "rationale": rationale,
        })

    out.sort(key=lambda x: (x["category"], x["sentence_indexes"][0] if x["sentence_indexes"] else 10**9))
    return out


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------
def run_main():
    parser = argparse.ArgumentParser(description="TOSCheck: flag risky Terms/Privacy clauses.")
    parser.add_argument("input", help="Path to text/TOS/Privacy file")
    parser.add_argument("--threshold", type=float, default=0.75, help="Similarity threshold for RAG seed matches")
    parser.add_argument("--max-suspects", type=int, default=120, help="Max candidate sentences to send to LLM")
    parser.add_argument("--llm-polish", action="store_true", help="Polish rationales using the LLM")
    parser.add_argument("--no-progress", action="store_true", help="(kept for compat; no visual bar here)")
    parser.add_argument("--report", help="Write markdown report to this path")
    parser.add_argument("--json", help="Write JSON flags to this path")
    args = parser.parse_args()

    # ---------- Parse ----------
    text = read_text(args.input)
    sents = split_sentences(text)
    numbered_global = [f"{i}: {s}" for i, s in enumerate(sents)]
    print(f"\n╭──────────────────────────────────────╮")
    print(f"│ Sentences: {len(sents):<5} │")
    print(f"╰──────────────────────────────────────╯")

    # ---------- RAG preselect ----------
    rag_hits = rag_select(
        sents,
        threshold=args.threshold,
        max_suspects=args.max_suspects
    )
    for _f in rag_hits:
        _f.setdefault("_src", "heuristic")

    # Use RAG-selected indexes if any, otherwise all sentences
    cand = sorted({i for f in rag_hits for i in f.get("sentence_indexes", [])})
    if not cand:
        cand = list(range(len(sents)))

    # Create numbered view with GLOBAL indexes (so the model returns global ids)
    numbered_for_llm = [f"{i}: {sents[i]}" for i in cand]

    # ---------- LLM classification ----------
    llm_out = infer_flags(numbered_for_llm, llm_only=True) or []
    for _f in llm_out:
        _f.setdefault("_src", "llm")

    # ---------- Combine + validate ----------
    combined = validate_flags(sents, rag_hits + llm_out)
    flags = _merge_flags(combined)

    # ---------- Optional LLM rationale polish ----------
    if args.llm_polish and flags:
        try:
            flags = llm_refine_rationales(sents, flags)
            for _f in flags:
                _f["_src"] = "llm_polish"
        except Exception as e:
            print(f"[warn] llm_polish failed: {e}")

    # ---------- Outputs ----------
    if args.report:
        md = render_flags(flags, sents)
        save_report(md, args.report)
        print(f"📄 Saved markdown report → {args.report}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as jf:
            json.dump(flags, jf, ensure_ascii=False, indent=2)
        print(f"📊 Saved JSON output → {args.json}")

    print(f"✅ Done! {len(flags)} categories flagged.\n")


if __name__ == "__main__":
    run_main()
