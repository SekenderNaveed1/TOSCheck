from __future__ import annotations
import json
from typing import List, Dict
import ollama
from .utils import MODEL, NUM_CTX, TEMPERATURE, TOP_P


SYSTEM = (
"You are TOSCheck, a terse compliance spotter. "
"Given sentences from Terms/Privacy docs, return compact flags using the allowed categories."
)


USER_TEMPLATE = """You are given numbered sentences from a Terms/Privacy document.\n\nCategories:\n- Unilateral changes\n- Data sharing\n- Arbitration\n- Vague permissions\n- Opt-out tricks\n\nReturn JSON list like:\n[\n {{\n \"category\": \"<one of the above>\",\n \"sentence_indexes\": [<ints>],\n \"rationale\": \"<short reason>\"\n }}\n]\n\nSentences:\n{sentences}\n"""



def infer_flags(numbered_sentences: List[str]) -> List[Dict]:
    prompt = USER_TEMPLATE.format(sentences="\n".join(numbered_sentences))
    res = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        options={
            "num_ctx": NUM_CTX,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
        },
        stream=False,
    )
    txt = res["message"]["content"]
    try:
        blob = json.loads(_grab_json_block(txt))
        return blob if isinstance(blob, list) else []
    except Exception:
        return []




def _grab_json_block(txt: str) -> str:
    import re
    m = re.search(r"\[.*\]", txt, re.S)
    return m.group(0) if m else "[]"