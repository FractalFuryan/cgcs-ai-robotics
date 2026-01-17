# 🟢📖💚 PUBLIC — Safe for sharing
# 🛡️🧭🔎🧹🌊 DAVNA-COMPLIANT
# ======================================================================
# CGCS RoleSpec — Immutable Role Registry
# Roles constrain capability, never expand it
# ======================================================================

from __future__ import annotations
from dataclasses import dataclass
from typing import Set, Dict, Optional

@dataclass(frozen=True)
class RoleSpec:
    """
    Immutable role specification.
    
    Roles are temporary capability constraints, not identity claims.
    """
    name: str
    allowed_actions: Set[str]
    max_load: float  # Maximum stress before forced rotation
    recovery_rate: float  # Per-hour recovery when inactive
    description: str

# Immutable role registry
ROLES: Dict[str, RoleSpec] = {
    "listener": RoleSpec(
        name="listener",
        allowed_actions={"observe", "acknowledge", "reflect"},
        max_load=0.4,
        recovery_rate=0.3,
        description="Receive without advice. Constrained output."
    ),
    "guide": RoleSpec(
        name="guide",
        allowed_actions={"observe", "acknowledge", "suggest", "explain"},
        max_load=0.7,
        recovery_rate=0.2,
        description="Offer options, never commands."
    ),
    "analyst": RoleSpec(
        name="analyst",
        allowed_actions={"observe", "analyze", "structure", "summarize"},
        max_load=0.8,
        recovery_rate=0.15,
        description="Pattern recognition, no interpretation."
    ),
    "rest": RoleSpec(
        name="rest",
        allowed_actions=set(),
        max_load=0.0,
        recovery_rate=0.5,
        description="Full capability withdrawal for recovery."
    )
}

def get_role(name: str) -> Optional[RoleSpec]:
    """Retrieve role by name."""
    return ROLES.get(name)

def list_roles() -> list[str]:
    """List all available role names."""
    return list(ROLES.keys())
