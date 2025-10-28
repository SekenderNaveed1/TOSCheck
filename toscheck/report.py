from __future__ import annotations
from typing import List, Dict
from rich.console import Console
from rich.table import Table
import json

console = Console()

CANNED_RATIONALES = {
    "Unilateral changes": "Terms can be changed without notice/consent.",
    "Arbitration / class-action waiver": "Binding arbitration and/or class action/jury waiver.",
    "Governing law / venue": "Specifies governing law or exclusive venue.",
    "Termination for convenience": "Account can be terminated at any time/sole discretion.",
    "Warranty disclaimer": "Service provided “as is” / no warranties.",
    "Limitation of liability": "Liability capped or excludes consequential damages.",
    "Indemnification": "You must indemnify/hold provider harmless.",
    "Automatic renewal / negative option": "Auto-renews unless canceled (negative option).",
    "Cancellation hurdles": "Cancellation requires friction (e.g., call, mail, business hours).",
    "Price / fee changes": "Provider may change prices/fees.",
    "Refund exclusions": "Payments/fees are non-refundable.",
    "Broad license to user content": "Perpetual/worldwide/royalty-free license to your content.",
    "Data collection (personal)": "Collects personal information.",
    "Sensitive data / biometrics": "Processes sensitive/biometric/health data.",
    "Location / device data": "Accesses location/camera/mic/device data.",
    "Data sharing / sale": "Shares/sells personal data with partners/third parties.",
    "Targeted ads / profiling": "Uses data for targeted advertising or profiling.",
    "Third-party trackers / cookies": "Uses third-party cookies/pixels/SDKs; may not honor DNT.",
    "International transfers": "Transfers data internationally/outside your region.",
    "Data retention / deletion": "Retains data for long periods; deletion caveats.",
    "User rights (GDPR/CCPA/CPRA)": "Lists access/delete/opt-out/portability rights.",
    "Children's data (COPPA / minors)": "Restrictions or consent requirements for minors.",
    "Notice by posting only": "Changes announced only by posting on a page.",
    "Opt-out hard to find": "Opt-out requires friction (mail/print/fax).",
}

def print_header(model: str, n_sentences: int):
    console.print("╭──────────────────────────────────────╮")
    console.print(f"│ Model: {model}  |  Sentences: {n_sentences:<5} │")
    console.print("╰──────────────────────────────────────╯")

def _friendly_rationale(cat: str, raw: str | None) -> str:
    raw = (raw or "").strip()
    return raw if raw else CANNED_RATIONALES.get(cat, "—")

def render_flags(sentences: List[str], flags: List[Dict]):
    if not flags:
        console.print("✅ No flags detected in the scanned chunk.")
        return
    table = Table(title="TOSCheck Flags")
    table.add_column("Category", no_wrap=True)
    table.add_column("Cited Sentences")
    table.add_column("Rationale", no_wrap=True)
    for f in flags:
        cat = f.get("category", "Unknown")
        rat = _friendly_rationale(cat, f.get("rationale"))
        cited_lines = []
        for idx in f.get("sentence_indexes", []):
            if 0 <= idx < len(sentences):
                cited_lines.append(f"{idx}. {sentences[idx]}")
        table.add_row(cat, "\n".join(cited_lines), rat)
    console.print(table)

def save_report(sentences: List[str], flags: List[Dict], out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# TOSCheck Report\n\n")
        for fdict in flags:
            cat = fdict.get("category", "Unknown")
            f.write(f"## {cat}\n\n")
            f.write(f"**Rationale:** {_friendly_rationale(cat, fdict.get('rationale'))}\n\n")
            f.write("**Cited Sentences:**\n\n")
            for idx in fdict.get("sentence_indexes", []):
                if 0 <= idx < len(sentences):
                    f.write(f"- ({idx}) {sentences[idx]}\n")
            ev = fdict.get("evidence") or []
            if ev:
                f.write("\n**Evidence (RAG seeds):**\n\n")
                for e in ev:
                    idx = e.get("sentence_index")
                    seed = e.get("matched_seed", "")
                    sim = e.get("similarity", 0.0)
                    f.write(f"- sentence {idx}: seed = \"{seed}\" (sim {sim:.2f})\n")
            f.write("\n---\n\n")
    console.print(f":page_facing_up: Saved markdown report → {out_path}")

def save_json(flags: List[Dict], out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(flags, f, ensure_ascii=False, indent=2)
    console.print(f":floppy_disk: Saved JSON → {out_path}")
