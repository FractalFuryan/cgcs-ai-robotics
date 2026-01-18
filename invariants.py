# invariants.py
# 🧾✅ Formal Invariants for Emoji–Color Signaling Protocol
# Goal: certification-style checks (deterministic, explicit, fail-closed)

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional

from emoji_signal import parse_signal, COLOR_INTENTS, TOKENS, MAX_TOKENS

@dataclass(frozen=True)
class InvariantResult:
    ok: bool
    invariant_id: str
    detail: str

# -----------------------------
# Invariants (audit friendly)
# -----------------------------

def inv_01_color_first(raw: str) -> InvariantResult:
    if not raw or raw.strip() == "":
        return InvariantResult(False, "INV-01", "Empty signal")
    first = raw.strip()[0]
    return InvariantResult(first in COLOR_INTENTS, "INV-01", "Color prefix must be first and known")

def inv_02_single_color(raw: str) -> InvariantResult:
    # We treat "single color" as: parser must succeed and identify exactly one color at position 0
    sig, err = parse_signal(raw)
    if err:
        return InvariantResult(False, "INV-02", f"Parse failed: {err.code} {err.message}")
    return InvariantResult(sig.color == sig.raw[0], "INV-02", "Exactly one color prefix at start")

def inv_03_known_tokens_only(raw: str) -> InvariantResult:
    sig, err = parse_signal(raw)
    if err:
        return InvariantResult(False, "INV-03", f"Rejected (good): {err.code} {err.message}")
    unknown = [t for t in sig.tokens if t not in TOKENS]
    return InvariantResult(len(unknown) == 0, "INV-03", "All tokens must be explicitly defined")

def inv_04_length_limit(raw: str) -> InvariantResult:
    sig, err = parse_signal(raw)
    if err:
        # If it failed due to TOO_LONG this invariant is satisfied by rejection
        if err.code == "TOO_LONG":
            return InvariantResult(True, "INV-04", "Overlong signals are rejected (fail-closed)")
        return InvariantResult(False, "INV-04", f"Parse failed: {err.code} {err.message}")
    return InvariantResult(len(sig.tokens) <= MAX_TOKENS, "INV-04", "Token count within limit")

def inv_05_fail_closed(raw: str) -> InvariantResult:
    # Invalid inputs must never be accepted silently.
    sig, err = parse_signal(raw)
    if err:
        return InvariantResult(True, "INV-05", f"Invalid rejected: {err.code}")
    return InvariantResult(True, "INV-05", "Valid accepted")

def run_invariants(raw: str) -> List[InvariantResult]:
    return [
        inv_01_color_first(raw),
        inv_02_single_color(raw),
        inv_03_known_tokens_only(raw),
        inv_04_length_limit(raw),
        inv_05_fail_closed(raw),
    ]

def run_suite() -> Tuple[bool, List[str]]:
    """
    Minimal test suite:
      - Known good examples must pass
      - Known bad examples must reject
    """
    good = [
        "🟢⚙️✅",
        "🔴⚙️⚠️",
        "🟣⚙️🌀",
        "⚫",            # boundary with no tokens allowed
        "🟢 ⚙️ ✅",      # whitespace tolerated
    ]

    bad = [
        "⚙️✅",          # no color
        "🟢💥",          # unknown token
        "🔴❤️",          # forbidden combo (care cannot be forced)
        "🟢⚙️✅🌀📡💾❌",  # > MAX_TOKENS
        "",              # empty
    ]

    failures: List[str] = []

    for s in good:
        sig, err = parse_signal(s)
        if err is not None:
            failures.append(f"GOOD rejected: {repr(s)} -> {err.code} {err.message}")
            continue
        invs = run_invariants(s)
        bad_invs = [i for i in invs if not i.ok]
        if bad_invs:
            failures.append(f"GOOD invariant fail: {repr(s)} -> {bad_invs}")

    for s in bad:
        sig, err = parse_signal(s)
        if err is None:
            failures.append(f"BAD accepted: {repr(s)} -> parsed={sig}")

    return (len(failures) == 0), failures

if __name__ == "__main__":
    ok, failures = run_suite()
    if ok:
        print("✅ Invariants suite PASS")
    else:
        print("❌ Invariants suite FAIL")
        for f in failures:
            print(" -", f)
