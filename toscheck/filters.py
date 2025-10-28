from __future__ import annotations
import re
from typing import Iterable, List

KEYWORDS = [
    r'\barbitration\b', r'\bclass action\b', r'\bjury trial\b',
    r'\bindemnif(y|ication)\b', r'\blimitation of liabilit(y|ies)\b',
    r'\bsole discretion\b', r'\bterminate (your|the) account\b',
    r'\bnon[- ]?refundable\b', r'\bperpetual\b', r'\birrevocable\b',
    r'\baffiliate(s)?\b', r'\bthird[-\s]?part(y|ies)\b', r'\bpartners?\b',
    r'\bshare (your|personal) data\b', r'\bsell (your|personal) data\b',
    r'\bchange (these )?terms\b', r'\bmodify (these )?terms\b',
    r'\bautomatically? renews?\b', r'\bnegative option\b',
    r'\bdo not track\b', r'\bcookies?\b', r'\btracking pixel(s)?\b',
    r'\binternational transfer(s)?\b', r'\bretention\b', r'\bdelete\b',
    r'\bchildren|minors|under (13|16)\b', r'\bgoverning law\b', r'\bvenue\b',
]

KEY_RX = re.compile("|".join(KEYWORDS), re.I)

def keyword_filter(sentences: List[str]) -> List[int]:
    return [i for i, s in enumerate(sentences) if KEY_RX.search(s or "")]
