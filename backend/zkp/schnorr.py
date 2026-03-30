"""
Schnorr Identification Protocol — ZK-Login
==========================================
Proves knowledge of a secret (password) without revealing it.

Protocol:
  Setup:   x = secret, y = g^x mod p  (public key)
  Step 1:  Prover picks random r, sends t = g^r mod p  (commitment)
  Step 2:  Verifier sends random challenge c
  Step 3:  Prover sends s = (r + c*x) mod q  (response)
  Verify:  g^s ≡ t · y^c (mod p)  ?

Zero-Knowledge because: t is uniformly random → s reveals nothing about x.
"""
import secrets
import hashlib
from typing import Tuple, Dict, Any

# RFC 5114 §2.1 — 1024-bit safe prime (p = 2q+1, both prime)
P = int(
    "B10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C6"
    "9A6A9DCA52D23B616073E28675A23D189838EF1E2EE652C0"
    "13ECB4AEA906112324975C3CD49B83BFACCBDD7D90C4BD70"
    "98488E9C219A73724EFFD6FAE5644738FAA31A4FF55BCCC0"
    "A151AF5F0DC8B4BD45BF37DF365C1A65E68CFDA76D4DA708"
    "DF1FB2BC2E4A4371", 16
)
G = 2           # generator
Q = (P - 1) // 2  # subgroup order


def _short(n: int) -> str:
    """Return first 16 chars of hex for display."""
    return hex(n)[:18] + "…"


def derive_secret(password: str) -> int:
    raw = int(hashlib.sha256(password.encode()).hexdigest(), 16) % Q
    return raw or 1


def compute_public_key(x: int) -> int:
    return pow(G, x, P)


def full_proof(password: str) -> Dict[str, Any]:
    """Run a complete interactive Schnorr proof and return all steps."""
    x = derive_secret(password)
    y = compute_public_key(x)

    # Step 1 — Commitment
    r = secrets.randbelow(Q - 1) + 1
    t = pow(G, r, P)

    # Step 2 — Challenge
    c = secrets.randbelow(Q - 1) + 1

    # Step 3 — Response
    s = (r + c * x) % Q

    # Verification
    lhs = pow(G, s, P)
    rhs = (t * pow(y, c, P)) % P
    valid = lhs == rhs

    return {
        "valid": valid,
        "public_key": _short(y),
        "steps": [
            {
                "step": 1, "actor": "prover", "name": "Key Setup",
                "description": "Prover derives secret x from password using SHA-256. Computes public key y = g^x mod p. Public key is shared; x never leaves the prover.",
                "formula": "y = gˣ mod p",
                "transmitted": {"y (public key)": _short(y)},
                "secret": {"x": _short(x)},
            },
            {
                "step": 2, "actor": "prover", "name": "Commitment",
                "description": "Prover picks a random nonce r and sends commitment t = g^r mod p. This hides x behind fresh randomness every round.",
                "formula": "t = gʳ mod p",
                "transmitted": {"t (commitment)": _short(t)},
                "secret": {"r (nonce)": _short(r)},
            },
            {
                "step": 3, "actor": "verifier", "name": "Challenge",
                "description": "Verifier picks a random challenge c. The prover cannot predict c, so they cannot pre-compute a fake response.",
                "formula": "c ← random ∈ ℤq",
                "transmitted": {"c (challenge)": _short(c)},
                "secret": {},
            },
            {
                "step": 4, "actor": "prover", "name": "Response",
                "description": "Prover binds the nonce to the challenge: s = (r + c·x) mod q. The response ties the commitment to the secret, but x is unrecoverable from s.",
                "formula": "s = (r + c·x) mod q",
                "transmitted": {"s (response)": _short(s)},
                "secret": {},
            },
            {
                "step": 5, "actor": "verifier", "name": "Verification",
                "description": "Verifier checks gˢ ≡ t·yᶜ (mod p). If equal, the prover knows x — without ever sending x.",
                "formula": "gˢ ≡ t · yᶜ (mod p)",
                "transmitted": {},
                "check": {"lhs gˢ": _short(lhs), "rhs t·yᶜ": _short(rhs), "match": valid},
                "valid": valid,
            },
        ],
        "zkp_properties": {
            "completeness": "An honest prover always passes verification.",
            "soundness": "Without knowing x, a cheater passes with probability ≤ 1/q (negligible).",
            "zero_knowledge": "The transcript (t, c, s) is simulatable without x → verifier learns nothing.",
        },
    }


def cheat_proof(real_password: str, fake_password: str) -> Dict[str, Any]:
    """Attempt to prove with wrong secret — demonstrates soundness."""
    x_real = derive_secret(real_password)
    y_real = compute_public_key(x_real)

    x_fake = derive_secret(fake_password)

    r = secrets.randbelow(Q - 1) + 1
    t = pow(G, r, P)
    c = secrets.randbelow(Q - 1) + 1
    s = (r + c * x_fake) % Q  # wrong secret used!

    lhs = pow(G, s, P)
    rhs = (t * pow(y_real, c, P)) % P
    valid = lhs == rhs

    return {"valid": valid, "caught": not valid,
            "message": "Soundness verified: cheater was caught!" if not valid else "False positive (astronomically rare)"}
