# 🔵🧾💙 Provenance (CGCS v1.0)

This repo is designed to be auditable.  
We publish SHA-256 hashes of key files at release time.

## How to Verify

Run:
```bash
python tools/provenance_hash.py
```

Record the printed hashes below per release tag.

## Release: v1.0.0

```
cgcs_core.py:       d14906f9626a4201ec80a2cf6198dcbcf147b084d6048a2a04840b55b08d50f3
loop_guard.py:      58cc8c64ded62a2c5e2cb65ae5a629f55c91d5bbabac7c69467a075405860818
role_spec.py:       47cff47ac163f37a79bfe62c9af97503ee3cc611daed13dc6279e8e677cd8d67
emoji_signal.py:    86eae345f8f8e04e3f39d5627879b0aae28c437e938d6583acdc8a3a061b0c03
invariants.py:      055f97ee7c9d8f12ba094ef01916eac49a0abff9b4903416f3646c7ab559779e
DAVNA-COVENANT.md:  7de4c41a54dce9fb07235f8b598af7c24b79b79bcb279a92c21ac49ac8bc32a6
ETHICS-LICENSE.md:  5e6a1da72e394544a26bb202d447889ff215b3aa6b4723e735f0f0310a19708d
README.md:          a1ae3ef8bc8936273d3f5aee10bfea083db6013c15471382c1981ae751f74a7d
ARCHITECTURE.md:    12f8bdbde829111083262329b3e878310451d18f6ef17a4a6cada673e555f209
CONTRIBUTING.md:    9ea3f99fb2c8be3bd648c2b9da9fc7ef037317dbaae0dcc2294ceb332761d1a5
SECURITY.md:        8d1682650f19188af985b90cd4b529956d85d391271a98cba6eef0ab0f508f54
```

## Stack Layer Extensions (v1.1)

```
stack/interfaces.py:                     3cda1c456db521d11347da84117cf910811fddbc82ef2eae313dfb330a8e40b6
stack/mission_planner.py:                177426bef7d2a22f0dcc8af8ac3256acf3cf6a1719b6e20d8ec8d5fc8aa17ed1
stack/fleet_manager.py:                  6a4addb512ebe19bb0b24e8da4f0ca9dcd7c15ee551eb8e6f0118dbde8dcda8c
examples/demo_coordinated_mission.py:    98a25403124d43164a308a6f369c47df0c600628ea9cc2430b76a08a357f0e28
```

## Verification Process

1. Clone the repository at the tagged release
2. Run `python tools/provenance_hash.py`
3. Compare output with hashes recorded here
4. Any mismatch indicates tampering or modification

## Chain of Trust

These hashes establish a verifiable audit trail. Each release tag should include updated provenance hashes in this file before tagging.
