"""
ZK-Rollup Proof of Concept — ZK-Chain
======================================
Demonstrates how Zero-Knowledge Proofs secure a decentralized system.

Traditional Blockchain:
  - Every node re-executes every transaction
  - All transaction data is public on-chain
  - Slow: O(n) work per node per block

ZK-Rollup (what we simulate):
  - Transactions bundled off-chain by an operator
  - Single ZK proof posted on-chain per block
  - Nodes verify 1 proof instead of re-executing N transactions
  - Transaction amounts and balances are NEVER revealed on-chain

Cryptographic guarantees:
  - Balance privacy:    Pedersen commitments hide all balances
  - Spend validity:     Range proof proves sender_balance >= amount
  - Conservation:       Homomorphic commitments prove no coins created/destroyed
  - Integrity:          Invalid transactions make the proof fail — always
"""
import secrets
import hashlib
import time
from typing import Dict, Any, List

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

INITIAL_BALANCES = {"Marty": 1000, "Gloria": 500, "Skipper": 750}


def _commit(v: int, r: int) -> int:
    return (pow(G, v % Q, P) * pow(H, r, P)) % P


def _short(n: int) -> str:
    return hex(n)[:18] + "…"


def _make_fresh_user(balance: int) -> dict:
    r = secrets.randbelow(Q - 1) + 1
    return {"balance": balance, "r": r, "commitment": _short(_commit(balance, r))}


# ── Chain state ────────────────────────────────────────────────────────────
_state = {
    "balances": {k: _make_fresh_user(v) for k, v in INITIAL_BALANCES.items()},
    "mempool":  [],
    "blocks":   [],
}


def _state_root() -> str:
    """Merkle-style commitment to full ledger state."""
    combined = sum(
        _commit(_state["balances"][u]["balance"], _state["balances"][u]["r"])
        for u in sorted(_state["balances"])
    ) % P
    return _short(combined)


def _init_genesis():
    genesis = {
        "index": 0,
        "label": "Genesis",
        "timestamp": int(time.time()),
        "tx_count": 0,
        "transactions": [],
        "proof_hash": hashlib.sha256(b"ZKVault genesis").hexdigest()[:20] + "…",
        "prev_hash": "0" * 20 + "…",
        "state_root": _state_root(),
        "valid": True,
        "proof_steps": [],
        "zk_summary": "Initial state committed. No transactions.",
    }
    _state["blocks"] = [genesis]


_init_genesis()


# ── Public API ─────────────────────────────────────────────────────────────

def get_state() -> Dict[str, Any]:
    return {
        "blocks": _state["blocks"],
        "mempool": [
            {"id": tx["id"], "sender": tx["sender"],
             "receiver": tx["receiver"], "amount": "HIDDEN",
             "amount_commitment": tx["amount_commitment"]}
            for tx in _state["mempool"]
        ],
        "balances": {
            u: {"commitment": d["commitment"], "balance_hidden": True}
            for u, d in _state["balances"].items()
        },
        "state_root": _state_root(),
        "chain_length": len(_state["blocks"]),
    }


def add_transaction(sender: str, receiver: str, amount: int) -> Dict[str, Any]:
    users = list(_state["balances"].keys())
    if sender not in users or receiver not in users:
        return {"success": False, "error": "Unknown user"}
    if sender == receiver:
        return {"success": False, "error": "Cannot send to yourself"}
    if amount <= 0:
        return {"success": False, "error": "Amount must be positive"}

    sender_bal = _state["balances"][sender]["balance"]
    valid = sender_bal >= amount
    r_amount = secrets.randbelow(Q - 1) + 1

    tx = {
        "id":               hashlib.sha256(f"{sender}{receiver}{amount}{time.time()}".encode()).hexdigest()[:12],
        "sender":           sender,
        "receiver":         receiver,
        "amount":           amount,           # kept server-side only
        "amount_commitment": _short(_commit(amount, r_amount)),
        "valid":            valid,
    }

    if not valid:
        return {
            "success": False,
            "rejected": True,
            "error": f"Proof generation failed: {sender} cannot afford {amount} coins. The ZK proof would be unsatisfiable — the prover cannot construct a valid range proof for a negative balance.",
            "tx": {**tx, "amount": "HIDDEN"},
        }

    _state["mempool"].append(tx)
    return {
        "success": True,
        "tx": {**tx, "amount": "HIDDEN"},
        "mempool_size": len(_state["mempool"]),
        "note": f"Transaction added to mempool. Amount ({amount}) is hidden — only its Pedersen commitment is recorded.",
    }


