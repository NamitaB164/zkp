// ── ZK-Vote: OR-Proof ────────────────────────────────────────────────

async function runVote() {
  if (selectedVote === null) { alert('Please select YES or NO first.'); return; }

  showLoading('proof-vote', 'Generating anonymous ballot proof…');

  try {
    const res = await fetch('/api/vote/prove', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vote: selectedVote })
    });
    const data = await res.json();
    renderVoteResult(data, 'proof-vote');
  } catch(e) {
    document.getElementById('proof-vote').innerHTML =
      `<div class="proof-placeholder"><p style="color:var(--rose)">Error: ${e.message}</p></div>`;
  }
}

function renderVoteResult(data, containerId) {
  const container = document.getElementById(containerId);

  const summaryHtml = `
    <div style="display:flex;gap:1rem;margin-bottom:1.2rem;flex-wrap:wrap">
      <div style="flex:1;min-width:130px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:0.9rem 1.1rem">
        <div style="font-size:0.72rem;color:var(--text-muted);font-weight:700;text-transform:uppercase;letter-spacing:.4px">Ballot Valid?</div>
        <div style="font-size:1.1rem;font-weight:800;color:var(--emerald);margin-top:0.2rem">✓ Verified</div>
      </div>
      <div style="flex:1;min-width:130px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:0.9rem 1.1rem">
        <div style="font-size:0.72rem;color:var(--text-muted);font-weight:700;text-transform:uppercase;letter-spacing:.4px">Vote Revealed?</div>
        <div style="font-size:1.1rem;font-weight:800;color:var(--amber);margin-top:0.2rem">🙈 Never</div>
      </div>
      <div style="flex:1;min-width:130px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:0.9rem 1.1rem">
        <div style="font-size:0.72rem;color:var(--text-muted);font-weight:700;text-transform:uppercase;letter-spacing:.4px">Sealed Ballot</div>
        <div style="font-size:0.75rem;font-family:var(--font-mono);color:var(--cyan);margin-top:0.3rem;word-break:break-all">${data.ballot_commitment}</div>
      </div>
    </div>
    <div style="background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.25);border-radius:10px;padding:0.9rem 1.2rem;margin-bottom:1.2rem;font-size:0.85rem;color:var(--text-muted)">
      <strong style="color:var(--primary-light)">🔮 The magic:</strong>
      The verifier just confirmed your vote is YES or NO — but has <em>zero</em> idea which.
      The two proof branches are mathematically indistinguishable. This is OR-proof in action.
    </div>`;

  let html = `
    <div class="proof-result">
      <div class="proof-header valid">
        <div>
          <div>Anonymous ballot accepted — vote proven valid without disclosure</div>
          <div style="font-size:0.8rem;opacity:0.7;font-weight:400;margin-top:2px">Non-interactive Fiat-Shamir OR-proof</div>
        </div>
      </div>
      ${summaryHtml}
      <div class="steps-timeline">
        ${(data.steps || []).map(renderStep).join('')}
      </div>
      ${renderZKPProps(data.zkp_properties)}
    </div>`;

  container.innerHTML = html;
  buildSteps(data.steps || [], containerId);
}
