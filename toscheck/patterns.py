import re
from typing import Dict, List


PATTERNS: Dict[str, List[re.Pattern]] = {
"Unilateral changes": [re.compile(r"\b(change|modify|amend)\b.*\b(any time|without notice)\b", re.I)],
"Data sharing": [re.compile(r"\b(share|disclose|transfer)\b.*\b(third part(y|ies)|partners?|affiliates?)\b", re.I)],
"Arbitration": [
re.compile(r"\b(binding|mandatory)\b.*\barbitration\b", re.I),
re.compile(r"\b(class action)\b.*\b(waiver|waive)\b", re.I),
],
"Vague permissions": [re.compile(r"\bmay\b.*\b(as we|as (we )?deem|at our discretion)\b", re.I)],
"Opt-out tricks": [re.compile(r"\b(opt[- ]?out)\b.*\b(within|by)\b.*\b(days|writing|mail)\b", re.I)],
}


CATEGORIES = list(PATTERNS.keys())