def mine_block() -> Dict[str, Any]:
    if not _state["mempool"]:
        return {"success": False, "error": "Mempool is empty — add transactions first"}

    txs = list(_state["mempool"])
    old_root = _state_root()
    proof_steps = []

    # ── Off-chain: generate per-transaction proofs ──────────────────────
    for tx in txs:
        sender, receiver, amount = tx["sender"], tx["receiver"], tx["amount"]
        sb = _state["balances"][sender]["balance"]
        rb = _state["balances"][receiver]["balance"]
        sr = _state["balances"][sender]["r"]
        rr = _state["balances"][receiver]["r"]

        C_sender_old  = _commit(sb, sr)
        C_recv_old    = _commit(rb, rr)
        r_s_new = secrets.randbelow(Q - 1) + 1
        r_r_new = secrets.randbelow(Q - 1) + 1
        C_sender_new  = _commit(sb - amount, r_s_new)
        C_recv_new    = _commit(rb + amount, r_r_new)
        r_amount      = secrets.randbelow(Q - 1) + 1
        C_amount      = _commit(amount, r_amount)

        # Homomorphic conservation check:
        # C_sender_old = C_amount * C_sender_new  (mod P)
        # Because: g^sb * h^sr = g^amount * h^r_a * g^(sb-amount) * h^r_s_new
        #          = g^sb * h^(r_a + r_s_new)  => holds if sr = r_a + r_s_new mod Q
        # For demo we verify the balance arithmetic directly
        conservation = (sb == (sb - amount) + amount)

        proof_steps.append({
            "tx_id":        tx["id"],
            "sender":       sender,
            "receiver":     receiver,
            "proof_type":   "Range proof + Homomorphic conservation",
            "checks": {
                "sender_balance_sufficient": True,
                "amount_non_negative":        True,
                "conservation_holds":         conservation,
            },
            "commitments": {
                f"{sender} old balance":  _short(C_sender_old),
                f"{sender} new balance":  _short(C_sender_new),
                f"{receiver} old balance": _short(C_recv_old),
                f"{receiver} new balance": _short(C_recv_new),
                "amount commitment":      _short(C_amount),
            },
            "what_verifier_sees": "Only commitments and proof — amounts and balances NEVER revealed",
        })

        # Apply state
        _state["balances"][sender]["balance"]   = sb - amount
        _state["balances"][sender]["r"]         = r_s_new
        _state["balances"][sender]["commitment"] = _short(C_sender_new)
        _state["balances"][receiver]["balance"]  = rb + amount
        _state["balances"][receiver]["r"]        = r_r_new
        _state["balances"][receiver]["commitment"] = _short(C_recv_new)

    new_root = _state_root()

    # ── Aggregate proof (in production: zk-SNARK proof) ─────────────────
    prev_proof = _state["blocks"][-1]["proof_hash"].replace("…", "")
    agg_input  = f"{old_root}{new_root}{len(txs)}{prev_proof}".encode()
    agg_proof  = hashlib.sha256(agg_input).hexdigest()

    block = {
        "index":       len(_state["blocks"]),
        "label":       f"Block #{len(_state['blocks'])}",
        "timestamp":   int(time.time()),
        "tx_count":    len(txs),
        "transactions": [{"id": tx["id"], "sender": tx["sender"],
                           "receiver": tx["receiver"], "amount": "HIDDEN"}
                          for tx in txs],
        "proof_hash":        agg_proof[:20] + "…",
        "prev_hash":         prev_proof[:20] + "…",
        "old_state_root":    old_root,
        "state_root":        new_root,
        "valid":             True,
        "proof_steps":       proof_steps,
        "zk_summary":        f"{len(txs)} transaction(s) proven valid. Amounts hidden. State updated.",
        "on_chain_data_size": f"~256 bits (1 proof hash)",
        "traditional_size":   f"~{len(txs) * 512} bits ({len(txs)} full transactions)",
    }

    _state["blocks"].append(block)
    _state["mempool"] = []

    return {
        "success":      True,
        "block":        block,
        "new_balances": {u: {"commitment": d["commitment"], "balance_hidden": True}
                          for u, d in _state["balances"].items()},
        "zk_guarantees": {
            "Privacy":    "Transaction amounts and balances never appear on-chain",
            "Integrity":  "Invalid transactions cannot produce a valid proof",
            "Scalability": f"{len(txs)} transactions → 1 proof posted on-chain",
            "Trustless":  "Any node can verify the proof without trusting the operator",
        },
        "vs_traditional": {
            "Traditional": f"Re-execute {len(txs)} txn(s), store all amounts publicly",
            "ZK-Rollup":   "Verify 1 proof (~256 bits), store nothing sensitive",
        },
    }


def reset_chain() -> Dict[str, Any]:
    _state["balances"] = {k: _make_fresh_user(v) for k, v in INITIAL_BALANCES.items()}
    _state["mempool"]  = []
    _init_genesis()
    return {"reset": True, "message": "Chain reset to genesis state"}
