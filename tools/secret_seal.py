#!/usr/bin/env python3
# tools/secret_seal.py
# STDLIB-ONLY "sealed envelope":
# - Key derivation: PBKDF2-HMAC-SHA256
# - Stream: SHA256(counter || key) XOR
# - Integrity: HMAC-SHA256 over header+ciphertext
#
# Notes:
# - Prefer age/gpg for real-world strong encryption.
# - This is for local protection / "don't accidentally leak" use-cases.

import os, hmac, hashlib, struct, base64
from dataclasses import dataclass

MAGIC = b"CGCS-SEALv1"
PBKDF2_ITERS = 200_000
SALT_LEN = 16
NONCE_LEN = 16
TAG_LEN = 32

def pbkdf2_key(password: str, salt: bytes, nbytes: int = 32) -> bytes:
    """Derive encryption key from password using PBKDF2."""
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERS, dklen=nbytes)

def keystream(key: bytes, nonce: bytes, n: int) -> bytes:
    """Generate keystream for XOR cipher using SHA256."""
    out = bytearray()
    counter = 0
    while len(out) < n:
        block = hashlib.sha256(nonce + struct.pack(">Q", counter) + key).digest()
        out.extend(block)
        counter += 1
    return bytes(out[:n])

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte sequences."""
    return bytes(x ^ y for x, y in zip(a, b))

@dataclass
class Sealed:
    """Sealed secret (base64-encoded blob)."""
    b64: str

def seal(plaintext: bytes, password: str) -> Sealed:
    """
    Seal plaintext with password.
    
    Returns base64-encoded blob containing:
    - Magic header
    - Random salt (for PBKDF2)
    - Random nonce (for keystream)
    - Ciphertext (plaintext XOR keystream)
    - HMAC tag (authentication)
    """
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = pbkdf2_key(password, salt, 32)

    ks = keystream(key, nonce, len(plaintext))
    ct = xor_bytes(plaintext, ks)

    header = MAGIC + salt + nonce
    tag = hmac.new(key, header + ct, hashlib.sha256).digest()
    blob = header + ct + tag
    return Sealed(base64.urlsafe_b64encode(blob).decode("ascii"))

def unseal(sealed_b64: str, password: str) -> bytes:
    """
    Unseal encrypted blob with password.
    
    Raises ValueError if:
    - Magic header doesn't match
    - HMAC authentication fails
    - Blob is malformed
    """
    blob = base64.urlsafe_b64decode(sealed_b64.encode("ascii"))
    if blob[:len(MAGIC)] != MAGIC:
        raise ValueError("bad magic")
    
    salt = blob[len(MAGIC):len(MAGIC)+SALT_LEN]
    nonce = blob[len(MAGIC)+SALT_LEN:len(MAGIC)+SALT_LEN+NONCE_LEN]
    ct_and_tag = blob[len(MAGIC)+SALT_LEN+NONCE_LEN:]
    
    if len(ct_and_tag) < TAG_LEN:
        raise ValueError("truncated")
    
    ct = ct_and_tag[:-TAG_LEN]
    tag = ct_and_tag[-TAG_LEN:]

    key = pbkdf2_key(password, salt, 32)
    header = MAGIC + salt + nonce
    check = hmac.new(key, header + ct, hashlib.sha256).digest()
    
    if not hmac.compare_digest(tag, check):
        raise ValueError("auth failed")

    ks = keystream(key, nonce, len(ct))
    return xor_bytes(ct, ks)

def main():
    """Example usage (interactive mode)."""
    import sys
    if len(sys.argv) < 2 or sys.argv[1] not in {"seal", "unseal"}:
        print("Usage: python secret_seal.py {seal|unseal}")
        print("\nExample:")
        print("  echo 'my secret' | python secret_seal.py seal")
        print("  echo '<sealed>' | python secret_seal.py unseal")
        return

    import getpass
    password = getpass.getpass("Password: ")

    if sys.argv[1] == "seal":
        plaintext = sys.stdin.buffer.read()
        sealed = seal(plaintext, password)
        print(sealed.b64)
    else:
        sealed_b64 = sys.stdin.read().strip()
        try:
            plaintext = unseal(sealed_b64, password)
            sys.stdout.buffer.write(plaintext)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
