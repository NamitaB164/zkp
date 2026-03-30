// ── ZK-Finance: Range Proof ──────────────────────────────────────────

async function runRange() {
  const salary    = parseInt(document.getElementById('salary-input').value    || 0);
  const threshold = parseInt(document.getElementById('threshold-input').value || 50000);

  if (isNaN(salary) || isNaN(threshold)) { alert('Enter valid numbers.'); return; }

  showLoading('proof-finance', 'Generating range proof…');

  try {
    const res = await fetch('/api/range/prove', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ salary, threshold })
    });
    const data = await res.json();
    renderRangeResult(data, 'proof-finance', salary, threshold);
  } catch(e) {
    document.getElementById('proof-finance').innerHTML =
      `<div class="proof-placeholder"><p style="color:var(--rose)">Error: ${e.message}</p></div>`;
  }
}

function renderRangeResult(data, containerId, salary, threshold) {
  const container = document.getElementById(containerId);

  if (!data.valid) {
    container.innerHTML = `
      <div class="proof-result">
        <div class="proof-header invalid">
          <span class="result-icon">❌</span>
          <div>
            <div>Proof failed — salary does not meet threshold</div>
            <div style="font-size:0.8rem;opacity:0.7;font-weight:400;margin-top:2px">
              A proof certifying eligibility cannot be generated because it would be false.
            </div>
          </div>
        </div>
        <div style="padding:1.5rem;text-align:center;color:var(--text-muted);font-size:0.9rem">
          <div style="font-size:2rem;margin-bottom:0.8rem">🛡</div>
          <strong style="color:var(--text)">Soundness in action.</strong><br/>
          The protocol prevents you from creating a false proof.
          Try setting salary above the threshold.
        </div>
      </div>`;
    return;
  }

  const resultColor = data.result === 'ABOVE THRESHOLD' ? 'var(--emerald)' : 'var(--rose)';
  const resultIcon  = data.result === 'ABOVE THRESHOLD' ? '✅' : '❌';

  // Summary bar
  const summaryHtml = `
    <div style="display:flex;gap:1rem;margin-bottom:1.2rem;flex-wrap:wrap">
      <div style="flex:1;min-width:140px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:0.9rem 1.1rem">
        <div style="font-size:0.72rem;color:var(--text-muted);font-weight:700;text-transform:uppercase;letter-spacing:.4px">Result</div>
        <div style="font-size:1.1rem;font-weight:800;color:${resultColor};margin-top:0.2rem">${resultIcon} ${data.result}</div>
      </div>
      <div style="flex:1;min-width:140px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:0.9rem 1.1rem">
        <div style="font-size:0.72rem;color:var(--text-muted);font-weight:700;text-transform:uppercase;letter-spacing:.4px">Salary Revealed?</div>
        <div style="font-size:1.1rem;font-weight:800;color:var(--amber);margin-top:0.2rem">🙈 Never</div>
      </div>
      <div style="flex:1;min-width:140px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:0.9rem 1.1rem">
        <div style="font-size:0.72rem;color:var(--text-muted);font-weight:700;text-transform:uppercase;letter-spacing:.4px">Bit Commitments</div>
        <div style="font-size:1.1rem;font-weight:800;color:var(--primary-light);margin-top:0.2rem">${data.num_bits || 20}</div>
      </div>
    </div>`;

  let html = `
    <div class="proof-result">
      <div class="proof-header valid">
        <div>
          <div>Range proof verified — salary meets threshold of $${threshold.toLocaleString()}</div>
          <div style="font-size:0.8rem;opacity:0.7;font-weight:400;margin-top:2px">Commitment: <code>${(data.commitments || {})['C_salary'] || ''}</code></div>
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
