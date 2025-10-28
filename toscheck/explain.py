# toscheck/explain.py
from dotenv import load_dotenv
from collections import defaultdict
from toscheck.index import load_index
from toscheck.retrieve import retrieve
from toscheck.llm import _client, GEN_MODEL

load_dotenv()


def _diversify_by_kb_filename(kb_hits: list[dict], max_per_file: int = 1) -> list[dict]:
    """
    Prefer variety: limit how many hits from the same KB file we keep.
    We infer filename from a header marker inserted during directory indexing (if present),
    falling back to chunk text heuristics.
    """
    buckets = defaultdict(list)
    for h in kb_hits:
        chunk = h.get("chunk", "")
        # Try to detect "### FILE: <name>" marker from extract.py directory indexing
        fname = "unknown"
        marker = "### FILE:"
        if marker in chunk.splitlines()[0]:
            # first line looks like "### FILE: X"
            fname = chunk.splitlines()[0].replace(marker, "").strip()
        else:
            # crude guess by keyword
            for k in ("arbitration", "unilateral_changes", "refund", "content_rights", "surveillance", "data_collection"):
                if k in chunk.lower():
                    fname = f"{k}.txt"
                    break
        buckets[fname].append(h)

    diversified = []
    for fname, items in buckets.items():
        items = sorted(items, key=lambda x: x.get("score", 0.0), reverse=True)
        diversified.extend(items[:max_per_file])
    # sort again by score overall
    return sorted(diversified, key=lambda x: x.get("score", 0.0), reverse=True)


def explain_tos_with_kb(
    query: str,
    tos_cache: str,
    kb_cache: str,
    k_tos: int = 8,
    k_kb: int = 3,
    all_chunks: bool = True,
    kb_score_threshold: float = 0.30,
):
    """
    Explain the entire TOS (or top-k chunks) using KB patterns.

    - all_chunks=True: iterate every TOS chunk
    - k_kb: how many KB patterns to show per clause (after diversification)
    - kb_score_threshold: drop weak KB matches
    """
    print("🔍 Loading indexes...")
    tos_data = load_index(out_dir=tos_cache)
    kb_data  = load_index(out_dir=kb_cache)

    # choose which TOS chunks to process
    if all_chunks:
        print(f"📄 Using all TOS chunks: {len(tos_data['chunks'])}")
        tos_hits = [{"idx": i, "score": 1.0, "chunk": c} for i, c in enumerate(tos_data["chunks"])]
    else:
        tos_hits = retrieve(query, tos_data, k=k_tos)
        print(f"📄 Retrieved {len(tos_hits)} relevant TOS chunks by query")

    explanations = []

    for hit in tos_hits:
        clause = hit["chunk"]
        raw_kb_hits = retrieve(clause, kb_data, k=20)  # get a larger pool first
        # threshold + diversify by file name, then truncate to k_kb
        filtered = [h for h in raw_kb_hits if h.get("score", 0.0) >= kb_score_threshold]
        kb_hits = _diversify_by_kb_filename(filtered, max_per_file=1)[:k_kb]

        kb_context = "\n\n---\n\n".join(
            (f"[{j}] {k['chunk']}") for j, k in enumerate(kb_hits)
        ) if kb_hits else "(no close KB matches)"

        prompt = f"""
You are analyzing a Terms of Service clause using known red-flag patterns. Explain clearly what the clause means, why it matters, and cite which patterns match.

Clause:
{clause}

Relevant known patterns (from a curated KB):
{kb_context}

Respond with:
- 1–2 sentence plain-language summary
- Bullet list of risks/implications with short quotes where possible
- Final line: "Likely category: <category guess>"
If nothing matches, say: "No close KB match found."
"""

        resp = _client.chat.completions.create(
            model=GEN_MODEL,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = resp.choices[0].message.content.strip()

        explanations.append({
            "clause_idx": hit.get("idx"),
            "clause": clause,
            "patterns": kb_hits,   # each has idx/score/chunk
            "answer": answer
        })

    return explanations
