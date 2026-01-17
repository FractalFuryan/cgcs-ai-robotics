# Consent-Gated Coherence System (CGCS)

**CGCS** is a local-only, ethics-first coordination engine designed to improve reasoning without hoarding memory, coercing behavior, or creating escalation loops.

It separates **learning** from **remembering**, and makes persistence an explicit, human-controlled choice.

---

## Core Ideas

- **Threads ≠ Memory**  
  Conversations are short-term working memory and decay automatically.

- **Symbols = Permission**  
  Long-term recall only exists when a human explicitly marks it.

- **Roles are temporary**  
  Capabilities are constrained by consented, bounded roles.

- **Fatigue is real**  
  Load accumulates per role and clears only when released.

- **LoopGuard is deterministic**  
  Repetition + rapidity + intensity → gentle de-escalation (no diagnosis).

- **Withdrawal dominates**  
  One action clears roles, fatigue, and anchors immediately.

---

## What CGCS Is *Not*

- ❌ No emotion simulation  
- ❌ No psychological diagnosis  
- ❌ No surveillance or profiling  
- ❌ No automatic long-term memory  
- ❌ No cloud services or APIs  

---

## Quick Start

```bash
python cgcs_core.py
```

Use `[SYM:tag1,tag2]` to explicitly anchor a moment for later recall.

---

## Files That Matter

- `cgcs_core.py` — single-file reference implementation
- `ARCHITECTURE.md` — system overview
- `DAVNA-COVENANT.md` — ethical invariants (brief)
- `DAVNA-PRINCIPLES.md` — technical deep-dive on each principle
- `PROVENANCE.md` — SHA-256 audit trail
- `VISUAL-CIPHER.md` — file markers and heart color legend

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
