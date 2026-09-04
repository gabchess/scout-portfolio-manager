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
  if (!res.ok) {
    throw new Error(`${path} responded ${res.status}`);
  }
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

/* ---------- Technical Analysis (calculate) ---------- */

function renderTa(data) {
  const el = $("#ta-body");
  if (data.status !== "ok") {
    el.innerHTML = `<p class="placeholder">Analysis unavailable: ${esc(
      data.error?.message || data.error || "unknown error",
    )}</p>`;
    return;
  }
  const ind = data.indicators || {};
  const range = ind.range_30d;
  const rangeText =
    range != null ? `${usd(range.low)} &ndash; ${usd(range.high)}` : "&mdash;";
  const drawdown = ind.drawdown_from_cost_basis_pct;
  const cls = (n) => (n == null ? "" : n >= 0 ? "pos" : "neg");
  const sign = (n) => (n >= 0 ? "+" : "");
  const stale = data.freshness?.stale;

  const staleHtml = stale
    ? `<div class="callout callout-question"><b>Price data is stale.</b> Last observed price: ${esc(
        data.freshness.last_price_date,
      )} (max allowed age: ${data.freshness.max_age_days}d).</div>`
    : "";
  const unknownHtml = data.unknown.length
    ? `<div class="callout callout-question">${esc(data.unknown.join("; "))}</div>`
    : "";

  el.innerHTML = `
    <div class="ta-asset">
      <span class="sym">${esc(data.asset)}</span>
      <span class="conf conf-${esc(data.confidence)}">confidence: ${esc(data.confidence)}</span>
    </div>
    <div class="ta-stats">
      <div class="stat"><div class="k">SMA 20</div><div class="v">${
        ind.sma_20 != null ? usd(ind.sma_20) : "&mdash;"
      }</div></div>
      <div class="stat"><div class="k">EMA 12</div><div class="v">${
        ind.ema_12 != null ? usd(ind.ema_12) : "&mdash;"
      }</div></div>
      <div class="stat"><div class="k">RSI 14</div><div class="v">${
        ind.rsi_14 != null ? ind.rsi_14 : "&mdash;"
      }</div></div>
      <div class="stat"><div class="k">30d range</div><div class="v">${rangeText}</div></div>
      <div class="stat"><div class="k">Drawdown vs. basis</div>
        <div class="v ${cls(drawdown)}">${
          drawdown != null ? `${sign(drawdown)}${drawdown}%` : "&mdash;"
        }</div></div>
    </div>
    ${staleHtml}${unknownHtml}
    <div class="disclosure-strip">
      <span class="pill pill-heuristic">heuristic, not backtested</span>
    </div>
    <div class="formula">${esc(data.disclosure)}</div>`;
}

async function loadTa() {
  const el = $("#ta-body");
  el.innerHTML = `<p class="loading">Loading indicators…</p>`;
  try {
    const data = await getJSON("/api/analyze");
    renderTa(data);
  } catch (err) {
    el.innerHTML = `<p class="placeholder">Analysis unavailable: ${esc(err.message)}</p>`;
  }
}

/* ---------- DCA Windows (propose) ---------- */

function renderDcaWindow(data) {
  const el = $("#dca-windows-body");
  if (data.status !== "ok") {
    el.innerHTML = `<p class="placeholder">DCA window unavailable: ${esc(
      data.error?.message || data.error || "unknown error",
    )}</p>`;
    return;
  }
  const staleHtml = data.freshness?.stale
    ? `<div class="callout callout-question"><b>Price data is stale.</b> This classification is based on stale data.</div>`
    : "";
  const amountHtml =
    data.suggested_amount_usd != null
      ? `<div class="field"><div class="k">Suggested amount</div><div class="v">${usd(
          data.suggested_amount_usd,
        )}</div></div>`
      : "";
  el.innerHTML = `
    <span class="window-label window-${esc(data.label)}">${esc(data.label)} window</span>
    <div class="intent-grid">
      <div class="field"><div class="k">Asset</div><div class="v">${esc(data.asset)}</div></div>
      <div class="field"><div class="k">Risk profile</div><div class="v">${esc(data.risk_profile)}</div></div>
      <div class="field"><div class="k">Sizing fraction</div><div class="v">${data.sizing_fraction}</div></div>
      ${amountHtml}
    </div>
    <div class="formula">${esc(data.rationale)}</div>
    <div class="formula">${esc(data.sensitivity_note)}</div>
    ${staleHtml}
    <div class="disclosure-strip">
      <span class="pill pill-heuristic">heuristic, not backtested</span>
      <span class="pill">${esc(data.not_financial_advice)}</span>
    </div>`;
}

