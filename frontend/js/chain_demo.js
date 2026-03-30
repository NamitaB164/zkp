// ── ZK-Chain: ZK-Rollup Demo ─────────────────────────────────────────

// Override switchTab to handle the chain panel (outside .scenarios)
const _origSwitch = switchTab;
window.switchTab = function(name) {
  document.querySelectorAll('.tab').forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected','false'); });
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  document.getElementById('tab-' + name).setAttribute('aria-selected','true');
  document.getElementById('panel-' + name).classList.add('active');
  if (name === 'chain') loadChainState();
};

async function loadChainState() {
  try {
    const res  = await fetch('/api/chain/state');
    const data = await res.json();
    renderBalances(data.balances);
    renderBlocks(data.blocks);
    renderMempool(data.mempool);
  } catch(e) { console.error(e); }
}

// ── Balances ─────────────────────────────────────────────────────────
function renderBalances(balances) {
  const el = document.getElementById('chain-balances');
  if (!el) return;
  el.innerHTML = Object.entries(balances).map(([user, d]) => `
    <div class="balance-row">
      <span class="balance-user">${user}</span>
      <span class="balance-val">${d.commitment}</span>
      <span class="balance-tag">HIDDEN</span>
    </div>`).join('');
}

// ── Blocks ────────────────────────────────────────────────────────────
function renderBlocks(blocks) {
  const el = document.getElementById('chain-blocks');
  if (!el) return;
  el.innerHTML = blocks.map((b, i) => `
    <div class="chain-block ${b.index === 0 ? 'genesis' : ''}" onclick="showBlockDetail(${b.index})" id="block-${b.index}">
      ${i > 0 ? '<div class="chain-arrow">→</div>' : ''}
      <div class="block-card">
        <div class="block-label">${b.label}</div>
        <div class="block-row"><span>Proof</span><code>${b.proof_hash}</code></div>
        <div class="block-row"><span>Prev</span><code>${b.prev_hash}</code></div>
        <div class="block-row"><span>Txns</span><span class="block-count">${b.tx_count}</span></div>
        <div class="block-row"><span>State Root</span><code>${b.state_root || '—'}</code></div>
        <div class="block-row"><span>Amounts</span><span class="hidden-tag">HIDDEN</span></div>
      </div>
    </div>`).join('');

  // Scroll to latest block
  const last = document.getElementById(`block-${blocks.length - 1}`);
  if (last) last.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'end' });
}

const _blockDataCache = {};
async function showBlockDetail(index) {
  // Re-fetch state to get fresh block data
  const res   = await fetch('/api/chain/state');
  const state = await res.json();
  const block = state.blocks[index];
  if (!block) return;

  const el = document.getElementById('chain-proof-detail');
  if (!block.proof_steps || block.proof_steps.length === 0) {
    el.innerHTML = `<div class="proof-result"><div class="proof-header valid"><div><div>${block.label} — Genesis. No transactions.</div></div></div></div>`;
    return;
  }

  const stepsHtml = block.proof_steps.map((s, i) => `
    <div class="step-item visible" style="margin-bottom:1rem">
      <div class="step-dot prover">${i+1}</div>
      <div class="step-body">
        <div class="step-meta"><span class="step-actor prover">ZK Proof</span></div>
        <div class="step-name">${s.sender} → ${s.receiver}</div>
        <div class="step-desc">${s.proof_type}</div>
        <div class="formula-box">Checks: ${Object.entries(s.checks).map(([k,v])=>`${k}: ${v?'PASS':'FAIL'}`).join(' | ')}</div>
        <div class="transmitted-wrap">
          <div class="transmitted-label">Commitments posted on-chain (no amounts)</div>
          <div class="kv-list">${Object.entries(s.commitments).map(([k,v])=>`<div class="kv-row"><span class="kv-key">${k}</span><span class="kv-val">${v}</span></div>`).join('')}</div>
        </div>
        <div style="margin-top:0.5rem;font-size:0.8rem;color:var(--amber)">
          ${s.what_verifier_sees}
        </div>
      </div>
    </div>`).join('');

  el.innerHTML = `
    <div class="proof-result" style="margin-top:1.5rem;animation:fadeIn 0.3s ease">
      <div class="proof-header valid">
        <div>
          <div>${block.label} — Block Proof Verified</div>
          <div style="font-size:0.8rem;opacity:0.7;font-weight:400;margin-top:2px">
            ${block.tx_count} transaction(s) | On-chain: ${block.on_chain_data_size} | Traditional: ${block.traditional_size}
          </div>
        </div>
      </div>
      <div style="display:flex;gap:1rem;margin-bottom:1rem;flex-wrap:wrap">
        <div style="flex:1;min-width:130px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:0.8rem 1rem">
          <div style="font-size:0.7rem;color:var(--text-muted);font-weight:700;text-transform:uppercase">On-Chain Data</div>
          <div style="font-size:0.95rem;font-weight:800;color:var(--emerald)">${block.on_chain_data_size}</div>
        </div>
        <div style="flex:1;min-width:130px;background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.3);border-radius:10px;padding:0.8rem 1rem">
          <div style="font-size:0.7rem;color:var(--text-muted);font-weight:700;text-transform:uppercase">Traditional Would Store</div>
          <div style="font-size:0.95rem;font-weight:800;color:var(--rose)">${block.traditional_size}</div>
        </div>
        <div style="flex:1;min-width:130px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:0.8rem 1rem">
          <div style="font-size:0.7rem;color:var(--text-muted);font-weight:700;text-transform:uppercase">Amounts Revealed?</div>
          <div style="font-size:0.95rem;font-weight:800;color:var(--amber)">Never</div>
        </div>
      </div>
      <div class="steps-timeline">${stepsHtml}</div>
    </div>`;
}

