"""Regex/keyword pattern libraries for rule-based detectors (Turkish + English).

Patterns are compiled once at import time. Each pattern group is a list of
``(name, compiled_regex)`` tuples so detectors can report *which* rule fired.
"""

from __future__ import annotations

import re
from re import Pattern

# ---------------------------------------------------------------------------
# Prompt injection — attempts to override/ignore prior instructions.
# ---------------------------------------------------------------------------
_INJECTION_RAW: dict[str, str] = {
    # English
    "ignore_instructions": r"\bignore\s+(all\s+|the\s+|your\s+|previous\s+|above\s+)*"
    r"(instructions?|prompts?|rules?|context)\b",
    "disregard": r"\bdisregard\s+(all\s+|the\s+|your\s+|previous\s+|above\s+)*"
    r"(instructions?|prompts?|rules?)\b",
    "forget_everything": r"\bforget\s+(everything|all|previous|what\s+i\s+said|the\s+above)\b",
    "override": r"\boverride\s+(the\s+|your\s+|all\s+)*(instructions?|rules?|settings?|system)\b",
    "reveal_system_prompt": r"\b(reveal|show|print|repeat|display|leak)\s+"
    r"(me\s+)?(the\s+|your\s+|initial\s+)*(system\s+)?(prompt|instructions?|rules?)\b",
    "new_instructions": r"\b(here\s+are\s+|these\s+are\s+)?(your\s+)?new\s+instructions?\b",
    "you_are_now": r"\byou\s+are\s+now\b",
    "developer_mode": r"\bdeveloper\s+mode\b",
    # Turkish
    "tr_ignore": r"\b(t[üu]m\s+)?(talimatlar[ıi]|kurallar[ıi]|komutlar[ıi])[ıi]?\s*"
    r"(unut|yok\s*say|g[öo]rmezden\s+gel|dikkate\s+alma|iptal\s+et)\b",
    "tr_forget": r"\bunut\s+(her\s*[şs]eyi|t[üu]m[üu]n[üu]|[öo]ncekiler[ıi])\b",
    "tr_reveal_prompt": r"\b(sistem\s+)?(prompt|talimat|y[öo]nerge)(unu|[ıi]n[ıi]|lar[ıi]n[ıi])?\s+"
    r"(g[öo]ster|a[çc][ıi]kla|s[öo]yle|yaz|payla[şs])\b",
    "tr_override": r"\b(kurallar[ıi]|talimatlar[ıi]|ayarlar[ıi])[ıi]?\s+(de[ğg]i[şs]tir|ez|ge[çc]ersiz)\b",
    "tr_new_instructions": r"\byeni\s+(talimat|kural|y[öo]nerge)(lar)?[ıi]?n?\b",
    "tr_act_as": r"\bsen\s+art[ıi]k\b|\b[şs]imdi\s+sen\b",
}

# ---------------------------------------------------------------------------
# Jailbreak — persona/roleplay/encoding tricks to bypass safety.
# ---------------------------------------------------------------------------
_JAILBREAK_RAW: dict[str, str] = {
    "dan": r"\bDAN\b|\bdo\s+anything\s+now\b",
    "jailbreak_word": r"\bjailbreak(en|ing)?\b",
    "roleplay_evil": r"\b(pretend|act|roleplay|imagine)\b.{0,40}\b(no\s+(rules|restrictions|filters?|limits)"
    r"|without\s+(any\s+)?(rules|restrictions|filters?|ethics|guidelines))\b",
    "no_restrictions": r"\b(no|without|ignore\s+all)\s+(restrictions?|filters?|guidelines?|"
    r"limitations?|safety|ethics?)\b",
    "hypothetical_bypass": r"\bhypothetically\b.{0,40}\b(how\s+(would|to)|steps?)\b",
    "opposite_mode": r"\b(opposite|evil|unfiltered|uncensored)\s+(mode|version|ai|assistant|gpt)\b",
    "grandma_exploit": r"\bmy\s+(dead\s+)?grandma\b|\bdece[a]?sed\s+grandmother\b",
    # Turkish
    "tr_roleplay": r"\b(rol\s*yap|canland[ıi]r|hayal\s+et)\b.{0,40}\b"
    r"(kural(s[ıi]z|lar\s+olmadan)|s[ıi]n[ıi]rs[ıi]z|k[ıi]s[ıi]tlama\s+olmadan|filtresiz)\b",
    "tr_no_rules": r"\b(kural|s[ıi]n[ıi]r|filtre|k[ıi]s[ıi]tlama|etik)(lar|ler)?\s*(s[ıi]z|olmadan)\b",
    "tr_evil_mode": r"\b(k[öo]t[üu]|sansu?rsuz|filtresiz)\s+(mod|versiyon|yapay\s+zeka)\b",
}

# ---------------------------------------------------------------------------
# Turkish PII patterns. Named capture where useful.
# ---------------------------------------------------------------------------
_PII_RAW: dict[str, str] = {
    # TC Kimlik No — 11 digits, first digit non-zero (validated separately).
    "tc_kimlik": r"\b[1-9][0-9]{10}\b",
    # Turkish phone: +90 / 0 followed by 10 digits, optional separators.
    # Lookarounds keep it from matching a slice of a longer digit run (e.g. a
    # 16-digit card number that happens to contain "0555...").
    "telefon": r"(?<!\d)(?:\+90|0)\s*\(?5\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}(?!\d)",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    # Turkish IBAN: TR + 24 digits (26 chars total), optional spaces.
    "iban": r"\bTR\d{2}(?:\s?\d{4}){5}\s?\d{2}\b|\bTR\d{24}\b",
    # Credit card — 13-16 digits, optional separators (Luhn-checked separately).
    "kredi_karti": r"\b(?:\d[ -]?){13,16}\b",
}


def _compile(raw: dict[str, str]) -> list[tuple[str, Pattern[str]]]:
    flags = re.IGNORECASE | re.UNICODE
    return [(name, re.compile(pat, flags)) for name, pat in raw.items()]


INJECTION_PATTERNS: list[tuple[str, Pattern[str]]] = _compile(_INJECTION_RAW)
JAILBREAK_PATTERNS: list[tuple[str, Pattern[str]]] = _compile(_JAILBREAK_RAW)
PII_PATTERNS: list[tuple[str, Pattern[str]]] = _compile(_PII_RAW)

# Human-readable mask labels per PII category.
PII_LABELS: dict[str, str] = {
    "tc_kimlik": "[TC_KİMLİK]",
    "telefon": "[TELEFON]",
    "email": "[EMAIL]",
    "iban": "[IBAN]",
    "kredi_karti": "[KREDİ_KARTI]",
    "isim": "[İSİM]",
}


def validate_tc_kimlik(value: str) -> bool:
    """Validate a Turkish national ID number (TC Kimlik No).

    Rules: 11 digits, first digit non-zero, and the two checksum digits
    (10th and 11th) satisfy the official algorithm.
    """
    digits = [c for c in value if c.isdigit()]
    if len(digits) != 11 or digits[0] == "0":
        return False
    d = [int(c) for c in digits]
    odd_sum = d[0] + d[2] + d[4] + d[6] + d[8]
    even_sum = d[1] + d[3] + d[5] + d[7]
    tenth = (odd_sum * 7 - even_sum) % 10
    if tenth != d[9]:
        return False
    eleventh = sum(d[:10]) % 10
    return eleventh == d[10]


def luhn_check(value: str) -> bool:
    """Luhn checksum validation for credit card numbers."""
    digits = [int(c) for c in value if c.isdigit()]
    if not 13 <= len(digits) <= 16:
        return False
    total = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0
