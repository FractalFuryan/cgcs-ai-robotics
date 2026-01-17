# Contributing to CGCS

Thank you for your interest.

CGCS is an ethics-first system. Contributions are welcome **only** if they preserve the core invariants.

---

## Non-Negotiables

**PRs will be rejected if they:**
- Add hidden persistence
- Add network access
- Add inference about mental state
- Remove withdrawal dominance
- Store content instead of indices
- Include secrets or personal identifiers

---

## Core Invariants
- Refusal/withdrawal dominance
- No hidden persistence or memory accumulation
- Memory is index-only and opt-in
- No coercive behavior, nudging, or manipulation
- Deterministic, auditable logic preferred over opaque models

## What We Welcome
- Bug fixes
- Documentation clarity
- Test cases
- Performance or readability improvements
- New roles or guards that *reduce* capability under stress

## What We Will Not Accept
- Features that increase persuasion, retention, or engagement pressure
- Silent logging, profiling, or telemetry
- Emotion inference, diagnosis, or psychological labeling
- Any form of surveillance, scoring, or behavioral optimization

## Process
Open issues for discussion first. Preserve:
- No external dependencies
- No automatic actions
- No content storage (index-only)

## No Secrets Policy

**Do not commit:**
- API keys, tokens, session cookies
- Personal identifiers (names, emails, phone numbers, addresses)
- Raw chat logs or transcripts
- Memory content (only index receipts/handles allowed)
- Local environment paths that reveal identity

**Use instead:**
- `.env` files (gitignored) for local secrets
- `age` or `gpg` for encrypted storage
- `tools/secret_seal.py` for stdlib-only encryption (local protection)
- `tools/provenance_hash.py` for audit hashes

**Pre-commit check:** Grep for common leak patterns:
```bash
git diff --cached | grep -E '(token|api_key|password|@.*\.|BEGIN.*KEY)'
```

By submitting a PR, you agree to uphold the ETHICS-LICENSE and DAVNA Covenant.

Clean hands. Quiet service.
