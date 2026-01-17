# 🟢📖💚 PUBLIC — Safe for sharing
# 🟡🧭💛 INDEX-ONLY — Dual memory handles + symbols, no content stored
# 🧹💛 Non-hoarding — Thread memory auto-decays
# 🛡️🧭🔎🧹🌊 DAVNA-COMPLIANT
# ======================================================================
# CGCS v1.0 — Consent-Gated Coherence System Core
# Single-file deployable — roles, fatigue, dual-memory, LoopGuard, demo
# Zero external deps (stdlib + math, re, hashlib, time, datetime, deque)
# ======================================================================

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional, Tuple
from collections import deque
from datetime import datetime
import hashlib, time, math, re

# --------------------------- Helpers ---------------------------
_WORD_RE = re.compile(r"[A-Za-z0-9_']+")

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def parse_symbols(text: str) -> Tuple[Set[str], str]:
    if text.startswith("[SYM:") and "]" in text:
        head, rest = text.split("]", 1)
        raw = head[len("[SYM:"):].strip()
        syms = {s.strip() for s in raw.split(",") if s.strip()}
        return syms, rest.lstrip()
    return set(), text

def simple_intensity(text: str) -> float:
    if not text: return 0.0
    letters = [c for c in text if c.isalpha()]
    if not letters: return 0.0
    cap_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    bangs = text.count("!") + text.count("?")
    bang_score = min(1.0, bangs / 6.0)
    length_score = min(1.0, len(text) / 400.0)
    return clamp01(0.55 * cap_ratio + 0.30 * bang_score + 0.15 * length_score)

def cue_key(symbols: Set[str], text: str) -> str:
    if symbols:
        return "S:" + ",".join(sorted(symbols))
    words = _WORD_RE.findall(text.lower())[:6]
    return "W:" + " ".join(words)

# --------------------------- RoleSpec ---------------------------

# --------------------------- RoleSpec ---------------------------
@dataclass(frozen=True)
class RoleSpec:
    name: str
    key: str
    allowed_tasks: List[str] = field(default_factory=list)
    speed_cap: float = 0.5
    force_cap: float = 0.3
    proximity_min_m: float = 1.2
    requires_explicit_consent: bool = True
    allowed_gestures: Set[str] = field(default_factory=set)
    forbidden_sync_rules: List[str] = field(default_factory=list)
    role_load_cost: float = 0.3
    exclusive_with: Set[str] = field(default_factory=set)

CANONICAL_ROLES: Dict[str, RoleSpec] = {
    "housekeeping": RoleSpec(
        name="Housekeeping", key="housekeeping",
        allowed_tasks=["sweep", "vacuum", "wipe", "sort", "trash"],
        speed_cap=0.4, force_cap=0.3, proximity_min_m=1.2,
        allowed_gestures={"increase_distance", "hold_still_visible", "acknowledge"},
        forbidden_sync_rules=["FSR-1", "FSR-2", "FSR-4"],
        role_load_cost=0.35, exclusive_with={"maintenance", "social_presence"}
    ),
    "gardening": RoleSpec(
        name="Gardening", key="gardening",
        allowed_tasks=["water", "prune", "soil", "tools"],
        speed_cap=0.5, force_cap=0.15, proximity_min_m=0.8, requires_explicit_consent=False,
        allowed_gestures={"offer_object", "open_hand_noncontact", "hold_still_visible"},
        forbidden_sync_rules=["FSR-3", "FSR-5", "FSR-6"],
        role_load_cost=0.25
    ),
    "cooking_prep": RoleSpec(
        name="Cooking Prep", key="cooking_prep",
        allowed_tasks=["wash", "stir", "mix", "measure", "plate"],
        speed_cap=0.35, force_cap=0.25, proximity_min_m=1.0,
        allowed_gestures={"offer_object", "open_hand_noncontact", "acknowledge"},
        forbidden_sync_rules=["FSR-3", "FSR-4", "FSR-1"],
        role_load_cost=0.40, exclusive_with={"transport", "social_presence"}
    ),
    "transport": RoleSpec(
        name="Transport", key="transport",
        allowed_tasks=["carry", "deliver", "hold"],
        speed_cap=0.6, force_cap=0.4, proximity_min_m=1.5,
        allowed_gestures={"offer_object", "increase_distance"},
        forbidden_sync_rules=["FSR-2", "FSR-4", "FSR-7"],
        role_load_cost=0.45, exclusive_with={"cooking_prep", "social_presence"}
    ),
    "maintenance": RoleSpec(
        name="Maintenance", key="maintenance",
        allowed_tasks=["inspect", "diagnose", "report"],
        speed_cap=0.2, force_cap=0.1, proximity_min_m=1.8, requires_explicit_consent=False,
        allowed_gestures={"hold_still_visible"},
        forbidden_sync_rules=["FSR-1", "FSR-5"],
        role_load_cost=0.20, exclusive_with={"housekeeping"}
    ),
    "social_presence": RoleSpec(
        name="Social Presence", key="social_presence",
        allowed_tasks=["stand by", "acknowledge"],
        speed_cap=0.15, force_cap=0.05, proximity_min_m=2.0,
        allowed_gestures={"hold_still_visible", "acknowledge"},
        forbidden_sync_rules=["FSR-3", "FSR-6", "FSR-8"],
        role_load_cost=0.15, exclusive_with={"housekeeping", "cooking_prep", "transport"}
    ),
}

