from __future__ import annotations
import os, sys, argparse, time
from rich.console import Console
from nltk import download as nltk_download
from .utils import BANNER, MODEL
from .extract import read_text
from .scoring import split_sentences, merge_llm_flags
from .llm import infer_flags, heuristic_flags_all
from .report import render_flags, save_report

console = Console()

def _ensure_nltk():
    try:
        import nltk
        nltk.data.find("tokenizers/punkt")
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        console.print("[yellow]NLTK data missing, downloading...[/yellow]")
        nltk_download("punkt")
        try:
            nltk_download("punkt_tab")
        except Exception:
            pass
        console.print("[green]NLTK ready[/green]")

def print_header(model, count):
    console.print("╭──────────────────────────────────────╮")
    console.print(f"│ Model: {model}  |  Sentences: {count:<5} │")
    console.print("╰──────────────────────────────────────╯")

def run_main():
    _ensure_nltk()
    parser = argparse.ArgumentParser(description="TOSCheck – flag risky ToS clauses.")
    parser.add_argument("input", help="Path or URL of the Terms file to scan.")
    parser.add_argument("--report", help="Markdown report path (optional).")
    parser.add_argument("--json", help="Save JSON output here (optional).")

    # long / windowed scanning
    parser.add_argument("--long", action="store_true", help="Windowed scanning for long ToS (recommended).")
    parser.add_argument("--window", type=int, default=120, help="Sentences per window.")
    parser.add_argument("--overlap", type=int, default=30, help="Overlap between windows.")

    # engines
    parser.add_argument("--engine", choices=["heuristics", "llm", "hybrid", "rag"], default="hybrid",
                        help="Engine: heuristics, llm, rag, or hybrid (union of all).")
    parser.add_argument("--seeds", default="seeds.yml", help="Path to seeds.yml for RAG mode.")
    parser.add_argument("--threshold", type=float, default=0.75, help="RAG similarity threshold (0–1).")
    parser.add_argument("--llm-polish", action="store_true",
                        help="Use LLM to rewrite rationales (short, clear).")

    # progress toggles
    parser.add_argument("--progress", dest="progress", action="store_true", help="Show progress bar (default).")
    parser.add_argument("--no-progress", dest="progress", action="store_false", help="Disable progress bar.")
    parser.set_defaults(progress=True)

    parser.add_argument("--debug", action="store_true", help="Verbose output.")
    args = parser.parse_args()

    t0 = time.perf_counter()

    text = read_text(args.input)
    sents = split_sentences(text)
    use_long = args.long or len(sents) > 400

    if use_long:
        from .longscan import scan_windows
        flags = scan_windows(
            sents, args.engine, args.window, args.overlap,
            args.seeds, args.threshold, debug=args.debug,
            llm_polish=args.llm_polish, show_progress=args.progress
        )
    else:
        if args.engine == "heuristics":
            numbered = [f"{i}: {s}" for i, s in enumerate(sents)]
            flags = heuristic_flags_all(numbered)
        elif args.engine == "rag":
            from .rag import load_seeds, rag_flag
            seeds = load_seeds(args.seeds)
            flags = rag_flag(sents, seeds, threshold=args.threshold)
        elif args.engine == "llm":
            flags = infer_flags([f"{i}: {s}" for i, s in enumerate(sents)], llm_only=True)
        else:  # hybrid (union of rag + heuristics + llm)
            from .rag import load_seeds, rag_flag
            from .longscan import _merge_flag_lists
            seeds = load_seeds(args.seeds)
            r = rag_flag(sents, seeds, threshold=args.threshold)
            h = heuristic_flags_all([f"{i}: {s}" for i, s in enumerate(sents)])
            l = infer_flags([f"{i}: {s}" for i, s in enumerate(sents)], llm_only=True)
            flags = _merge_flag_lists([r, h, l])

            if args.llm_polish and flags:
                from .llm import llm_refine_rationales
                try:
                    flags = llm_refine_rationales(sents, flags)
                except Exception:
                    pass

    print_header(MODEL, len(sents))
    render_flags(sents, flags)
    if args.report:
        save_report(sents, flags, args.report)
    if args.json:
        from .report import save_json
        save_json(flags, args.json)

    elapsed = time.perf_counter() - t0
    rate = (len(sents) / elapsed) if elapsed > 0 else 0.0
    console.print(f"⏱️  [bold]Elapsed:[/bold] {elapsed:0.2f}s   •   [bold]Throughput:[/bold] {rate:0.1f} sentences/s")

if __name__ == "__main__":
    run_main()