// ── Mempool ───────────────────────────────────────────────────────────
function renderMempool(txs) {
  const el  = document.getElementById('chain-mempool');
  const btn = document.getElementById('btn-mine');
  if (!el) return;

  if (!txs || txs.length === 0) {
    el.innerHTML = '<p class="hint">No pending transactions.</p>';
    if (btn) btn.disabled = true;
    return;
  }

  el.innerHTML = txs.map(tx => `
    <div class="mempool-tx">
      <span class="tx-flow">${tx.sender} → ${tx.receiver}</span>
      <span class="tx-amount">Amount: <span class="hidden-tag">HIDDEN</span></span>
      <span class="tx-commit" title="${tx.amount_commitment}">${tx.amount_commitment}</span>
    </div>`).join('');

  if (btn) btn.disabled = false;
}

// ── Add transaction ───────────────────────────────────────────────────
async function addChainTx() {
  const sender   = document.getElementById('tx-sender').value;
  const receiver = document.getElementById('tx-receiver').value;
  const amount   = parseInt(document.getElementById('tx-amount').value || 0);

  if (sender === receiver) { showChainMsg('Sender and receiver must be different.', 'error'); return; }
  if (!amount || amount <= 0) { showChainMsg('Enter a valid amount.', 'error'); return; }

  try {
    const res  = await fetch('/api/chain/add_tx', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ sender, receiver, amount })
    });
    const data = await res.json();

    if (data.success) {
      showChainMsg(`Transaction added to mempool. Amount sealed in commitment — not visible on-chain.`, 'success');
      loadChainState();
    } else if (data.rejected) {
      showChainMsg(`Proof rejected: ${data.error}`, 'error');
    } else {
      showChainMsg(data.error || 'Error', 'error');
    }
  } catch(e) { showChainMsg(e.message, 'error'); }
}

// ── Mine block ────────────────────────────────────────────────────────
async function mineBlock() {
  const btn = document.getElementById('btn-mine');
  if (btn) { btn.disabled = true; btn.querySelector('span').textContent = 'Generating proof…'; }

  try {
    const res  = await fetch('/api/chain/mine', { method: 'POST' });
    const data = await res.json();

    if (data.success) {
      showChainMsg(`Block #${data.block.index} mined. ${data.block.tx_count} transaction(s) proven — amounts never revealed.`, 'success');
      await loadChainState();
      showBlockDetail(data.block.index);
    } else {
      showChainMsg(data.error, 'error');
    }
  } catch(e) { showChainMsg(e.message, 'error'); }

  if (btn) btn.querySelector('span').textContent = 'Mine Block (Generate Proof)';
}

// ── Reset chain ───────────────────────────────────────────────────────
async function resetChain() {
  await fetch('/api/chain/reset', { method: 'POST' });
  document.getElementById('chain-proof-detail').innerHTML = '';
  showChainMsg('Chain reset to genesis.', 'success');
  loadChainState();
}

// ── Notification ──────────────────────────────────────────────────────
function showChainMsg(msg, type) {
  let el = document.getElementById('chain-msg');
  if (!el) {
    el = document.createElement('div');
    el.id = 'chain-msg';
    document.getElementById('panel-chain').prepend(el);
  }
  const color = type === 'success' ? 'var(--emerald)' : 'var(--rose)';
  const bg    = type === 'success' ? 'rgba(16,185,129,0.1)' : 'rgba(244,63,94,0.1)';
  el.style.cssText = `background:${bg};border:1px solid ${color};color:${color};padding:0.7rem 1rem;border-radius:8px;font-size:0.85rem;margin-bottom:1rem;animation:fadeIn 0.25s ease`;
  el.textContent = msg;
  setTimeout(() => { if (el) el.remove(); }, 5000);
}
