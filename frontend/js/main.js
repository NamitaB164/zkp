// ── Tab switching ────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected','false'); });
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  document.getElementById('tab-' + name).setAttribute('aria-selected','true');
  document.getElementById('panel-' + name).classList.add('active');
}

// ── Shared: show loading spinner ─────────────────────────────────────
function showLoading(containerId, label) {
  document.getElementById(containerId).innerHTML = `
    <div class="spinner-wrap">
      <div class="spinner"></div>
      <div class="spinner-label">${label}</div>
    </div>`;
}

// ── Shared: build step HTML ──────────────────────────────────────────
function buildSteps(steps, containerId) {
  const container = document.getElementById(containerId);
  const stepItems = container.querySelectorAll('.step-item');
  stepItems.forEach((el, i) => {
    setTimeout(() => el.classList.add('visible'), 120 * i);
  });
}

function renderKV(obj, cls='') {
  if (!obj || !Object.keys(obj).length) return '';
  const rows = Object.entries(obj).map(([k, v]) => {
    const display = Array.isArray(v) ? v.join(', ') : String(v);
    return `<div class="kv-row ${cls}"><span class="kv-key">${k}</span><span class="kv-val">${display}</span></div>`;
  }).join('');
  return rows;
}

function renderStep(step) {
  const actor = step.actor || 'prover';
  const checks = step.check ? Object.entries(step.check).map(([k,v]) => {
    const isOk = v === true || v === 'APPROVED';
    return `<div class="check-badge ${isOk ? 'pass':'fail'}">${isOk?'✓':'✗'} ${k}</div>`;
  }).join('') : '';

  const transmitted = renderKV(step.transmitted);
  const secret = renderKV(step.secret, 'kv-secret');

  return `
  <div class="step-item">
    <div class="step-dot ${actor}">${step.step}</div>
    <div class="step-body">
      <div class="step-meta">
        <span class="step-num">Step ${step.step}</span>
        <span class="step-actor ${actor}">${actor}</span>
      </div>
      <div class="step-name">${step.name}</div>
      <div class="step-desc">${step.description}</div>
      ${step.formula ? `<div class="formula-box">${step.formula}</div>` : ''}
      ${transmitted ? `<div class="transmitted-wrap"><div class="transmitted-label">📡 Transmitted to verifier</div><div class="kv-list">${transmitted}</div></div>` : ''}
      ${secret ? `<div class="transmitted-wrap"><div class="transmitted-label">🔒 Kept secret</div><div class="kv-list">${secret}</div></div>` : ''}
      ${checks ? `<div class="check-badges">${checks}</div>` : ''}
    </div>
  </div>`;
}

function renderZKPProps(props) {
  if (!props) return '';
  const items = Object.entries(props).map(([k,v]) => `
    <div class="zkp-prop-item">
      <span class="zkp-prop-name">${k.charAt(0).toUpperCase()+k.slice(1)}</span>
      <span class="zkp-prop-desc">${v}</span>
    </div>`).join('');
  return `<div class="zkp-props"><div class="zkp-props-title">ZKP Properties Demonstrated</div><div class="zkp-prop-list">${items}</div></div>`;
}

// ── Vote state ────────────────────────────────────────────────────────
let selectedVote = null;

function selectVote(v) {
  selectedVote = v;
  document.getElementById('vote-yes').classList.toggle('selected', v === 1);
  document.getElementById('vote-no').classList.toggle('selected',  v === 0);
  const label = document.getElementById('vote-selected');
  label.style.display = 'block';
  label.textContent = `Ballot sealed: ${v === 1 ? '✓ YES' : '✗ NO'} — your choice is hidden until proof is generated`;
  document.getElementById('btn-vote-prove').disabled = false;
}

function syncSalarySlider(val) {
  document.getElementById('salary-input').value = val;
  document.getElementById('slider-val').textContent = '$' + Number(val).toLocaleString();
}
