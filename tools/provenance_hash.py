#!/usr/bin/env python3
# tools/provenance_hash.py
# Compute SHA-256 hashes for provenance/audit. (No secrets.)

import hashlib
from pathlib import Path

FILES = [
    "cgcs_core.py",
    "loop_guard.py",
    "role_spec.py",
    "DAVNA-COVENANT.md",
    "ETHICS-LICENSE.md",
    "README.md",
    "ARCHITECTURE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
]

def sha256_file(p: Path) -> str:
    """Compute SHA-256 hash of file contents."""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    root = Path(__file__).resolve().parents[1]
    print("CGCS v1.0 Provenance Hashes")
    print("=" * 60)
    for rel in FILES:
        path = root / rel
        if path.exists():
            hash_val = sha256_file(path)
            print(f"{rel:30s} {hash_val}")
        else:
            print(f"{rel:30s} (missing)")
    print("=" * 60)

if __name__ == "__main__":
    main()
