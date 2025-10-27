import re
from typing import Dict, List

# Expanded categories aligned with ToS;DR themes, GDPR/CCPA concepts, and common consumer contract clauses.
# These are heuristic regexes: conservative enough to avoid spam, broad enough to catch variants.
PATTERNS: Dict[str, List[re.Pattern]] = {
    # Contract power & procedural
    "Unilateral changes": [
        re.compile(r"\b(change|modify|amend|update)\b.*\b(any time|without\s+notice|at\s+our\s+sole\s+discretion)\b", re.I),
    ],
    "Governing law / venue": [
        re.compile(r"\b(governing\s+law|jurisdiction|venue|choice\s+of\s+law)\b", re.I),
    ],
    "Arbitration / class-action waiver": [
        re.compile(r"\b(binding|mandatory)\b.*\barbitration\b", re.I),
        re.compile(r"\b(class\s+action)\b.*\b(waiver|waive|barred)\b", re.I),
        re.compile(r"\b(waive|waiver)\b.*\b(jury\s+trial)\b", re.I),
    ],
    "Termination for convenience": [
        re.compile(r"\b(terminate|suspend)\b.*\b(at\s+any\s+time|for\s+any\s+reason|sole\s+discretion)\b", re.I),
    ],

    # Liability & warranty
    "Limitation of liability": [
        re.compile(r"\blimitation\s+of\s+liability\b", re.I),
        re.compile(r"\b(liability)\b.*\b(limited\s+to|cap(ped)?\s+at|maximum)\b", re.I),
        re.compile(r"\b(indirect|incidental|consequential|special|punitive)\s+damages\b", re.I),
    ],
    "Warranty disclaimer": [
        re.compile(r"\b(as\s+is|as-?is|as\s+available|no\s+warrant(y|ies))\b", re.I),
    ],
    "Indemnification": [
        re.compile(r"\bindemnif(y|ication)\b|\bhold\s+harmless\b", re.I),
    ],
    "Security disclaimers": [
        re.compile(r"\b(security)\b.*\b(not\s+guaranteed|cannot\s+guarantee|at\s+your\s+own\s+risk)\b", re.I),
    ],

    # Money & subscriptions
    "Automatic renewal / negative option": [
        re.compile(r"\b(auto(matic)?\s*renew(al)?)\b", re.I),
        re.compile(r"\b(negative\s+option|continuity\s+plan|free\s+trial)\b", re.I),
    ],
    "Cancellation hurdles": [
        re.compile(r"\b(cancel(lation)?)\b.*\b(phone|fax|mail|in\s+person|business\s+hours|written\s+request)\b", re.I),
        re.compile(r"\b(retentions?\s+team|chat\s+only|call\s+to\s+cancel)\b", re.I),
    ],
    "Price / fee changes": [
        re.compile(r"\b(change|increase)\b.*\b(price|fees?|charges?)\b", re.I),
    ],
    "Refund exclusions": [
        re.compile(r"\b(no\s+refunds?|non-?refundable|credit\s+only)\b", re.I),
    ],

    # IP & content
    "Broad license to user content": [
        re.compile(r"\b(license|licence)\b.*\b(perpetual|irrevocable|worldwide|royalty-?free)\b.*\b(your\s+content|user\s+content|submissions?)\b", re.I),
    ],
    "DMCA / takedown": [
        re.compile(r"\b(dmca|digital\s+millennium\s+copyright)\b", re.I),
    ],

    # Privacy: collection, sharing, retention, rights
    "Data collection (personal)": [
        re.compile(r"\b(collect|obtain|receive)\b.*\b(personal\s+data|personal\s+information|PII)\b", re.I),
    ],
    "Sensitive data / biometrics": [
        re.compile(r"\b(sensitive)\s+(personal\s+)?(information|data)\b", re.I),
        re.compile(r"\b(biometric|faceprint|voiceprint|fingerprint|iris|retina)\b", re.I),
        re.compile(r"\b(health|medical|genetic)\s+data\b", re.I),
    ],
    "Location / device data": [
        re.compile(r"\b(location|geolocation|GPS)\b", re.I),
        re.compile(r"\b(camera|microphone|contacts|photos)\b.*\b(access|collect|scan)\b", re.I),
    ],
    "Data sharing / sale": [
        re.compile(r"\b(share|disclose|transfer)\b.*\b(third\s+part(y|ies)|partners?|affiliates?)\b", re.I),
        re.compile(r"\b(sell|sale\s+of)\b.*\b(personal\s+information|personal\s+data)\b", re.I),
        re.compile(r"\b(share)\b.*\b(for\s+target(ed|ing)?\s+ads?|cross-?context\s+behavioral)\b", re.I),
    ],
    "Targeted ads / profiling": [
        re.compile(r"\b(target(ed|ing)?\s+ads?|behavioral\s+advertis(ing|ements?)|profiling)\b", re.I),
    ],
    "Third-party trackers / cookies": [
        re.compile(r"\b(cookies?|pixels?|sdk(s)?|beacons?)\b.*\b(third\s+part(y|ies)|analytics|advertis(ing|ers))\b", re.I),
        re.compile(r"\b(do\s+not\s+track|DNT)\b.*\b(not\s+honor|ignore|no(t)?\s+respond)\b", re.I),
    ],
    "International transfers": [
        re.compile(r"\b(transfer)\b.*\b(internationally|outside\s+the\s+(EU|EEA|UK|country|state))\b", re.I),
    ],
    "Data retention / deletion": [
        re.compile(r"\b(retain|retention|store)\b.*\b(until|as\s+long\s+as|for\s+as\s+long)\b", re.I),
        re.compile(r"\b(delete|erasure|de-identif(y|ication))\b", re.I),
        re.compile(r"\b(deactivate|disable)\b.*\b(account)\b.*\b(not\s+delete|retain)\b", re.I),
    ],
    "User rights (GDPR/CCPA/CPRA)": [
        re.compile(r"\b(access|rectification|correction|erasure|delete|restriction|object|portability)\b.*\b(rights?)\b", re.I),
        re.compile(r"\b(opt-?out)\b.*\b(sale|share|target(ed|ing)?\s+ads?|analytics)\b", re.I),
        re.compile(r"\b(limit\s+use)\b.*\b(sensitive\s+personal)\b", re.I),
    ],
    "Children's data (COPPA / minors)": [
        re.compile(r"\b(children|child|minor(s)?)\b.*\b(under\s*(13|16)|parent(al)?\s+consent)\b", re.I),
    ],

    # Notice & opt-out mechanics
    "Vague permissions": [
        re.compile(r"\bmay\b.*\b(as\s+we\s+deem|as\s+we\s+determine|at\s+our\s+discretion)\b", re.I),
    ],
    "Opt-out hard to find": [
        re.compile(r"\b(opt[- ]?out|unsubscribe)\b.*\b(mail|fax|write|post(al)?\s+mail|print)\b", re.I),
    ],
    "Notice by posting only": [
        re.compile(r"\b(notice)\b.*\b(by\s+posting|post(ed)?\s+on\s+this\s+page)\b", re.I),
    ],
}

# Keep the exported category order stable:
CATEGORIES = list(PATTERNS.keys())
