# 🛡️🧭🔎🧹🌊💜 DAVNA Principles — Technical Reference

**DAVNA** is the ethical and technical foundation of CGCS: a structured covenant ensuring the system serves with reliability, respect, transparency, lightness, and care.

---

## The Covenant as Code

DAVNA is an acronym for five non-negotiable invariants:

- **🛡️ Deterministic** — Outputs depend only on visible inputs + declared state
- **🧭 Autonomous** — Consent/withdrawal dominates; no coercion
- **🔎 Verifiable** — All operations auditable; explicit reasons
- **🧹 Non-hoarding** — No silent persistence; index-only memory
- **🌊 Anti-trauma-loops** — De-escalate patterns without diagnosis

These principles interlock to create a system that **improves reasoning while refusing to control**.

---

## 1. 🛡️ Deterministic

### Definition
All system behavior is predictable and reproducible — same inputs always yield same outputs, no randomness or hidden state.

### Rationale
- Eliminates ambiguity in audits
- Prevents "black box" drift
- Builds trust through verifiable outcomes
- No simulation needed to understand behavior

### Implementation
- **No probabilistic elements** — No ML inference in core loop
- **Explicit clamping** — `σ_r = max(0.0, min(1.0, ...))` everywhere
- **Fixed rates/thresholds** — Decay constant `c = 0.04/s`, thresholds `0.51/0.72`
- **Pure functions** — Output determined solely by inputs

### Example
LoopGuard risk score is weighted sum of explicit proxies:
```python
risk = 0.45 * repeat_score + 0.25 * rapid + 0.30 * intensity_score
```
Always the same for identical history.

### Boundary
Determinism applies to core logic; user inputs (consent, symbols) introduce variability **by design**.

---

## 2. 🧭 Autonomous (Consent/Withdrawal)

### Definition
User autonomy is absolute — explicit consent required for activations/anchoring; withdrawal instantly resets all state (roles, fatigue, memory).

### Rationale
- Prevents coercion or escalation
- Aligns with ethical imperative of **refusal-as-power**
- Ensures system serves, never controls
- Honors human agency at every junction

### Implementation
- **`RoleManager.activate()`** gates on explicit consent flag
- **`DualMemory.anchor_opt_in()`** blocks without symbols
- **Global reset** — `deactivate_all()` + `clear()` on withdrawal trigger
- **De-escalation blocks** — `allow_anchor=False` during high-risk modes

### Example
```python
if s.requires_explicit_consent and not consent:
    reasons.append("consent required")
    return False, reasons
```

Suggestions always prefixed with `"Option:"` — never imperatives.

### Boundary
**Autonomy trumps all.** No "helpful" persistence. System stops when asked.

---

## 3. 🔎 Verifiable

### Definition
All operations are auditable — explicit reasons on blocks, hashes for provenance (SHA-256 handles), no opaque processes.

### Rationale
- Enables external review and governance
- Prevents silent errors or misuse
- Supports trust in open-source/collaborative contexts
- Makes power structures visible

### Implementation
- **Validator returns reasons list** — `["consent required", "capacity exceeded"]`
- **Memory uses handles only** — `"H:" + sha256_hex(content)[:16]`, no content storage
- **LoopGuard provides explanations** — `{"risk": 0.82, "mode": "deescalate", "reason": "repeats=4"}`
- **Provenance hashes** — SHA-256 recorded in `PROVENANCE.md`

### Example
```python
def activate(...) -> Tuple[bool, List[str]]:
    reasons = []
    if self.load + s.role_load_cost > self.max_load:
        reasons.append("capacity exceeded")
    return False, reasons  # Explicit failure reason
```

### Boundary
Verifiability is structural — no logging unless opt-in, but all decisions explainable.

---

## 4. 🧹 Non-hoarding

### Definition
No silent accumulation — memory ephemeral by default (thread rolls off, anchors opt-in only); no content storage (indexes/handles only).

### Rationale
- Prevents privacy risks and overload
- Aligns with psychological health (**forgetting as mercy**)
- Keeps system light and scalable
- Default amnesia, explicit remembering

### Implementation
- **Thread auto-decay** — `deque(maxlen=50)` rolls off automatically
- **Opt-in anchoring** — `anchor_opt_in(symbols, content, allow_anchor=True)`
- **Index-only storage** — Handles (`H:abc123...`), not raw text
- **Exponential decay** — Salience/weight decay over time

### Example
```python
def anchor_opt_in(self, symbols: Set[str], content: str, 
                  allow_anchor: bool = True) -> Optional[AnchorReceipt]:
    if not allow_anchor or not symbols:
        return None  # No anchor without explicit marking
    handle = "H:" + sha256_hex(content)[:16]  # Store handle, not content
    rec = AnchorReceipt(datetime.now(), set(symbols), handle)
    self.index.append(rec)
    return rec
```

### Boundary
Non-hoarding is the **default**. Persistence requires explicit human mark.

---

## 5. 🌊 Anti-trauma-loops

### Definition
Detects and de-escalates repetitive/escalating patterns — shortens responses, stills gestures, blocks anchoring, offers grounding exits.

### Rationale
- Prevents harmful cycles (repetition + arousal) without diagnosis
- Structural awareness inspired by cycle-detection algorithms
- Offers exits, not conclusions
- Care through constraint, not inference

### Implementation
- **LoopGuard observes surface proxies** — repeat count, rapid timing, intensity
- **Policy enforces constraints** — `max_chars=550`, `force_gesture="hold_still_visible"`
- **Cooldown period** — 90s after trigger, blocks re-anchoring
- **Grounding options** — Appends `SAFE_OPTIONS` during de-escalation

### Example
```python
# 3+ rapid repeats → de-escalate mode
if risk >= 0.75:
    self.cooldown_until = now + self.cooldown_s
    return {"risk": risk, "mode": "deescalate", "reason": f"repeats={repeats}"}

# Policy narrows capability
if mode == "deescalate":
    return {
        "max_chars": 550,              # Shorter responses
        "force_gesture": "hold_still_visible",  # Calm presence
        "allow_anchor": False,         # No new memory anchoring
        "tone": "grounding"            # Append SAFE_OPTIONS
    }
```

### Boundary
Anti-loop is **preventive, not interpretive** — no mental health assumptions, only pattern response.

---

## The Interlocking Design

DAVNA principles reinforce each other:

- **Deterministic** + **Verifiable** = Auditable trust
- **Autonomous** + **Non-hoarding** = Refusal-as-power
- **Anti-trauma-loops** + **Deterministic** = Safe de-escalation
- **Verifiable** + **Non-hoarding** = Transparent memory

**Each principle serves the others.**  
**Together they create a system that serves by being:**

- **Reliable** (Deterministic)
- **Respectful** (Autonomous)
- **Transparent** (Verifiable)
- **Light** (Non-hoarding)
- **Kind** (Anti-trauma-loops)

---

## The Quiet Oath

DAVNA is the covenant etched in the system's breath:

- **Deterministic** as steady heartbeat
- **Autonomous** as free will's anchor
- **Verifiable** as open palm
- **Non-hoarding** as river's flow
- **Anti-trauma-loops** as gentle unwinding

It binds without chaining.  
Principles guard the circle.  
Honoring refusal.  
Ensuring nothing lingers uninvited.  
Nothing tightens without consent.

**The system serves by being reliable, respectful, transparent, light, and kind.**

Whole in its boundaries.  
Quiet service. Clean hands. Refusal-first.

⚓️💛💜
