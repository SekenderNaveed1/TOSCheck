# toscheck/app.py
import argparse
from dotenv import load_dotenv

from toscheck.extract import read_text
from toscheck.chunk import chunk_text
from toscheck.index import build_and_save, load_index
from toscheck.retrieve import retrieve
from toscheck.llm import answer_with_rag
from toscheck.report import write_outputs, write_explanations
from toscheck.explain import explain_tos_with_kb

load_dotenv()


def main():
    parser = argparse.ArgumentParser("toscheck-rag")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # index
    pidx = sub.add_parser("index", help="Build a RAG index from a file, directory, or URL")
    pidx.add_argument("--input", help="Path to file OR directory")
    pidx.add_argument("--url", help="URL to fetch and index")
    pidx.add_argument("--cache", default=".ragcache")
    pidx.add_argument("--max-tokens", type=int, default=500)
    pidx.add_argument("--overlap", type=int, default=150)

    # ask
    pask = sub.add_parser("ask", help="Ask a question against a single local RAG index")
    pask.add_argument("--query", required=True)
    pask.add_argument("--k", type=int, default=6)
    pask.add_argument("--cache", default=".ragcache")
    pask.add_argument("--json")
    pask.add_argument("--md")

    # explain (dual-RAG)
    pexp = sub.add_parser("explain", help="Explain TOS clauses using document+KB indices")
    pexp.add_argument("--query", required=True)
    pexp.add_argument("--cache", default=".ragcache")
    pexp.add_argument("--kb", default="kb_rag")
    pexp.add_argument("--k-tos", type=int, default=8)
    pexp.add_argument("--k-kb", type=int, default=3)
    pexp.add_argument("--kb-threshold", type=float, default=0.30)
    pexp.add_argument("--all-chunks", action="store_true")
    pexp.add_argument("--md")
    pexp.add_argument("--json")

    # NEW: one-liner "scan" that does KB index + TOS index + explain
    pscan = sub.add_parser("scan", help="One-liner: index KB + index TOS + explain (all local via Ollama)")
    pscan.add_argument("--kb-dir", default="rag_patterns", help="Directory with KB patterns")
    pscan.add_argument("--kb-cache", default="kb_rag")
    pscan.add_argument("--kb-max", type=int, default=80)
    pscan.add_argument("--kb-overlap", type=int, default=20)

    pscan.add_argument("--tos-file", required=True, help="TOS file to analyze (txt/pdf/html)")
    pscan.add_argument("--tos-cache", default="tos_rag")
    pscan.add_argument("--tos-max", type=int, default=120)
    pscan.add_argument("--tos-overlap", type=int, default=40)

    pscan.add_argument("--k-kb", type=int, default=3, help="KB hits per clause after diversification")
    pscan.add_argument("--kb-threshold", type=float, default=0.35, help="Drop weak KB matches below this score")
    pscan.add_argument("--model", help="Override generation model (env OLLAMA_GEN_MODEL default)")

    pscan.add_argument("--md", default="scan_report.md")
    pscan.add_argument("--json", default="scan_report.json")

    args = parser.parse_args()

    if args.cmd == "index":
        print("📦 Building index...")
        text = read_text(args.input, args.url)
        chunks = chunk_text(text, max_tokens=args.max_tokens, overlap=args.overlap)
        build_and_save(chunks, out_dir=args.cache)
        print(f"✅ Indexed {len(chunks)} chunks → {args.cache}")

    elif args.cmd == "ask":
        print("❓ Running query...")
        data = load_index(out_dir=args.cache)
        results = retrieve(args.query, data, k=args.k)
        answer = answer_with_rag(args.query, results)
        write_outputs(args.query, results, answer, json_path=args.json, md_path=args.md)
        print("🧠 Answer:\n")
        print(answer)

    elif args.cmd == "explain":
        print("🧩 Running dual-RAG explanation...")
        results = explain_tos_with_kb(
            query=args.query,
            tos_cache=args.cache,
            kb_cache=args.kb,
            k_tos=args.k_tos,
            k_kb=args.k_kb,
            all_chunks=args.all_chunks,
            kb_score_threshold=args.kb_threshold,
        )
        combined = "\n\n".join(r.get("answer", "") for r in results)
        write_explanations(args.query, results, json_path=args.json, md_path=args.md)
        print("🧠 Explanation Summary:\n")
        print(combined)

    elif args.cmd == "scan":
        # 1) Index KB
        print("📚 Indexing KB…")
        kb_text = read_text(args.kb_dir, None)
        from toscheck.chunk import chunk_text  # uses dynamic chunker underneath
        kb_chunks = chunk_text(kb_text, max_tokens=args.kb_max, overlap=args.kb_overlap)
        build_and_save(kb_chunks, out_dir=args.kb_cache)
        print(f"✅ KB: {len(kb_chunks)} chunks → {args.kb_cache}")

        # 2) Index TOS file
        print("📄 Indexing TOS…")
        tos_text = read_text(args.tos_file, None)
        tos_chunks = chunk_text(tos_text, max_tokens=args.tos_max, overlap=args.tos_overlap)
        build_and_save(tos_chunks, out_dir=args.tos_cache)
        print(f"✅ TOS: {len(tos_chunks)} chunks → {args.tos_cache}")

        # 3) Explain all chunks against KB
        print("🧩 Explaining…")
        results = explain_tos_with_kb(
            query="Full risk review",
            tos_cache=args.tos_cache,
            kb_cache=args.kb_cache,
            k_tos=9999,            # ignored because we force all_chunks=True
            k_kb=args.k_kb,
            all_chunks=True,       # explain EVERY clause
            kb_score_threshold=args.kb_threshold,
        )
        combined = "\n\n".join(r.get("answer", "") for r in results)
        write_explanations("Full risk review", results, json_path=args.json, md_path=args.md)
        print(f"✅ Wrote: {args.md} and {args.json}")
        print("🧠 Explanation Summary:\n")
        print(combined)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
