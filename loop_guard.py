# 🟢📖💚 PUBLIC — Safe for sharing
# 🛡️🧭🔎🧹🌊💛 DAVNA-COMPLIANT — Care-first de-escalation
# ======================================================================
# CGCS LoopGuard — Standalone Module
# Deterministic escalation detection and de-escalation policy
# ======================================================================

from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from typing import Set
import time, re

# Helpers
_WORD_RE = re.compile(r"[A-Za-z0-9_']+")

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def simple_intensity(text: str) -> float:
    """Estimate intensity from capitalization, punctuation, length."""
    if not text: return 0.0
    letters = [c for c in text if c.isalpha()]
    if not letters: return 0.0
    cap_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    bangs = text.count("!") + text.count("?")
    bang_score = min(1.0, bangs / 6.0)
    length_score = min(1.0, len(text) / 400.0)
    return clamp01(0.55 * cap_ratio + 0.30 * bang_score + 0.15 * length_score)

def cue_key(symbols: Set[str], text: str) -> str:
    """Generate a stable key for repetition tracking."""
    if symbols:
        return "S:" + ",".join(sorted(symbols))
    words = _WORD_RE.findall(text.lower())[:6]
    return "W:" + " ".join(words)

@dataclass
class LoopEvent:
    t: float
    key: str
    intensity: float

class LoopGuard:
    """
    Detects repetitive escalation patterns and enforces de-escalation policies.
    
    No diagnosis, no psychological labeling—purely structural intervention.
    """
    def __init__(self, window_s: int = 120, cooldown_s: int = 90):
        self.window_s = window_s
        self.cooldown_s = cooldown_s
        self.events: deque[LoopEvent] = deque(maxlen=128)
        self.cooldown_until: float = 0.0
        self.last_reason: str = ""

    def observe(self, text: str, symbols: Set[str] = None, now: float = None) -> dict:
        """
        Observe incoming text and compute risk score.
        
        Returns:
            {
                "risk": float [0,1],
                "mode": "normal" | "deescalate",
                "reason": str
            }
        """
        now = now or time.time()
        symbols = symbols or set()
        k = cue_key(symbols, text)
        inten = simple_intensity(text)
        
        # Sliding window
        cutoff = now - self.window_s
        while self.events and self.events[0].t < cutoff:
            self.events.popleft()
        
        self.events.append(LoopEvent(now, k, inten))
        
        # Count repetitions
        same = [e for e in self.events if e.key == k]
        repeats = len(same)
        
        # Rapid repetition score
        rapid = 0.0
        if repeats >= 2:
            dt = same[-1].t - same[-2].t
            rapid = max(0.0, 1.0 - dt / 60.0)
        
        # Composite risk
        repeat_score = clamp01((repeats - 1) / 3.0)
        intensity_score = clamp01(inten / 0.55)
        risk = clamp01(0.45 * repeat_score + 0.25 * rapid + 0.30 * intensity_score)
        
        # Cooldown enforcement
        if now < self.cooldown_until:
            return {"risk": max(risk, 0.6), "mode": "deescalate", "reason": self.last_reason}
        
        # Trigger threshold
        if risk >= 0.75:
            self.cooldown_until = now + self.cooldown_s
            self.last_reason = f"repeats={repeats} rapid={rapid:.2f} inten={inten:.2f}"
            return {"risk": risk, "mode": "deescalate", "reason": self.last_reason}
        
        return {"risk": risk, "mode": "normal", "reason": ""}

    def policy(self, mode: str) -> dict:
        """
        Return constraints for the given mode.
        
        De-escalation mode narrows capability:
        - Shorter responses
        - Grounding tone
        - No memory anchoring
        - Forced gesture
        """
        if mode == "deescalate":
            return {
                "max_chars": 550,
                "force_gesture": "hold_still_visible",
                "allow_anchor": False,
                "tone": "grounding"
            }
        return {
            "max_chars": 1400,
            "force_gesture": None,
            "allow_anchor": True,
            "tone": "neutral"
        }
