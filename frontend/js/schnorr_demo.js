// ── ZK-Login: Schnorr Identification Protocol ─────────────────────────

async function runSchnorr() {
  const password = document.getElementById('login-password').value.trim();
  if (!password) { alert('Please enter a password.'); return; }

  showLoading('proof-login', 'Running Schnorr Protocol…');

  try {
    const res = await fetch('/api/schnorr/prove', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    });
    const data = await res.json();
    renderSchnorrResult(data, 'proof-login');
  } catch(e) {
    document.getElementById('proof-login').innerHTML =
      `<div class="proof-placeholder"><p style="color:var(--rose)">Error: ${e.message}</p></div>`;
  }
}

async function runCheat() {
  const real_password = document.getElementById('login-real').value.trim();
  const fake_password = document.getElementById('login-fake').value.trim();
  if (!real_password || !fake_password) { alert('Enter both passwords.'); return; }
  if (real_password === fake_password) { alert('Use different passwords to simulate an attacker!'); return; }

  showLoading('proof-login', 'Simulating attack…');

  try {
    const res = await fetch('/api/schnorr/cheat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ real_password, fake_password })
    });
    const data = await res.json();
    renderCheatResult(data, 'proof-login');
  } catch(e) {
    document.getElementById('proof-login').innerHTML =
      `<div class="proof-placeholder"><p style="color:var(--rose)">Error: ${e.message}</p></div>`;
  }
}

function renderSchnorrResult(data, containerId) {
  const container = document.getElementById(containerId);
  const validClass = data.valid ? 'valid' : 'invalid';
  const msg  = data.valid ? 'Proof verified — identity confirmed. Password never transmitted.' : 'Verification failed.';

  let html = `
    <div class="proof-result">
      <div class="proof-header ${validClass}">
        <div>
          <div>${msg}</div>
          <div style="font-size:0.8rem;opacity:0.7;font-weight:400;margin-top:2px">Public key: <code>${data.public_key}</code></div>
        </div>
      </div>
      <div class="steps-timeline">
        ${(data.steps || []).map(renderStep).join('')}
      </div>
      ${renderZKPProps(data.zkp_properties)}
    </div>`;

  container.innerHTML = html;
  buildSteps(data.steps || [], containerId);
}

function renderCheatResult(data, containerId) {
  const container = document.getElementById(containerId);
  const caught = data.caught !== false;
  const icon   = caught ? '🚨' : '😱';
  const title  = caught ? 'Attacker Caught!' : 'False Positive (Extremely Rare)';
  const color  = caught ? 'var(--emerald)' : 'var(--rose)';

  container.innerHTML = `
    <div class="cheat-result">
      <div class="cheat-icon">${icon}</div>
      <div class="cheat-title" style="color:${color}">${title}</div>
      <div class="cheat-desc">${data.message}</div>
      <div style="margin-top:1.5rem;font-size:0.85rem;color:var(--text-muted);max-width:360px;margin:1.5rem auto 0">
        <strong style="color:var(--text)">Why soundness works:</strong><br/>
        Without the correct secret x, g^s ≢ t·y^c (mod p). An attacker would need to solve
        the discrete logarithm problem — computationally infeasible on a 1024-bit prime.
      </div>
    </div>`;
}
