# toscheck/report.py
import json
from datetime import datetime

def write_outputs(query: str, hits: list[dict], answer: str, json_path: str | None, md_path: str | None):
    if json_path:
        with open(json_path, "w") as f:
            json.dump({
                "query": query,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "answer": answer,
                "hits": hits
            }, f, indent=2)

    if md_path:
        with open(md_path, "w") as f:
            f.write(f"# Answer\n\n{answer}\n\n")
            f.write("## Retrieved Chunks\n\n")
            for h in hits:
                idx = h.get("idx")
                score = h.get("score", 0.0)
                chunk = h.get("chunk", "")
                f.write(f"### [{idx}] (score {score:.3f})\n\n{chunk}\n\n---\n")


def write_explanations(query: str, explanations: list[dict], json_path: str | None, md_path: str | None):
    payload = {
        "query": query,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "explanations": explanations,
    }

    if json_path:
        with open(json_path, "w") as f:
            json.dump(payload, f, indent=2)

    if md_path:
        with open(md_path, "w") as f:
            f.write(f"# Explanation Results\n\n")
            f.write(f"_Query:_ **{query}**\n\n")
            for n, item in enumerate(explanations, 1):
                clause = item.get("clause", "")
                ans = item.get("answer", "")
                pats = item.get("patterns", [])

                # try to extract category hint from the LLM's last line
                likely_cat = ""
                for line in ans.splitlines()[::-1]:
                    if "Likely category:" in line:
                        likely_cat = line.strip()
                        break

                title = f"## Clause {n}"
                if likely_cat:
                    title += f" — {likely_cat.replace('Likely category:','').strip()}"
                f.write(title + "\n\n")

                f.write(f"**Clause text:**\n\n> {clause}\n\n")
                f.write(f"**Matched patterns from KB:**\n\n")
                if not pats:
                    f.write("- (no close KB matches)\n\n")
                else:
                    for p in pats:
                        idx = p.get("idx")
                        score = p.get("score", 0.0)
                        chunk = p.get("chunk", "")
                        # show only first 500 chars for readability
                        display = chunk[:500] + ("…" if len(chunk) > 500 else "")
                        f.write(f"- **[{idx}]** (score {score:.3f}) — {display}\n")
                f.write("\n**Explanation:**\n\n")
                f.write(ans + "\n\n---\n")
