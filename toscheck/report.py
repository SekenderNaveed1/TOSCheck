from __future__ import annotations
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def print_header(model: str, num_sentences: int):
    """Display a header panel with the current model and total sentences processed."""
    console.print(Panel.fit(f"[bold]Model:[/bold] {model}  |  [bold]Sentences:[/bold] {num_sentences}"))

def render_flags(sentences: List[str], flags: List[Dict]):
    """Render the detected flags in a formatted table."""
    if not flags:
        console.print(":white_heavy_check_mark: No flags detected in the scanned chunk.")
        return
    table = Table(title="TOSCheck Flags", show_lines=True)
    table.add_column("Category", style="bold cyan", no_wrap=True)
    table.add_column("Cited Sentences", style="dim")
    table.add_column("Rationale", style="green")
    for f in flags:
        cites = []
        for idx in f.get("sentence_indexes", []):
            if 0 <= idx < len(sentences):
                cites.append(f"{idx}. {sentences[idx]}")
        cites_text = "\n".join(cites) if cites else "—"
        rationale = f.get("rationale", "").strip() or "—"
        table.add_row(f.get("category", "Unknown"), cites_text, rationale)
    console.print(table)

def save_report(sentences: List[str], flags: List[Dict], out_path: str):
    """Save the results as a markdown report for sharing or documentation."""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# TOSCheck Report\n\n")
        if not flags:
            f.write("✅ No flags detected in the scanned text.\n")
            return
        for fdict in flags:
            f.write(f"## {fdict.get('category', 'Unknown')}\n\n")
            f.write(f"**Rationale:** {fdict.get('rationale', '—')}\n\n")
            f.write("**Cited Sentences:**\n\n")
            for idx in fdict.get("sentence_indexes", []):
                if 0 <= idx < len(sentences):
                    f.write(f"- ({idx}) {sentences[idx]}\n")
            f.write("\n---\n\n")
    console.print(f":page_facing_up: Saved markdown report → [green]{out_path}[/green]")
