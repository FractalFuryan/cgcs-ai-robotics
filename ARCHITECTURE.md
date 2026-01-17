# CGCS Architecture Overview

## System Flow

```
Context Thread
     │
     ▼
LoopGuard ──► Policy (shorten / still / block anchor)
     │
     ▼
Role System + Stress ──► Advisory signals
     │
     ▼
Response Generation (ephemeral)
     │
     ├─ (optional human mark)
     ▼
Symbol Index (cue → handle, decays)
```

---

## 1. Role System
- Immutable RoleSpec registry
- RoleManager: consent + capacity + exclusivity validation
- Gesture filtering by active role allowances

## 2. Fatigue & Recovery
- Per-role σ_r ∈ [0,1]
- Accumulation only when active
- Full decay when idle (half-life ~17s baseline)
- Advisory levels 1 (soft) / 2 (strong) — options-only

## 3. Dual Memory
- Thread memory: short-term rolling window
- Symbol-anchored index: opt-in long-term, cue recall via set inclusion
- Salience exponential decay + reactivation

## 4. LoopGuard
- Deterministic detection (cue repeat + rapid + intensity proxy)
- De-escalation policy: shorten, still gesture, block anchoring, grounding options

## 5. Care Tuning
- Parameter multipliers for slower/softer/earlier warnings

## Core Principle
No layer may silently increase power.
All escalation paths narrow capability, never widen it.
All components local-only, deterministic, refusal-first.
