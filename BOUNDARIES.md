# Engineering Boundaries

**Last Updated**: January 18, 2026

## What CGCS Does NOT Claim

CGCS (Consent-Gated Coordination System) is an **engineering framework**, not a philosophical statement. It does not claim:

- ❌ **Sentience** — agents have no subjective experience
- ❌ **Consciousness** — no self-awareness or qualia
- ❌ **Moral Agency** — no independent ethical reasoning
- ❌ **Free Will** — decisions follow deterministic rules
- ❌ **Rights** — agents have no legal or moral standing
- ❌ **Suffering** — fatigue is a numerical parameter, not distress

## What CGCS Actually Implements

CGCS provides **deterministic coordination primitives** for multi-agent robotics:

### Core Mechanisms

1. **Consent-Gated Decision Logic**
   - Agents reject tasks outside configured role capacity
   - No external override without local approval
   - Refusal is a valid terminal state

2. **Fatigue-Based Load Shedding**
   - Numerical stress accumulation (σ ∈ [0,1])
   - Automatic task refusal above threshold
   - Linear decay over time

3. **Opt-In Memory Anchoring**
   - Cues require explicit consent to persist
   - No implicit state modification
   - Clear separation: thread (ephemeral) vs anchors (persistent)

4. **Loop Guard Circuit Breaker**
   - Risk metric = 0.45×repeat + 0.25×rapid + 0.30×intensity
   - Hard cutoff at risk ≥ 0.75
   - Prevents runaway oscillations

5. **Role-Based Exclusivity**
   - Mutex on conflicting role pairs
   - Prevents simultaneous incompatible behaviors
   - Examples: (advocate, adversary), (observer, advocate)

## Metaphoric Language Policy

Any language suggesting agency, consciousness, or rights is **explanatory metaphor**, not literal claim:

| Metaphor Used        | Actual Meaning                          |
|---------------------|-----------------------------------------|
| "Agent decides"     | Decision function evaluates constraints |
| "Refuses task"      | Returns rejection code                  |
| "Gets tired"        | Fatigue parameter crosses threshold     |
| "Remembers"         | Data persists in anchor dictionary      |
| "Consents"          | Boolean check passes                    |

## Why This Matters

### Legal Protection
- No implied liability for "autonomous decisions"
- Clear human responsibility chain
- No personhood claims

### Safety Certification
- Deterministic behavior under specification
- Auditable decision traces
- Bounded failure modes

### Ethical Clarity
- No anthropomorphization
- No rights confusion
- Clear tool vs agent distinction

### Research Integrity
- Reproducible results
- Falsifiable claims
- No unfounded speculation

## Advanced Module Clarifications

If this repository includes experimental modules with terms like "quantum," "neuromorphic," or "holographic":

- **"Quantum Decision"** → Multi-hypothesis evaluation with delayed commitment
- **"Neuromorphic Processing"** → Event-based sparse computation patterns
- **"Holographic Memory"** → Distributed feature embeddings with similarity-based recall
- **"Collective Consciousness"** → Aggregated state sharing across agent instances

These are **engineering patterns**, not physics or neuroscience claims.

## Invariant Preservation

The following properties MUST remain true regardless of extensions:

```
INV-01: ∀ cue, consent(cue) = False → cue ∉ anchors
INV-02: ∀ role, capacity(role) < threshold → assign(role) = Refused  
INV-03: ∀ agent, fatigue(agent) ≥ 0.8 → new_tasks(agent) = Empty
INV-04: risk(loop) ≥ 0.75 → interrupt(loop) = True
INV-05: ∀ r1, r2 ∈ exclusivity_pairs, ¬(active(r1) ∧ active(r2))
```

If any extension violates these, **the extension is invalid**, not the invariant.

## Contact for Clarification

If any language in this repository suggests claims beyond these boundaries:
1. File an issue referencing this document
2. Assume engineering interpretation unless proven otherwise
3. Request clarification from maintainers

---

**Bottom Line**: CGCS is a **coordination protocol with consent gates**, not a consciousness experiment. Any language suggesting otherwise is shorthand for deterministic mechanisms described herein.