async function loadDcaWindow() {
  const el = $("#dca-windows-body");
  el.innerHTML = `<p class="loading">Loading DCA window…</p>`;
  const riskProfile = $("#risk-profile-select").value;
  try {
    const data = await getJSON(
      `/api/dca-windows?risk_profile=${encodeURIComponent(riskProfile)}`,
    );
    renderDcaWindow(data);
  } catch (err) {
    el.innerHTML = `<p class="placeholder">DCA window unavailable: ${esc(err.message)}</p>`;
  }
}

/* ---------- Alerts (calculate) ---------- */

function renderAlerts(data) {
  const el = $("#alerts-body");
  if (data.status !== "ok") {
    el.innerHTML = `<p class="placeholder">Alerts unavailable: ${esc(
      data.error?.message || data.error || "unknown error",
    )}</p>`;
    return;
  }
  const { fired, not_fired, unknown } = data;
  if (!fired.length && !not_fired.length && !unknown.length) {
    el.innerHTML = `
      <p class="placeholder">No alerts set. This host stores alert rules in
      <code>.scout/alerts.json</code> via <code>set_alert</code>; none exist yet.</p>
      <div class="formula">${esc(data.not_financial_advice)}</div>`;
    return;
  }
  const row = (e, kind) => `<div class="alert-row ${kind}">
      <span class="alert-tag">${kind === "fired" ? "fired" : "quiet"}</span>
      <span>${esc(e.asset)} &middot; ${esc(e.kind)} &middot; observed ${esc(
        e.observed_value,
      )} vs. threshold ${esc(e.threshold)}${e.stale ? " &middot; stale" : ""}</span>
    </div>`;
  const rows =
    fired.map((e) => row(e, "fired")).join("") +
    not_fired.map((e) => row(e, "not-fired")).join("");
  const unknownHtml = unknown.length
    ? `<div class="callout callout-question">${esc(unknown.join("; "))}</div>`
    : "";
  el.innerHTML = `${rows}${unknownHtml}<div class="formula">${esc(
    data.not_financial_advice,
  )}</div>`;
}

async function loadAlerts() {
  const el = $("#alerts-body");
  el.innerHTML = `<p class="loading">Checking alert rules…</p>`;
  try {
    const data = await getJSON("/api/alerts");
    renderAlerts(data);
  } catch (err) {
    el.innerHTML = `<p class="placeholder">Alerts unavailable: ${esc(err.message)}</p>`;
  }
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

$("#risk-profile-select").addEventListener("change", loadDcaWindow);

loadTa();
loadDcaWindow();
loadAlerts();

Promise.allSettled([getJSON("/api/snapshot"), getJSON("/api/pnl")]).then(
  ([snapshotResult, pnlResult]) => {
    const snapshot =
      snapshotResult.status === "fulfilled" ? snapshotResult.value : null;

    if (snapshotResult.status === "fulfilled") {
      renderSnapshot(snapshot);
    } else {
      $("#snapshot-body").innerHTML =
        `<p class="placeholder">Snapshot unavailable: ${esc(
          snapshotResult.reason?.message || String(snapshotResult.reason),
        )}</p>`;
    }

    if (pnlResult.status === "fulfilled") {
      renderPnl(pnlResult.value, snapshot);
    } else {
      $("#pnl-body").innerHTML = `<p class="placeholder">PnL unavailable: ${esc(
        pnlResult.reason?.message || String(pnlResult.reason),
      )}</p>`;
    }
  },
);
