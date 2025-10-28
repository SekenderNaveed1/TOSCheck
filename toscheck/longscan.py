from __future__ import annotations
from typing import List, Dict
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn, TaskProgressColumn, SpinnerColumn
from .llm import infer_flags, heuristic_flags_all
from .rag import load_seeds, rag_flag

def _merge_flag_lists(flag_lists: List[List[Dict]]) -> List[Dict]:
    merged_idxs: Dict[str, set] = {}
    merged_rat: Dict[str, str] = {}
    merged_ev: Dict[str, list] = {}
    for flags in flag_lists:
        for f in flags:
            cat = f.get("category", "")
            idxs = f.get("sentence_indexes", [])
            if not cat or not idxs:
                continue
            merged_idxs.setdefault(cat, set()).update(idxs)
            r = (f.get("rationale") or "").strip()
            if r and not merged_rat.get(cat):
                merged_rat[cat] = r
            ev = f.get("evidence") or []
            if ev:
                merged_ev.setdefault(cat, []).extend(ev)
    out: List[Dict] = []
    for c, idxs in merged_idxs.items():
        item = {
            "category": c,
            "sentence_indexes": sorted(idxs),
            "rationale": merged_rat.get(c, ""),
        }
        if c in merged_ev:
            item["evidence"] = merged_ev[c]
        out.append(item)
    return out

def _scan_window(sentences: List[str], start: int, end: int, engine: str, seeds: Dict[str, List[str]] | None, threshold: float, debug: bool) -> List[Dict]:
    numbered = [f"{i}: {sentences[i]}" for i in range(start, end)]

    if engine == "heuristics":
        return heuristic_flags_all(numbered)

    if engine == "rag":
        r = rag_flag([sentences[i] for i in range(start, end)], seeds or {}, threshold=threshold)
        # re-index local -> global
        for f in r:
            f["sentence_indexes"] = [start + i for i in f.get("sentence_indexes", [])]
        return r

    if engine == "llm":
        return infer_flags(numbered, debug=debug, llm_only=True)

    # hybrid: rag + heuristics + llm
    r = rag_flag([sentences[i] for i in range(start, end)], seeds or {}, threshold=threshold)
    for f in r:
        f["sentence_indexes"] = [start + i for i in f.get("sentence_indexes", [])]
    h = heuristic_flags_all(numbered)
    l = infer_flags(numbered, debug=debug, llm_only=True)
    return _merge_flag_lists([r, h, l])

def scan_windows(sentences: List[str], engine: str, window: int, overlap: int,
                 seeds_path: str, threshold: float, debug: bool=False,
                 llm_polish: bool=False, show_progress: bool=True) -> List[Dict]:
    """
    Windowed scanner with optional progress bar.
    """
    n = len(sentences)
    if n == 0:
        return []

    # Pre-load seeds if needed
    seeds = None
    if engine in ("rag", "hybrid"):
        try:
            seeds = load_seeds(seeds_path)
        except Exception:
            seeds = {}

    # Compute planned windows for progress
    starts = []
    s = 0
    while s < n:
        starts.append(s)
        e = min(n, s + window)
        if e == n:
            break
        s = max(e - overlap, s + 1)

    all_flags: List[Dict] = []

    if not show_progress:
        # Plain loop without progress bar
        s = 0
        while s < n:
            e = min(n, s + window)
            flags = _scan_window(sentences, s, e, engine, seeds, threshold, debug)
            all_flags.extend(flags)
            if e == n:
                break
            s = max(e - overlap, s + 1)
    else:
        # Rich progress bar
        columns = [
            SpinnerColumn(),
            TextColumn("[bold blue]Scanning[/bold blue]"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("• ETA:"),
            TimeRemainingColumn(),
        ]
        with Progress(*columns) as progress:
            task = progress.add_task("scan", total=len(starts))
            for s in starts:
                e = min(n, s + window)
                flags = _scan_window(sentences, s, e, engine, seeds, threshold, debug)
                all_flags.extend(flags)
                progress.advance(task, 1)

    # Final merge across windows
    merged = _merge_flag_lists([all_flags])

    # Optional: polish rationales with LLM
    if llm_polish and merged:
        try:
            from .llm import llm_refine_rationales
            merged = llm_refine_rationales(sentences, merged)
        except Exception:
            pass

    return merged
