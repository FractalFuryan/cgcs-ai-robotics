# emoji_signal.py
# 🤖🔐 Emoji–Color Signaling Protocol — Reference Parser + Validator
# Deterministic • Audit-safe • No inference • No hidden state

from __future__ import annotations
from dataclasses import dataclass
from typing import FrozenSet, List, Optional, Tuple, Dict

# -----------------------------
# Spec: Color (Intent Layer)
# -----------------------------
COLOR_INTENTS: Dict[str, str] = {
    "🟢": "FLOW",
    "⚫": "BOUNDARY",
    "🟣": "COHERENCE",
    "🔴": "ALERT",
    "🟡": "ATTENTION",
    "🔵": "COMMUNICATION",
    "🟠": "CREATIVE",
}

# -----------------------------
# Spec: Emoji Tokens (Semantic Layer)
# Keep this table small + explicit.
# Unknown tokens => reject (no guessing).
# -----------------------------
TOKENS: Dict[str, str] = {
    "⚙️": "SYSTEM",
    "🔒": "CONSTRAINT",
    "❤️": "CONSENT_CARE",
    "⚠️": "WARNING",
    "✅": "VALIDATION_PASS",
    "❌": "VALIDATION_FAIL",
    "🌀": "RECURSION",
    "📡": "SIGNAL_TX",
    "💾": "MEMORY_ARCHIVE",
}

# -----------------------------
# Grammar limits
# -----------------------------
MAX_TOKENS = 5  # after the color
ALLOW_EMPTY_TOKENS = True  # color alone is allowed

# -----------------------------
# Intent consistency rules (examples)
# "care cannot be forced" => disallow ALERT + CONSENT_CARE
# add more rules here as needed
# -----------------------------
FORBIDDEN_COMBOS: FrozenSet[Tuple[str, str]] = frozenset({
    ("🔴", "❤️"),  # ALERT with CONSENT/Care token
})

# Some emoji appear in variant forms; normalize what we can deterministically.
# NOTE: This is intentionally minimal. If you add new tokens, add them explicitly above.
NORMALIZE = {
    "♥️": "❤️",
}

@dataclass(frozen=True)
class Signal:
    raw: str
    color: str
    intent: str
    tokens: Tuple[str, ...]
    token_meanings: Tuple[str, ...]

@dataclass(frozen=True)
class ParseError:
    code: str
    message: str

def _normalize(raw: str) -> str:
    s = raw.strip()
    for k, v in NORMALIZE.items():
        s = s.replace(k, v)
    return s

def parse_signal(raw: str) -> Tuple[Optional[Signal], Optional[ParseError]]:
    """
    Parse and validate a signal string like: '🟢⚙️✅'
    Deterministic:
      - Color must be first and exactly one
      - Tokens must be from TOKENS
      - <= MAX_TOKENS tokens
      - Forbidden combos rejected
    """
    if raw is None:
        return None, ParseError("EMPTY", "Signal is None")

    s = _normalize(raw)
    if not s:
        return None, ParseError("EMPTY", "Signal is empty")

    # First grapheme must be a known color.
    # We keep this strict: color must be the first character in string.
    color = s[0]
    if color not in COLOR_INTENTS:
        return None, ParseError("BAD_COLOR", f"Unknown or missing color prefix: {repr(color)}")

    # Extract tokens by scanning for known token strings.
    rest = s[1:]
    tokens: List[str] = []

    i = 0
    # Sort token keys by length desc to avoid partial matching issues.
    token_keys = sorted(TOKENS.keys(), key=len, reverse=True)

    while i < len(rest):
        matched = False
        for tk in token_keys:
            if rest.startswith(tk, i):
                tokens.append(tk)
                i += len(tk)
                matched = True
                break
        if not matched:
            # If we hit whitespace, skip it (allow '🟢 ⚙️ ✅' style)
            if rest[i].isspace():
                i += 1
                continue
            # Unknown char/token => reject (no guessing)
            snippet = rest[i:i+8]
            return None, ParseError("BAD_TOKEN", f"Unknown token near: {repr(snippet)}")

    if not tokens and not ALLOW_EMPTY_TOKENS:
        return None, ParseError("NO_TOKENS", "Signal must contain at least one token")

    if len(tokens) > MAX_TOKENS:
        return None, ParseError("TOO_LONG", f"Too many tokens: {len(tokens)} (max {MAX_TOKENS})")

    # Intent consistency rules
    for tk in tokens:
        if (color, tk) in FORBIDDEN_COMBOS:
            return None, ParseError("FORBIDDEN_COMBO", f"Forbidden combo: {color}+{tk}")

    meanings = tuple(TOKENS[tk] for tk in tokens)
    sig = Signal(
        raw=s,
        color=color,
        intent=COLOR_INTENTS[color],
        tokens=tuple(tokens),
        token_meanings=meanings,
    )
    return sig, None

def pretty(sig: Signal) -> str:
    parts = [f"{sig.color} ({sig.intent})"]
    for t, m in zip(sig.tokens, sig.token_meanings):
        parts.append(f"  - {t} = {m}")
    return "\n".join(parts)
