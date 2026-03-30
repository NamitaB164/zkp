"""
Disjunctive Sigma Protocol (OR-Proof) — ZK-Vote
================================================
Proves a ballot commitment is to 0 (NO) OR 1 (YES) — without revealing which.

Protocol (Fiat-Shamir non-interactive):
  Commit:     C = g^vote · h^r mod p
  Real path:  Full sigma proof for the actual vote bit
  Fake path:  Simulated proof for the other bit (backward construction)
  Challenge:  c = H(C, t0, t1)  — Fiat-Shamir
  Split:      c0 + c1 ≡ c (mod q)
  Verify:     Both branches satisfy: h^sᵢ · (C·g^{-i})^{cᵢ} = tᵢ

The simulation is computationally indistinguishable from a real proof → ZK.
"""
import secrets
import hashlib
from typing import Dict, Any

P = int(
    "B10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C6"
    "9A6A9DCA52D23B616073E28675A23D189838EF1E2EE652C0"
    "13ECB4AEA906112324975C3CD49B83BFACCBDD7D90C4BD70"
    "98488E9C219A73724EFFD6FAE5644738FAA31A4FF55BCCC0"
    "A151AF5F0DC8B4BD45BF37DF365C1A65E68CFDA76D4DA708"
    "DF1FB2BC2E4A4371", 16
)
G = 2
Q = (P - 1) // 2
H = pow(G, int(hashlib.sha256(b"ZKVault_H_gen_v1").hexdigest(), 16) % Q, P)
G_INV = pow(G, P - 2, P)  # g^(-1) mod p


def _short(n: int) -> str:
    return hex(n)[:18] + "…"


def _fiat_shamir(C: int, t0: int, t1: int) -> int:
    """Hash commitment + both branch transcripts → global challenge."""
    data = C.to_bytes(128, 'big') + t0.to_bytes(128, 'big') + t1.to_bytes(128, 'big')
    return int(hashlib.sha256(data).hexdigest(), 16) % Q


def pedersen_commit(v: int, r: int) -> int:
    return (pow(G, v % Q, P) * pow(H, r, P)) % P


