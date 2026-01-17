# Visual Cipher Legend

Quick-reference guide for file markers and badges used throughout CGCS.

---

## File Classification Markers (Lock Layer)

### 🟢 PUBLIC — Safe for sharing
Files marked with 🟢 contain no secrets and are safe to share publicly.
- Core implementation files
- Documentation
- Architecture descriptions

### 🟡 INDEX-ONLY — No content storage
Files marked with 🟡 handle only indices/handles, never raw content.
- Memory systems use symbols and handles
- No chat logs or personal data stored

### 🟣 SEALED — Protected ethical constraints
Files marked with 🟣 define ethical invariants that must not be violated.
- ETHICS-LICENSE.md
- DAVNA-COVENANT.md

### 🔵 HASHED — Verifiable provenance
Files marked with 🔵 are part of the SHA-256 audit trail.
- PROVENANCE.md
- Release hashes

### 🔴 PROHIBITED — Never commit
Files marked with 🔴 should NEVER be committed to the repository.
- API keys, tokens, credentials
- Personal identifiers
- Raw chat logs
- Local secrets

---

## 💛 Heart Color Layer (Intent & Care Semantics)

> **Rule:** Hearts express *intent, care, and handling posture* — never secrets.  
> They **overlay** the security emojis, not replace them.

### ❤️‍🔥 RED HEART — Critical / Boundary
**Meaning:** Hard limits, non-negotiable constraints  
**Use:** Prohibited areas, "do not cross" logic, invariants  
**Pairs with:** 🔴🚫  
**Example:** `🔴🚫❤️‍🔥 PROHIBITED — Never store identifiers`

### 🧡 ORANGE HEART — Caution / Review
**Meaning:** Sensitive logic; requires extra care or review  
**Use:** Stress thresholds, LoopGuard tuning, decay constants  
**Pairs with:** 🔵🧾  
**Example:** `🔵🧾🧡 VERIFIABLE — Review changes carefully`

### 💛 YELLOW HEART — Care / Human-Centered
**Meaning:** Designed to protect humans first  
**Use:** LoopGuard, de-escalation, grounding options  
**Pairs with:** 🧭🟡  
**Example:** `🟡🧭💛 INDEX-ONLY — Care-first memory cue`

### 💚 GREEN HEART — Safe / Open
**Meaning:** Safe to share, teach, fork  
**Use:** Public docs, examples, role specs  
**Pairs with:** 🟢📖  
**Example:** `🟢📖💚 PUBLIC — Safe for sharing`

### 💙 BLUE HEART — Trust / Integrity
**Meaning:** Integrity, auditability, truthfulness  
**Use:** Provenance, hashes, verification tools  
**Pairs with:** 🔵🧾  
**Example:** `🔵🧾💙 HASHED — Provenance verified`

### 💜 PURPLE HEART — Ethics / Covenant
**Meaning:** Ethical commitments, long-term principles  
**Use:** DAVNA Covenant, Ethics License  
**Pairs with:** 🛡️🔐  
**Example:** `🛡️🔐💜 COVENANT — Ethical constraints apply`

### 🖤 BLACK HEART — Refusal / Exit
**Meaning:** Stop, withdraw, disengage safely  
**Use:** Withdrawal paths, refusal dominance  
**Pairs with:** ⛔  
**Example:** `⛔🖤 WITHDRAWAL — Instant reset`

### 🤍 WHITE HEART — Neutral / Placeholder
**Meaning:** Intentionally empty, undecided, or future  
**Use:** Stubs, TODOs without commitment  
**Example:** `🤍 TODO — Pending design`

---

## 🧩 Combined Example (Full Dual-Layer Label)

```
🟡🧭💛 INDEX-ONLY — Symbol anchor (no content stored)
🔵🧾💙 HASHED — SHA-256 provenance
🛡️🔐💜 COVENANT — DAVNA enforced
```

At a glance:
- 🟡🧭 → *what it does*
- 💛 → *why it exists*
- 🛡️💜 → *ethical guardrails*

---

## 📌 Where to Use

- File headers
- Section titles in docs
- Inline comments near sensitive logic
- Commit messages (optional)
- GitHub README footers/badges

---

## ✅ Benefits of Dual-Layer Coding

- 🧠 **Faster comprehension** — symbol + emotion dual-coding
- 🫂 **Care made explicit** — not just mechanics, but intent
- 🔍 **Auditor-friendly** — see both function and purpose
- 🧘 **Human tone** — without weakening security
- 🧭 **CGCS-aligned** — protection through clarity and refusal

---

## DAVNA Covenant Badge

The 🛡️🧭🔎🧹🌊 badge indicates DAVNA compliance:

- 🛡️ **Deterministic** — no hidden learning
- 🧭 **Autonomous** — consent/withdrawal dominates
- 🔎 **Verifiable** — auditable logic
- 🧹 **Non-hoarding** — index-only, auto-decay
- 🌊 **Anti-trauma-loops** — de-escalate without diagnosis

---

## Usage

**At a glance:** See file headers and badges to instantly understand protection level and compliance status.

**For contributors:** Check markers before modifying files to understand constraints.

**For auditors:** Use markers to quickly identify security-sensitive areas.

---

*The marks are light—labels, not locks.*  
*Symbols name the protection without hiding the content.*