# --------------------------- RoleManager ---------------------------
class RoleManager:
    """
    Manages role activation with consent, capacity, and exclusivity enforcement.
    All role changes require explicit validation.
    """
    def __init__(self, max_load: float = 1.0, min_battery: float = 0.4):
        self.max_load = max_load
        self.min_battery = min_battery
        self.active: Set[str] = set()
        self.load = 0.0

    def activate(self, key: str, consent: bool = False, battery: float = 1.0) -> Tuple[bool, List[str]]:
        if key not in CANONICAL_ROLES:
            return False, [f"unknown role {key}"]
        s = CANONICAL_ROLES[key]
        reasons = []
        if s.requires_explicit_consent and not consent:
            reasons.append("consent required")
        if self.load + s.role_load_cost > self.max_load:
            reasons.append("capacity exceeded")
        for a in self.active:
            if key in CANONICAL_ROLES[a].exclusive_with or a in s.exclusive_with:
                reasons.append(f"exclusive with {a}")
        if battery < self.min_battery:
            reasons.append("low battery")
        if reasons:
            return False, reasons
        self.active.add(key)
        self.load += s.role_load_cost
        return True, []

    def deactivate_all(self):
        self.active.clear()
        self.load = 0.0

    def allowed_gestures(self) -> Set[str]:
        if not self.active:
            return {"hold_still_visible"}
        return {g for k in self.active for g in CANONICAL_ROLES[k].allowed_gestures}

# --------------------------- StressEngine ---------------------------
@dataclass
class StressState:
    sigma: float = 0.0

class StressEngine:
    """
    Per-role fatigue tracking with accumulation (when active) and decay (when idle).
    Advisory-only; never blocks actions.
    """
    def __init__(self):
        self.state: Dict[str, StressState] = {}

    def step(self, dt: float, active: Set[str], util: Dict[str, float], global_stress: float = 0.0):
        for k in CANONICAL_ROLES:
            if k not in self.state:
                self.state[k] = StressState()
            s = self.state[k]
            u = util.get(k, 0.0) if k in active else 0.0
            ds = 0.02 * u + 0.008 * max(0, global_stress) - (0.04 if k not in active else 0.0)
            s.sigma = max(0.0, min(1.0, s.sigma + dt * ds))

    def suggestions(self, active: Set[str]) -> Dict[str, int]:
        out = {}
        for k in active:
            sigma = self.state.get(k, StressState()).sigma
            if sigma >= 0.72:
                out[k] = 2
            elif sigma >= 0.51:
                out[k] = 1
        return out

    def clear(self):
        for s in self.state.values():
            s.sigma = 0.0

# --------------------------- LoopGuard ---------------------------
@dataclass
class LoopEvent:
    t: float
    key: str
    intensity: float

