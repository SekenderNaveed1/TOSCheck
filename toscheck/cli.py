from __future__ import annotations
import sys, argparse
from rich.console import Console
from nltk import download as nltk_download
from .utils import BANNER, MODEL
from .extract import read_text
from .scoring import split_sentences, select_candidate_indexes, number_subset, merge_llm_flags
from .llm import infer_flags
from .report import print_header, render_flags, save_report

console = Console()

def _ensure_nltk():
    """Ensure nltk resources are available, including punkt_tab fallback."""
    try:
        nltk_download("punkt", quiet=True)
        try:
            nltk_download("punkt_tab", quiet=True)
        except Exception:
            pass
    except Exception:
        pass

def run_main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="TOSCheck — flag TOS/Privacy clauses.")
    parser.add_argument("input", help="Path to .txt/.pdf or URL. Use '-' to read stdin.")
    parser.add_argument("--all", action="store_true", help="Scan the whole doc in sliding windows (basic).")
    parser.add_argument("--window", type=int, default=300, help="Approx sentences/window when --all is used.")
    parser.add_argument("--report", type=str, default="", help="Save a markdown report to this path.")
    args = parser.parse_args(argv)

    _ensure_nltk()

    text = sys.stdin.read() if args.input == "-" else read_text(args.input)
    sents = split_sentences(text)
    idxs = select_candidate_indexes(sents) if not args.all else list(range(len(sents)))

    if args.all:
        step = max(50, args.window // 2)
        final_flags, start = [], 0
        while start < len(sents):
            end = min(len(sents), start + args.window)
            numbered = [f"{i}: {sents[i]}" for i in range(start, end)]
            final_flags.extend(infer_flags(numbered))
            start += step
        flags = merge_llm_flags(sents, final_flags)
    else:
        numbered = number_subset(sents, idxs)
        flags = merge_llm_flags(sents, infer_flags(numbered))

    print_header(MODEL, len(sents))
    render_flags(sents, flags)
    if args.report:
        save_report(sents, flags, args.report)

# alias for console script
app = run_main
