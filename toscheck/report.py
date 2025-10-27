from __future__ import annotations
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


console = Console()




def print_header(model: str, num_sentences: int):
    console.print(Panel.fit(f"[bold]Model:[/bold] {model} | [bold]Sentences:[/bold] {num_sentences}"))




def render_flags(sentences: List[str], flags: List[Dict]):
    if not flags:
        console.print(":white_heavy_check_mark: No flags detected in the scanned chunk.")
        return
    table = Table(title="TOSCheck Flags", show_lines=True)
    table.add_column("Category", style="bold")
    table.add_column("Cites")
    table.add_column("Why")
    for f in flags:
        cites = []
        for idx in f["sentence_indexes"]:
            if 0 <= idx < len(sentences):
                cites.append(f"{idx}. {sentences[idx]}")
        table.add_row(f["category"], "\n".join(cites), f.get("rationale", ""))
    console.print(table)