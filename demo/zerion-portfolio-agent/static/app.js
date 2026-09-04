/* Front-end for the Zerion portfolio-manager agent demo.
   Renders read-only host responses; contains no portfolio logic of its own. */

const $ = (sel) => document.querySelector(sel);

const usd = (n) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD" });

// Matches the deck's month abbreviations exactly ("Sept", not Intl's "Sep").
const MONTH_ABBR = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sept",
  "Oct",
  "Nov",
  "Dec",
];
const fmtDate = (iso) => {
  const d = new Date(iso);
  return `${MONTH_ABBR[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`;
};

const esc = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[c],
  );

async function getJSON(path) {
  const res = await fetch(path);
  return res.json();
}

async function postJSON(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

/* ---------- Snapshot (observe) ---------- */

function renderSnapshot(data) {
  const el = $("#snapshot-body");
  if (data.status !== "ok") {
    el.innerHTML = `<p class="placeholder">Snapshot unavailable: ${esc(
      data.error?.message || data.error || "unknown error",
    )}</p>`;
    return;
  }
  const s = data.snapshot;
  $("#source-badge").textContent =
    s.source.kind === "fixture"
      ? "FIXTURE DATA"
      : esc(s.source.kind).toUpperCase();

  const total = s.holdings.reduce((acc, h) => acc + h.value_usd, 0);

  const holdingsRows = s.holdings
    .map(
      (h) => `<tr>
        <td><span class="asset-cell"><span class="asset-dot">${esc(
          h.asset.slice(0, 3),
        )}</span>${esc(h.asset)}</span></td>
        <td class="num">${h.quantity}</td>
        <td class="num">${usd(h.value_usd)}</td>
      </tr>`,
    )
    .join("");

  const txRows = s.transactions
    .map(
      (t) => `<tr>
        <td>${esc(t.kind)}</td>
        <td>${esc(t.asset)}</td>
        <td class="num">${t.quantity}</td>
        <td class="num">${usd(t.value_usd)}</td>
        <td class="num">${usd(t.fee_usd)}</td>
        <td>${esc(t.occurred_at.slice(0, 10))}</td>
      </tr>`,
    )
    .join("");

  el.innerHTML = `
    <div class="kv-row">
      <div class="kv"><div class="k">Wallet</div><div class="v">${esc(s.wallet_address)}</div></div>
      <div class="kv"><div class="k">Chain</div><div class="v">${esc(s.chain)}</div></div>
      <div class="kv"><div class="k">Observed at</div><div class="v">${esc(s.observed_at)}</div></div>
      <div class="kv"><div class="k">Source</div><div class="v">${esc(s.source.kind)} · ${esc(s.source.locator)}</div></div>
    </div>
    <div class="total-value">
      <div class="num">${usd(total)}</div>
      <div class="lbl">total observed value (fixture example, not live market data)</div>
    </div>
    <table>
      <thead><tr><th>Asset</th><th class="num">Quantity</th><th class="num">Value (USD)</th></tr></thead>
      <tbody>${holdingsRows}</tbody>
    </table>
    <div class="subhead">Transaction ledger</div>
    <table>
      <thead><tr><th>Kind</th><th>Asset</th><th class="num">Qty</th><th class="num">Value</th><th class="num">Fee</th><th>Date</th></tr></thead>
      <tbody>${txRows}</tbody>
    </table>`;
}

/* ---------- PnL (calculate) ---------- */

function renderPnl(data, snapshot) {
  const el = $("#pnl-body");
  if (data.status !== "ok") {
    el.innerHTML = `<p class="placeholder">PnL unavailable: ${esc(
      data.error?.message || data.error || "unknown error",
    )}</p>`;
    return;
  }
  const cls = (n) => (n >= 0 ? "pos" : "neg");
  const sign = (n) => (n >= 0 ? "+" : "");
  const snap = snapshot?.status === "ok" ? snapshot.snapshot : null;
  const blocks = data.results
    .map((r) => {
      const buys = (snap?.transactions || []).filter(
        (t) => t.asset === r.asset && t.kind === "buy",
      );
      const basisLine = buys.length
        ? `<div class="formula">Cost basis: bought ${esc(r.asset)} for ${usd(
            buys.reduce((acc, t) => acc + t.value_usd, 0),
          )} on ${fmtDate(buys[0].occurred_at)}.</div>`
        : "";
      const holding = (snap?.holdings || []).find((h) => h.asset === r.asset);
      const valueLine = holding
        ? `<div class="formula">Current value: ${esc(r.asset)} is ${usd(
            holding.value_usd,
          )} in this snapshot (${fmtDate(r.valuation_at)}).</div>`
        : "";
      return `
      <div class="pnl-asset">
        <span class="sym">${esc(r.asset)}</span>
        <span class="conf conf-${esc(r.confidence)}">confidence: ${esc(r.confidence)}</span>
      </div>
      <div class="pnl-stats">
        <div class="stat"><div class="k">Unrealized</div>
          <div class="v ${cls(r.unrealized_usd)}">${sign(r.unrealized_usd)}${usd(r.unrealized_usd)}</div></div>
        <div class="stat"><div class="k">Realized</div>
          <div class="v ${cls(r.realized_usd)}">${sign(r.realized_usd)}${usd(r.realized_usd)}</div></div>
        <div class="stat"><div class="k">Total</div>
          <div class="v ${cls(r.total_usd)}">${sign(r.total_usd)}${usd(r.total_usd)}</div></div>
        <div class="stat"><div class="k">Return</div>
          <div class="v ${cls(r.return_pct)}">${sign(r.return_pct)}${r.return_pct}%</div></div>
      </div>
      ${basisLine}${valueLine}
      <div class="formula"><b>How this was computed:</b> ${esc(r.formula)}
        &nbsp;·&nbsp; basis from observed buy transactions, never inferred
        &nbsp;·&nbsp; valued at ${esc(r.valuation_at)}</div>
      ${r.warnings.length ? `<div class="callout callout-question">${esc(r.warnings.join("; "))}</div>` : ""}`;
    })
    .join(
      "<hr style='border:none;border-top:1px solid var(--border);margin:14px 0'/>",
    );

  const unknown = data.unknown.length
    ? `<div class="callout callout-question">${esc(data.unknown.join("; "))}</div>`
    : "";
  el.innerHTML =
    blocks + unknown || `<p class="placeholder">No PnL results.</p>`;
}

/* ---------- DCA agent (propose / approve) ---------- */

const FIELD_ORDER = [
  "asset",
  "amount_usd",
  "chain",
  "schedule",
  "source",
  "destination",
];

function intentGrid(intent, missing) {
  const cells = FIELD_ORDER.map((name) => {
    const val = intent[name];
    const isMissing = missing.includes(name);
    return `<div class="field ${isMissing ? "field-missing" : ""}">
      <div class="k">${esc(name.replace("_", " "))}</div>
      <div class="v">${isMissing ? "missing, will ask" : esc(name === "amount_usd" ? usd(val) : val)}</div>
    </div>`;
  }).join("");
  return `<div class="intent-grid">${cells}</div>`;
}

function renderDca(parseRes, previewRes) {
  const el = $("#dca-result");

  if (parseRes.status === "needs_clarification") {
    el.innerHTML = `
      <div class="status-line">
        <span class="pill pill-clarify">needs clarification</span>
        <span class="mono-id">boundary: ${esc(parseRes.boundary)}</span>
      </div>
      ${intentGrid(parseRes.intent, parseRes.missing)}
      <div class="callout callout-question">
        <b>Agent asks (never guesses):</b> ${esc(parseRes.question)}
      </div>`;
    return;
  }

  // Parse is ready; show the full preview response.
  const p = previewRes.preview;
  el.innerHTML = `
    <div class="status-line">
      <span class="pill pill-ready">intent complete</span>
      <span class="mono-id">boundary: ${esc(previewRes.boundary)}</span>
    </div>
    ${intentGrid(previewRes.intent, [])}
    <div class="preview-box">
      <h3>
        DCA preview
        <span class="pill pill-approval">approval_state: ${esc(p.approval_state)}</span>
        <span class="pill pill-noexec">execution_available: false</span>
      </h3>
      <div class="intent-grid">
        <div class="field"><div class="k">Expected output</div><div class="v">${p.expected_output} ${esc(p.asset)}</div></div>
        <div class="field"><div class="k">Fees</div><div class="v">${usd(p.fees_usd)}</div></div>
        <div class="field"><div class="k">Slippage</div><div class="v">${p.slippage_pct}%</div></div>
        <div class="field"><div class="k">Max fee</div><div class="v">${usd(p.max_fee_usd)}</div></div>
        <div class="field"><div class="k">Quote expiry</div><div class="v">${esc(p.quote_expiry)}</div></div>
        <div class="field"><div class="k">Preview ID</div><div class="v">${esc(p.preview_id.slice(0, 13))}…</div></div>
      </div>
      <ul class="assumed">
        ${previewRes.assumed.map((a) => `<li>assumed: ${esc(a)}</li>`).join("")}
      </ul>
      <div class="preview-note">${esc(previewRes.note)}</div>
    </div>`;
}

async function runDca(text) {
  const el = $("#dca-result");
  el.innerHTML = `<p class="loading">Parsing request…</p>`;
  const parseRes = await postJSON("/api/dca/parse", { text });
  if (parseRes.status === "error") {
    el.innerHTML = `<p class="placeholder">${esc(parseRes.error)}</p>`;
    return;
  }
  const previewRes =
    parseRes.status === "ready"
      ? await postJSON("/api/dca/preview", { text })
      : null;
  renderDca(parseRes, previewRes);
}

/* ---------- Wire up ---------- */

$("#dca-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const text = $("#dca-input").value.trim();
  if (text) runDca(text);
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    $("#dca-input").value = chip.dataset.example;
    runDca(chip.dataset.example);
  });
});

Promise.all([getJSON("/api/snapshot"), getJSON("/api/pnl")]).then(
  ([snapshot, pnl]) => {
    renderSnapshot(snapshot);
    renderPnl(pnl, snapshot);
  },
);
