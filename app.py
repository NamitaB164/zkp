from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from zkp.schnorr import full_proof as schnorr_proof, cheat_proof
from zkp.range_proof import prove_range
from zkp.or_proof import prove_vote
from zkp import zkchain

app = Flask(__name__, static_folder='frontend')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

# ── Scenario 1: ZK-Login (Schnorr) ─────────────────────────────────────────

@app.route('/api/schnorr/prove', methods=['POST'])
def api_schnorr_prove():
    data = request.get_json()
    password = (data or {}).get('password', '').strip()
    if not password:
        return jsonify({"error": "Password is required"}), 400
    try:
        return jsonify(schnorr_proof(password))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schnorr/cheat', methods=['POST'])
def api_schnorr_cheat():
    data = request.get_json()
    real_pw = (data or {}).get('real_password', '').strip()
    fake_pw = (data or {}).get('fake_password', '').strip()
    if not real_pw or not fake_pw:
        return jsonify({"error": "Both passwords required"}), 400
    try:
        return jsonify(cheat_proof(real_pw, fake_pw))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Scenario 2: ZK-Finance (Range Proof) ───────────────────────────────────

@app.route('/api/range/prove', methods=['POST'])
def api_range_prove():
    data = request.get_json()
    try:
        salary = int((data or {}).get('salary', 0))
        threshold = int((data or {}).get('threshold', 50000))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid salary or threshold"}), 400
    try:
        return jsonify(prove_range(salary, threshold))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Scenario 3: ZK-Vote (OR-Proof) ─────────────────────────────────────────

@app.route('/api/vote/prove', methods=['POST'])
def api_vote_prove():
    data = request.get_json()
    try:
        vote = int((data or {}).get('vote', -1))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid vote"}), 400
    if vote not in (0, 1):
        return jsonify({"error": "Vote must be 0 (NO) or 1 (YES)"}), 400
    try:
        return jsonify(prove_vote(vote))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Scenario 4: ZK-Chain (ZK-Rollup) ───────────────────────────────────────

@app.route('/api/chain/state', methods=['GET'])
def api_chain_state():
    try:
        return jsonify(zkchain.get_state())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chain/add_tx', methods=['POST'])
def api_chain_add_tx():
    data = request.get_json() or {}
    try:
        sender   = data.get('sender', '')
        receiver = data.get('receiver', '')
        amount   = int(data.get('amount', 0))
        return jsonify(zkchain.add_transaction(sender, receiver, amount))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chain/mine', methods=['POST'])
def api_chain_mine():
    try:
        return jsonify(zkchain.mine_block())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chain/reset', methods=['POST'])
def api_chain_reset():
    try:
        return jsonify(zkchain.reset_chain())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n  ZK-Vault server starting...")
    print("  Open: http://localhost:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)