from __future__ import annotations
import json, re
from typing import Any

def parse_flags(text: str) -> Any:
    text = text or ""
    # Try fenced JSON
    m = re.search(r"```json\s*(\{.*?\}|\[.*?\])\s*```", text, re.S | re.I)
    blob = m.group(1) if m else text
    try:
        return json.loads(blob)
    except Exception:
        pass
    # Last resort: first JSON-like block
    m2 = re.search(r"(\{.*\}|\[.*\])", text, re.S)
    if m2:
        try:
            return json.loads(m2.group(1))
        except Exception:
            return []
    return []
