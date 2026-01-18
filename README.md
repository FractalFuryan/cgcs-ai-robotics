# CGCS — Consent-Gated Coherence System

**CGCS** is a local-only, ethics-first coordination engine for autonomous robotics. It provides deterministic, refusal-first coordination without hoarding memory, coercing behavior, or creating escalation loops.

Separates **learning** from **remembering**. Makes persistence an explicit, human-controlled choice.

---

## Architecture (L1-L7)

**Complete robotics stack — stdlib-only, zero external dependencies**

| Layer | Component | Purpose |
|-------|-----------|---------|
| **L7** | Mission Specification | High-level objectives and constraints |
| **L6** | Mission Planner | Deterministic role expansion |
| **L5** | Fleet Manager | Multi-agent coordination (no control authority) |
| **L4** | CGCS Core | Consent-gated role management + stress engine |
| **L3** | Loop Guard | Deterministic de-escalation detector |
| **L2** | Dual Memory | Thread decay + opt-in symbol-indexed anchors |
| **L1** | Emoji Protocol | Visual signaling with fail-closed validation |

---

## Core Principles

- **Threads ≠ Memory** — Conversations auto-decay (50-item deque)
- **Symbols = Permission** — Long-term recall requires explicit `[SYM:tag]`
- **Roles are bounded** — Capabilities constrained by mission-specific roles
- **Fatigue accumulates** — Per-role σ ∈ [0,1], threshold-gated de-escalation
- **LoopGuard is deterministic** — Risk = 0.45×repeat + 0.25×rapid + 0.30×intensity
- **Withdrawal dominates** — One action clears all state immediately
- **Fleet coordination ≠ control** — FleetManager cannot override consent

---

## What CGCS Is *Not*

- ❌ No emotion simulation  
- ❌ No psychological diagnosis  
- ❌ No surveillance or profiling  
- ❌ No automatic long-term memory  
- ❌ No cloud services or APIs  

---

## Quick Start

**Core coordination engine:**
```bash
python3 cgcs_core.py
```

**Full stack demo:**
```bash
python3 examples/demo_coordinated_mission.py
```

**Run invariants test suite:**
```bash
python3 invariants.py
```

---

## Repository Structure

**Core Implementation:**
- `cgcs_core.py` — Single-file reference (313 LOC)
- `role_spec.py` — Canonical role definitions (61 LOC)
- `loop_guard.py` — Deterministic escalation detector (127 LOC)
- `emoji_signal.py` — Protocol parser with fail-closed validation (158 LOC)
- `invariants.py` — Formal test harness (99 LOC)

**Robotics Stack:**
- `stack/interfaces.py` — Formal APIs (frozen dataclasses)
- `stack/mission_planner.py` — Stateless role expansion
- `stack/fleet_manager.py` — Multi-agent coordinator

**Tools:**
- `tools/provenance_hash.py` — SHA-256 audit trail generator
- `tools/secret_seal.py` — Stdlib-only encryption (PBKDF2 + HMAC)

**Documentation:**
- `ARCHITECTURE.md` — System design + ASCII flow diagram
- `DAVNA-COVENANT.md` — Ethical invariants (brief)
- `DAVNA-PRINCIPLES.md` — Technical deep-dive (226 LOC)
- `VISUAL-CIPHER.md` — Dual-layer encoding guide (151 LOC)
- `PROVENANCE.md` — SHA-256 hashes for v1.0/v1.1
- `CONTRIBUTING.md` — Non-negotiables + boundaries
- `SECURITY.md` — Local-first constraints

---

## License & Covenant

CGCS is released under a **consent-based ethics license**.  
Use requires preserving invariants and refusing harmful deployment.

See: `DAVNA-COVENANT.md` and `LICENSE.md`

---

## 🛡️🧭🔎🧹🌊 DAVNA-COMPLIANT

- 🛡️ **Deterministic** — outputs depend on visible inputs only
- 🧭 **Autonomous** — consent/withdrawal dominates
- 🔎 **Verifiable** — auditable thresholds and logic
- 🧹 **Non-hoarding** — index-only memory, auto-decay
- 🌊 **Anti-trauma-loops** — de-escalate without diagnosis