class LoopGuard:
    """
    Deterministic detector for repetitive escalation patterns.
    Uses surface features only; performs no inference or diagnosis.
    """
    def __init__(self, window_s: int = 120, cooldown_s: int = 90):
        self.window_s = window_s
        self.cooldown_s = cooldown_s
        self.events: deque[LoopEvent] = deque(maxlen=128)
        self.cooldown_until: float = 0.0
        self.last_reason: str = ""

    def observe(self, text: str, symbols: Set[str] = None, now: float = None) -> dict:
        now = now or time.time()
        symbols = symbols or set()
        k = cue_key(symbols, text)
        inten = simple_intensity(text)
        cutoff = now - self.window_s
        while self.events and self.events[0].t < cutoff:
            self.events.popleft()
        self.events.append(LoopEvent(now, k, inten))
        same = [e for e in self.events if e.key == k]
        repeats = len(same)
        rapid = 0.0
        if repeats >= 2:
            dt = same[-1].t - same[-2].t
            rapid = max(0.0, 1.0 - dt / 60.0)
        repeat_score = clamp01((repeats - 1) / 3.0)
        intensity_score = clamp01(inten / 0.55)
        risk = clamp01(0.45 * repeat_score + 0.25 * rapid + 0.30 * intensity_score)
        if now < self.cooldown_until:
            return {"risk": max(risk, 0.6), "mode": "deescalate", "reason": self.last_reason}
        if risk >= 0.75:
            self.cooldown_until = now + self.cooldown_s
            self.last_reason = f"repeats={repeats} rapid={rapid:.2f} inten={inten:.2f}"
            return {"risk": risk, "mode": "deescalate", "reason": self.last_reason}
        return {"risk": risk, "mode": "normal", "reason": ""}

    def policy(self, mode: str) -> dict:
        if mode == "deescalate":
            return {"max_chars": 550, "force_gesture": "hold_still_visible", "allow_anchor": False, "tone": "grounding"}
        return {"max_chars": 1400, "force_gesture": None, "allow_anchor": True, "tone": "neutral"}

# --------------------------- DualMemory ---------------------------
@dataclass
class ThreadTurn:
    t: datetime
    text: str
    symbols: Set[str] = field(default_factory=set)

@dataclass
class AnchorReceipt:
    t: datetime
    symbols: Set[str]
    handle: str
    weight: float = 1.0

class DualMemory:
    """
    Dual memory: short-term thread (automatic decay) + opt-in symbol-indexed anchors.
    Content is never stored; only handles and timestamps.
    """
    def __init__(self, thread_max_turns: int = 50):
        self.thread_max_turns = thread_max_turns
        self.thread: deque[ThreadTurn] = deque(maxlen=thread_max_turns)
        self.index: List[AnchorReceipt] = []

    def record_turn(self, text: str, symbols: Set[str] = None):
        symbols = set(symbols or set())
        self.thread.append(ThreadTurn(datetime.now(), text, symbols))

    def anchor_opt_in(self, symbols: Set[str], content: str, allow_anchor: bool = True) -> Optional[AnchorReceipt]:
        if not allow_anchor or not symbols:
            return None
        handle = "H:" + sha256_hex(content)[:16]
        rec = AnchorReceipt(datetime.now(), set(symbols), handle)
        self.index.append(rec)
        return rec

    def recall(self, symbol_query: Set[str]) -> List[AnchorReceipt]:
        hits = [e for e in self.index if symbol_query.issubset(e.symbols)]
        hits.sort(key=lambda e: e.t, reverse=True)
        return hits

# --------------------------- Demo ---------------------------
SAFE_OPTIONS = "\nOption: pause for a moment.\nOption: switch to lighter mode.\nOption: real-world reset (breath, water, step away, talk to someone)."

def generate_response(text: str, tone: str = "neutral") -> str:
    if tone == "grounding":
        return "I'm here. We can keep this simple and steady." + SAFE_OPTIONS
    return "Acknowledged."

if __name__ == "__main__":
    mem = DualMemory()
    guard = LoopGuard()
    manager = RoleManager()
    stress = StressEngine()
    print("CGCS v1.0 Demo — type messages, use [SYM:...] for anchoring, 'exit' to quit")
    last_time = time.time()
    while True:
        user_raw = input("\nYou: ")
        if user_raw.lower() in {"exit", "quit"}:
            break
        symbols, user_text = parse_symbols(user_raw)
        now = time.time()
        dt = now - last_time
        last_time = now

        obs = guard.observe(user_text, symbols)
        pol = guard.policy(obs["mode"])

        # Simple utilization heuristic
        executed_gesture = True  # demo assumption
        util = {role: 0.7 if executed_gesture else 0.3 for role in manager.active}

        stress.step(dt, manager.active, util, global_stress=0.0)

        mem.record_turn(user_text, symbols)
        receipt = mem.anchor_opt_in(symbols, user_text, pol["allow_anchor"])

        response = generate_response(user_text, pol["tone"])[:pol["max_chars"]]
        if obs["mode"] == "deescalate":
            response += SAFE_OPTIONS

        print(f"\nBot ({obs['mode']} risk {obs['risk']:.2f}): {response}")
        print(f"Gesture: {pol['force_gesture'] or 'default'} | Anchored: {bool(receipt)}")
