# 🧭💛 INDEX-ONLY + 📖💚 PUBLIC — CGCS Core
# 🧾💙 HASHED — Provenance available
# 🔐💜 DAVNA COVENANT — Deterministic · Autonomous · Verifiable · Non-hoarding · Anti-loops
# ⛔🖤 REFUSAL-FIRST — Withdrawal clears all state
# 🚫❤️‍🔥 PROHIBITED — No secrets, no identifiers, no raw logs

"""
Consent-Gated Coherence System (CGCS)

A refusal-first coordination framework where agents act through bounded roles,
recover through rest, and remember only by explicit human consent.
"""

from .consent import ConsentManager
from .agent import Agent, Role, RoleType
from .fatigue import FatigueTracker
from .memory import MemoryStore
from .coordinator import Coordinator

__version__ = "0.1.0"
__all__ = [
    "ConsentManager",
    "Agent",
    "Role",
    "RoleType",
    "FatigueTracker",
    "MemoryStore",
    "Coordinator",
]
