from __future__ import annotations
import os, time, argparse
from typing import List, Dict
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeElapsedColumn, MofNCompleteColumn
from nltk import download as nltk_download

from .utils import MODEL
from .extract import read_text
from .scoring import split_sentences
from .merge import merge_flags as _merge_flags
from .report import render_flags, save_report

console = Console()

# --- helpers ---------------------------------------------------------
def _ensure_nltk():
    try:
        import nltk  # noqa
        nltk.data.find("tokenizers/punkt")
        nltk.data.find("tokenizers/punkt_tab")
    except Exception:
        console.print("[yellow]NLTK data missing, downloading...[/yellow]")
        try: nltk_download("punkt")
        except Exception: pass
        try: nltk_download("punkt_tab")
        except Exception: pass
        console.print("[green]NLTK ready[/green]")

def _try_import_rag():
    try:
        from .rag import load_seeds, rag_flag
        return load_seeds, rag_flag
    except Exception:
        return None, None

def _try_import_llm():
    try:
        from .llm import infer_flags, llm_refine_rationales
        return infer_flags, llm_refine_rationales
    except Exception:
        return None, None

def _make_progress():
    return Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    )

def _header(model: str, n: int):
    console.print("╭──────────────────────────────────────╮")
    console.print(f"│ Model: {model}  |  Sentences: {n:<5} │")
    console.print("╰──────────────────────────────────────╯")

# --- index remap helper (robust to local/global/1-based) -------------
def _remap_indexes(maybe_idxs, cand):
    """Map indexes coming from the LLM to global sentence ids.
       Accepts: local 0-based, local 1-based, or global indexes.
       Returns only valid global indexes that exist in cand (preserves order, deduped)."""
    if not maybe_idxs:
        return list(cand)
    # normalize to ints
    ints = []
    for x in maybe_idxs:
        try:
            ints.append(int(x))
        except Exception:
            continue
    if not ints:
        return list(cand)
    # A) local 0-based
    if all(0 <= i < len(cand) for i in ints):
        return [cand[i] for i in ints]
    # B) local 1-based
    if all(1 <= i <= len(cand) for i in ints):
        return [cand[i-1] for i in ints]
    # C) treat as global; keep only those that are in cand
    cand_set = set(cand)
    out, seen = [], set()
    for i in ints:
        if i in cand_set and i not in seen:
            out.append(i); seen.add(i)
    return out if out else list(cand)

# --- RAG->LLM pipeline ----------------------------------------------
def run_main():
    _ensure_nltk()

    p = argparse.ArgumentParser(description="TOSCheck – RAG+LLM flagger (only).")
    p.add_argument("input", help="Path or URL of the Terms to scan.")
    p.add_argument("--report", help="Markdown report out path.")
    p.add_argument("--json", help="Save JSON output here.")
    p.add_argument("--seeds", default="seeds.yml", help="Path to seeds.yml for RAG exemplars.")
    p.add_argument("--threshold", type=float, default=0.75, help="RAG similarity threshold (0–1).")
    p.add_argument("--max-suspects", type=int, default=400, help="Max candidate sentences to send to LLM.")
    p.add_argument("--llm-polish", action="store_true", help="LLM rewrite/expand rationales.")
    p.add_argument("--progress", dest="progress", action="store_true")
    p.add_argument("--no-progress", dest="progress", action="store_false")
    p.add_argument("--gpu-check", action="store_true", help="Print whether Ollama is using GPU.")
    p.add_argument("--debug", action="store_true")
    p.set_defaults(progress=True)
    args = p.parse_args()

    if args.gpu_check:
        console.print("[bold]GPU check:[/bold] (ollama ps)")
        os.system("ollama ps || true")

    load_seeds, rag_flag = _try_import_rag()
    infer_flags, llm_refine_rationales = _try_import_llm()
    if not (load_seeds and rag_flag and infer_flags):
        console.print("[red]RAG+LLM requires toscheck.rag and toscheck.llm to be available.[/red]")
        raise SystemExit(2)

    t0 = time.perf_counter()

    if args.progress:
        with _make_progress() as prog:
            # Parse
            t_parse = prog.add_task("Parse", total=1)
            text = read_text(args.input)
            sents = split_sentences(text)
            prog.advance(t_parse)

            # RAG preselect (candidates only)
            t_rag = prog.add_task("RAG select", total=1)
            seeds = load_seeds(args.seeds)
            rag_hits = rag_flag(sents, seeds, threshold=args.threshold)  # [{"category","sentence_indexes",...}]
            cand = sorted({i for f in rag_hits for i in f.get("sentence_indexes", [])})
            if args.max_suspects and len(cand) > args.max_suspects:
                cand = cand[:args.max_suspects]
            prog.advance(t_rag)

            # LLM classify on candidates only
            t_llm = prog.add_task("LLM classify", total=1)
            if cand:
                numbered = [f"{i}: {sents[i]}" for i in cand]
                llm_out = infer_flags(numbered, llm_only=True) or []
                for f in llm_out:
                    f["sentence_indexes"] = _remap_indexes(f.get("sentence_indexes"), cand)
            else:
                llm_out = []
            prog.advance(t_llm)

            # Merge RAG evidence + LLM decisions
            t_merge = prog.add_task("Merge", total=1)
            combined = rag_hits + llm_out
            flags = _merge_flags(sents, combined)
            if args.llm_polish and flags:
                try:
                    flags = llm_refine_rationales(sents, flags)
                except Exception:
                    pass
            prog.advance(t_merge)
    else:
        text = read_text(args.input)
        sents = split_sentences(text)
        seeds = load_seeds(args.seeds)
        rag_hits = rag_flag(sents, seeds, threshold=args.threshold)
        cand = sorted({i for f in rag_hits for i in f.get("sentence_indexes", [])})
        if args.max_suspects and len(cand) > args.max_suspects:
            cand = cand[:args.max_suspects]
        if cand:
            numbered = [f"{i}: {sents[i]}" for i in cand]
            llm_out = infer_flags(numbered, llm_only=True) or []
            for f in llm_out:
                f["sentence_indexes"] = _remap_indexes(f.get("sentence_indexes"), cand)
        else:
            llm_out = []
        combined = rag_hits + llm_out
        flags = _merge_flags(sents, combined)
        if args.llm_polish and flags:
            try:
                flags = llm_refine_rationales(sents, flags)
            except Exception:
                pass

    # Output
    elapsed = time.perf_counter() - t0
    rate = (len(sents) / elapsed) if elapsed > 0 else 0.0
    _header(MODEL, len(sents))
    render_flags(sents, flags)
    if args.report:
        save_report(sents, flags, args.report)
    if args.json:
        import json
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps(flags, ensure_ascii=False, indent=2))
    console.print(f"⏱️  [bold]Elapsed:[/bold] {elapsed:0.2f}s   •   [bold]Throughput:[/bold] {rate:0.1f} sentences/s")

if __name__ == "__main__":
    run_main()