def prove_vote(vote: int) -> Dict[str, Any]:
    """Full disjunctive OR-proof. vote must be 0 (NO) or 1 (YES)."""
    assert vote in (0, 1), "Vote must be 0 or 1"
    vote_label = "YES" if vote == 1 else "NO"
    other_label = "NO" if vote == 1 else "YES"

    # Sealed ballot
    r = secrets.randbelow(Q - 1) + 1
    C = pedersen_commit(vote, r)

    # C_adj[i] = C · g^(-i): the value whose discrete log we prove
    # Branch 0: prove C itself = h^r  (vote=0 case)
    # Branch 1: prove C·g^(-1) = h^r (vote=1 case)

    if vote == 0:
        # ── Real branch 0 ──────────────────────────────────────────────
        k0 = secrets.randbelow(Q - 1) + 1
        t0 = pow(H, k0, P)                         # t0 = h^k0

        # ── Simulated branch 1 (backward) ──────────────────────────────
        c1 = secrets.randbelow(Q - 1) + 1
        s1 = secrets.randbelow(Q - 1) + 1
        C1 = (C * G_INV) % P                        # C/g
        t1 = (pow(H, s1, P) * pow(C1, c1, P)) % P  # t1 constructed so check passes

        # ── Fiat-Shamir & split ─────────────────────────────────────────
        c = _fiat_shamir(C, t0, t1)
        c0 = (c - c1) % Q
        s0 = (k0 - c0 * r) % Q

    else:  # vote == 1
        # ── Real branch 1 ──────────────────────────────────────────────
        k1 = secrets.randbelow(Q - 1) + 1
        C1 = (C * G_INV) % P                        # C/g
        t1 = pow(H, k1, P)                          # t1 = h^k1

        # ── Simulated branch 0 (backward) ──────────────────────────────
        c0 = secrets.randbelow(Q - 1) + 1
        s0 = secrets.randbelow(Q - 1) + 1
        t0 = (pow(H, s0, P) * pow(C, c0, P)) % P   # t0 constructed so check passes

        # ── Fiat-Shamir & split ─────────────────────────────────────────
        c = _fiat_shamir(C, t0, t1)
        c1 = (c - c0) % Q
        s1 = (k1 - c1 * r) % Q

    # ── Verification ───────────────────────────────────────────────────
    C0 = C
    C1_ver = (C * G_INV) % P
    c_total = _fiat_shamir(C, t0, t1)

    ok_challenge = (c0 + c1) % Q == c_total % Q
    ok_branch0   = (pow(H, s0, P) * pow(C0, c0, P)) % P == t0
    ok_branch1   = (pow(H, s1, P) * pow(C1_ver, c1, P)) % P == t1
    valid = ok_challenge and ok_branch0 and ok_branch1

    return {
        "valid": valid,
        "ballot_commitment": _short(C),
        "actual_vote_hidden": True,
        "steps": [
            {
                "step": 1, "actor": "voter", "name": "Sealed Ballot",
                "description": f"Voter seals their ballot in a Pedersen commitment. The commitment is perfectly hiding — it looks identical for YES or NO to any observer.",
                "formula": "C = g^vote · h^r mod p",
                "transmitted": {"C (sealed ballot)": _short(C)},
                "secret": {f"vote ({vote_label})": "HIDDEN", "r (blinding)": _short(r)},
            },
            {
                "step": 2, "actor": "voter", "name": "Dual-Path Proof",
                "description": f"Voter constructs TWO proof paths in parallel — one real (for actual vote: {vote_label}), one simulated (for {other_label}). The simulation is mathematically indistinguishable from a real proof.",
                "formula": "Prove: (C = g⁰·hʳ) OR (C = g¹·hʳ)",
                "transmitted": {"t₀ (branch-0 commitment)": _short(t0), "t₁ (branch-1 commitment)": _short(t1)},
                "secret": {"real branch": vote_label, "simulated branch": other_label},
            },
            {
                "step": 3, "actor": "verifier", "name": "Fiat-Shamir Challenge",
                "description": "Global challenge is computed by hashing all commitments — making this non-interactive. Challenge is split between the two branches.",
                "formula": "c = H(C, t₀, t₁)  →  c₀ + c₁ ≡ c (mod q)",
                "transmitted": {"c (global)": _short(c_total), "c₀": _short(c0), "c₁": _short(c1)},
                "secret": {},
            },
            {
                "step": 4, "actor": "voter", "name": "Responses",
                "description": "Voter sends responses s₀, s₁ for both branches. One is a real sigma-protocol response; the other was chosen freely during simulation.",
                "formula": "sᵢ = kᵢ − cᵢ·r mod q",
                "transmitted": {"s₀": _short(s0), "s₁": _short(s1)},
                "secret": {},
            },
            {
                "step": 5, "actor": "verifier", "name": "Verification",
                "description": "Verifier checks all three conditions. Never finds out WHICH branch was real — both look identical.",
                "formula": "h^{sᵢ}·(C·g^{-i})^{cᵢ} = tᵢ  for i∈{0,1}  ∧  c₀+c₁≡c",
                "transmitted": {},
                "check": {
                    "challenge sum": ok_challenge,
                    "branch 0 (NO)": ok_branch0,
                    "branch 1 (YES)": ok_branch1,
                },
                "valid": valid,
            },
        ],
        "zkp_properties": {
            "completeness": "Any honest vote (YES or NO) always produces a valid proof.",
            "soundness": "Voter cannot commit to an invalid ballot (e.g., vote=2) and pass verification.",
            "zero_knowledge": "Both branches look computationally identical — voter's choice is provably hidden.",
        },
    }
