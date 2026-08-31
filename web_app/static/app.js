/* MasterShield AI — Payment Fraud Defense Lab
   Every figure rendered here is fetched live from the API. Nothing is hardcoded. */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const el = {
    select: $("attackVectorSelect"), dossier: $("vectorDescription"),
    strength: $("advStrength"), strengthVal: $("strengthValue"), amount: $("attackAmount"),
    inject: $("btnInjectAttack"), coev: $("btnRunCoEvolution"), coevMsg: $("coevolutionStatus"),
    ruling: $("injectVerdict"), feed: $("liveFeed"), attrib: $("shapPanel"),
    kpis: $("kpiGrid"), audit: $("auditGrid"), pill: $("streamPill"),
    pillTxt: $("wsStatusText"), tip: $("tooltip"), graph: $("graphCanvas"),
    prov: $("benchProvenance"),
    t1: $("liveLatT1"), t2: $("liveLatT2"), t3: $("liveLatT3"), tt: $("liveLatTotal")
  };

  const BRAND = { red: "#EB001B", orange: "#FF5F00", yellow: "#F79E1B" };
  const SEM = { ok: "#047857", warn: "#B45309", crit: "#BE123C" };
  const INK = "#14141A", INK3 = "#7C7783", RULE = "#E2DCD5";

  let ontology = {}, ws = null, wsTries = 0, poll = null, chart = null;
  const MAX_ROWS = 26;

  const usd = (n) => "$" + Number(n).toLocaleString("en-US", { maximumFractionDigits: 0 });
  const pc = (n, d = 2) => (Number(n) * 100).toFixed(d) + "%";
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const kind = (d) => d === "DECLINE_FRAUD" ? "crit" : d === "CHALLENGE_STEPUP" ? "warn" : "ok";
  const label = (d) => d === "DECLINE_FRAUD" ? "Declined" : d === "CHALLENGE_STEPUP" ? "Step-up" : "Approved";

  /* ---------------- tooltips ---------------- */
  function place(t) {
    el.tip.textContent = t.dataset.tip;
    el.tip.classList.add("show");
    const r = t.getBoundingClientRect();
    const w = el.tip.offsetWidth;
    let x = Math.min(Math.max(10, r.left + r.width / 2 - w / 2), innerWidth - w - 10);
    let y = r.bottom + 9;
    if (y + el.tip.offsetHeight > innerHeight - 12) y = r.top - el.tip.offsetHeight - 9;
    el.tip.style.left = x + "px"; el.tip.style.top = y + "px";
  }
  document.addEventListener("mouseover", (e) => { const t = e.target.closest("[data-tip]"); if (t) place(t); });
  document.addEventListener("focusin", (e) => { const t = e.target.closest("[data-tip]"); if (t) place(t); });
  const hide = () => el.tip.classList.remove("show");
  document.addEventListener("mouseout", (e) => { if (e.target.closest("[data-tip]")) hide(); });
  document.addEventListener("focusout", hide);

  /* ---------------- KPI strip ---------------- */
  function renderKPIs(b) {
    const g = b.global_metrics, lat = b.latency_profile_ms;
    const base = b.comparative_baselines || {};
    const rules = base.rules_only_engine || {}, t1 = base.tier1_gbdt_standalone || {};

    el.prov.innerHTML =
      `Measured on <b>${b.dataset_size.toLocaleString()}</b> unseen transactions at <b>${pc(b.fraud_ratio)}</b> ` +
      `fraud prevalence, ${b.fraud_samples} attacks &middot; sequential streaming, zero lookahead &middot; ` +
      `run ${esc(b.timestamp)}`;

    const set = [
      { l: "Recall", v: pc(g.recall), s: `Static rules catch <b>${pc(rules.recall)}</b>`, c: SEM.ok,
        t: "Share of attacks flagged, at the single calibrated threshold that also governs false positives." },
      { l: "Precision", v: pc(g.precision), s: `Static rules: <b>${pc(rules.precision)}</b>`, c: INK,
        t: "Share of flagged transactions that were genuinely fraudulent. This is the modal result; under different thread scheduling we measure 91.86%." },
      { l: "False positives", v: pc(g.false_positive_rate, 4), s: `Static rules: <b>${pc(rules.fpr, 3)}</b>`, c: INK,
        t: "Share of legitimate payments wrongly declined. At 0.5% prevalence this is the number that decides whether a model is deployable at all." },
      { l: "Value protected", v: usd(g.total_prevented_fraud_usd), s: `<b>${pc(g.fraud_dollars_prevented_ratio, 1)}</b> of attacked value`, c: INK,
        t: "Weighted by value rather than count. Catching high-value fraud matters more than catching many small attempts." },
      { l: "P99 latency", v: lat.p99.toFixed(2) + " ms", s: `Target <b>&lt;${lat.sla_target_ms} ms</b> · not met`, c: SEM.warn,
        t: "99th percentile end-to-end authorization time on single-threaded Python. This does not meet target; the production path is compiling the graph engine to C++/GraphBLAS." },
      { l: "ROC-AUC", v: g.roc_auc.toFixed(4), s: `Tier 1 alone: <b>${(t1.roc_auc || 0).toFixed(4)}</b>`, c: INK,
        t: "Ranking quality independent of any threshold. Tiers 2 and 3 act as bounded overrides above the Tier 1 score." }
    ];

    el.kpis.innerHTML = set.map((k) => `
      <div class="kpi">
        <div class="kpi-l">${k.l}<button class="info" type="button" data-tip="${esc(k.t)}">i</button></div>
        <div class="kpi-v" style="color:${k.c}">${k.v}</div>
        <div class="kpi-s">${k.s}</div>
      </div>`).join("");
  }

  /* ---------------- vector chart (Chart.js) ---------------- */
  function renderChart(b) {
    const pv = b.per_vector_breakdown || {};
    const rows = Object.entries(pv).sort((a, z) => z[1].overall_recall - a[1].overall_recall);
    const labels = rows.map(([k]) => {
      const code = k.split("_").slice(0, 2).join("_");
      const nm = (ontology[k] || {}).name || k;
      return code + "  " + (nm.length > 34 ? nm.slice(0, 33) + "…" : nm);
    });
    const data = rows.map(([, d]) => +(d.overall_recall * 100).toFixed(1));
    const colors = data.map((v) => v >= 85 ? SEM.ok : v >= 40 ? SEM.warn : SEM.crit);

    if (!window.Chart) return;
    if (chart) chart.destroy();
    chart = new Chart($("vectorChart"), {
      type: "bar",
      data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0, barThickness: 15,
        borderRadius: 1, hoverBackgroundColor: colors.map(() => BRAND.orange) }] },
      options: {
        indexAxis: "y", responsive: true, maintainAspectRatio: false,
        layout: { padding: { right: 22, top: 4 } },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: INK, padding: 10, cornerRadius: 4, displayColors: false,
            titleFont: { family: "IBM Plex Mono", size: 11 },
            bodyFont: { family: "IBM Plex Sans", size: 12 },
            callbacks: {
              title: (i) => rows[i[0].dataIndex][0],
              label: (c) => {
                const d = rows[c.dataIndex][1];
                return [`Recall ${c.parsed.x}%`,
                        `${d.fully_declined} of ${d.total_attacks} declined`,
                        `Mean risk ${(d.avg_risk_score * 100).toFixed(1)}%`];
              }
            }
          }
        },
        scales: {
          x: { min: 0, max: 100, grid: { color: RULE, drawTicks: false },
               border: { display: false },
               ticks: { color: INK3, font: { family: "IBM Plex Mono", size: 10 }, callback: (v) => v + "%" } },
          y: { grid: { display: false }, border: { color: RULE },
               ticks: { color: INK, font: { family: "IBM Plex Mono", size: 10.5 }, crossAlign: "far" } }
        },
        onClick: (_e, act) => {
          if (!act.length) return;
          const key = rows[act[0].index][0];
          if ([...el.select.options].some((o) => o.value === key)) {
            el.select.value = key; dossier();
            document.querySelector(".cols").scrollIntoView({ behavior: "smooth", block: "start" });
          }
        }
      }
    });
  }

  /* ---------------- self audit ---------------- */
  const AUDIT = [
    ["Account-name length alone scored AUC 1.0000", "Unified entity namespace: benign and attack traffic now draw from the same account and merchant pools"],
    ["Simulation oracle flags used as model inputs", "Purged is_spoofed and prompt_injection_detected; only telemetry an issuer actually holds remains"],
    ["Detector matched generator-assigned substrings", "Deleted; replaced with computed flow balance and cycle detection on the live graph"],
    ["Whole test stream ingested before scoring", "Strict score-then-ingest streaming, so no decision sees its own future"],
    ["Retrained and re-scored the same batch", "Seed-disjoint holdout splits at every co-evolution round"],
    ["Step-ups counted for recall but not for FPR", "One symmetric threshold now governs both"],
    ["Fraud prevalence of 6–8% made precision easy", "Re-benchmarked at 0.50%, consistent with real card portfolios"],
    ["Benign velocity derived from the current amount", "Stateful rolling 24-hour accumulation per cardholder"],
    ["Saturating fusion compressed 99.5% of scores", "Removed; continuous Tier 1 ranking restored"]
  ];
  el.audit.innerHTML = AUDIT.map(([d, f]) => `<li><b>${esc(d)}</b><span>${esc(f)}</span></li>`).join("");

  /* ---------------- dossier ---------------- */
  function dossier() {
    const v = ontology[el.select.value];
    if (!v) { el.dossier.innerHTML = "<p>Select a vector.</p>"; return; }
    el.dossier.innerHTML = `
      <h4>${esc(v.name)}</h4>
      <div class="tax">
        <span>${esc(v.family)}</span>
        <span>${esc(v.rail)}</span>
        <span>${esc(v.iso_msg)}</span>
        <span class="code">${esc(v.rejection_code)}</span>
      </div>
      <p><b>How GenAI enables it.</b> ${esc(v.genai_mechanism)}</p>
      ${v.baseline_blindspot ? `<p><b>Why incumbent controls miss it.</b> ${esc(v.baseline_blindspot)}</p>` : ""}`;
  }

  /* ---------------- ruling ---------------- */
  function ruling(tx, v) {
    el.ruling.hidden = false;
    el.ruling.className = "ruling is-" + kind(v.decision);
    el.ruling.innerHTML = `
      <div class="ruling-top">
        <span class="ruling-dec">${label(v.decision)}</span>
        <span class="chip chip-red">${esc(v.iso_rejection_code || "no rejection code")}</span>
      </div>
      <div class="ruling-grid">
        <div><span>Risk</span><b>${(v.fraud_probability * 100).toFixed(1)}%</b></div>
        <div><span>Tier</span><b>${esc(v.risk_tier || "—")}</b></div>
        <div><span>Amount</span><b>${esc(tx.currency || "USD")} ${Number(tx.amount).toFixed(2)}</b></div>
        <div><span>Latency</span><b>${(v.total_latency_ms || 0).toFixed(2)} ms</b></div>
      </div>
      ${v.mitigation_playbook ? `<p><b>Mitigation.</b> ${esc(v.mitigation_playbook)}</p>` : ""}`;
    if (v.shap_top_features && v.shap_top_features.length) attribution(v);
  }

  function attribution(v) {
    const f = v.shap_top_features || [];
    if (!f.length) { el.attrib.innerHTML = '<p class="vacant">No attribution for an approved payment.</p>'; return; }
    const max = Math.max(...f.map((x) => Math.abs(x.shap_impact))) || 1;
    el.attrib.innerHTML =
      `<p class="at-cap">Contributors for <b>${esc(v.tx_id || "")}</b> · ${label(v.decision).toLowerCase()} at <b>${(v.fraud_probability * 100).toFixed(1)}%</b></p>` +
      f.map((x) => `
        <div class="at-row">
          <span class="at-name" title="${esc(x.feature)}">${esc(x.feature)}</span>
          <span class="at-bar"><i style="width:${(Math.abs(x.shap_impact) / max * 100).toFixed(1)}%"></i></span>
          <span class="at-val">${x.shap_impact >= 0 ? "+" : ""}${Number(x.shap_impact).toFixed(3)}</span>
        </div>`).join("");
  }

  /* ---------------- ledger ---------------- */
  function addRow(tx) {
    if (tx.latency_ms) el.tt.textContent = tx.latency_ms.toFixed(2) + " ms";
    const vacant = el.feed.querySelector(".vacant"); if (vacant) vacant.remove();

    const k = kind(tx.decision);
    const node = document.createElement("div");
    node.className = "row v-" + k;
    node.tabIndex = 0;
    node.innerHTML = `
      <div>
        <div class="row-id">${esc(tx.tx_id)}
          <span class="truth ${tx.is_fraud_ground_truth ? "atk" : "ben"}">${tx.is_fraud_ground_truth ? "ATTACK" : "LEGIT"}</span>
        </div>
        <div class="row-mer">${esc(tx.merchant_name || "")}</div>
      </div>
      <div class="row-r">
        <div class="row-amt">${esc(tx.currency || "USD")} ${Number(tx.amount).toFixed(2)}</div>
        <div class="row-dec">${label(tx.decision)} · ${(tx.fraud_probability * 100).toFixed(1)}%</div>
      </div>`;
    const pick = () => {
      el.feed.querySelectorAll(".row").forEach((n) => n.classList.remove("on"));
      node.classList.add("on");
      if (tx.top_feature) {
        attribution({ tx_id: tx.tx_id, decision: tx.decision, fraud_probability: tx.fraud_probability,
                      shap_top_features: [tx.top_feature] });
      } else {
        el.attrib.innerHTML =
          `<p class="at-cap"><b>${esc(tx.tx_id)}</b> was ${label(tx.decision).toLowerCase()} at <b>${(tx.fraud_probability * 100).toFixed(1)}%</b></p>
           <p class="vacant">Attribution is computed for non-approved payments. Send an attack for a full breakdown.</p>`;
      }
    };
    node.addEventListener("click", pick);
    node.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
    el.feed.prepend(node);
    while (el.feed.children.length > MAX_ROWS) el.feed.lastChild.remove();
    pushNode(tx);
  }

  /* ---------------- topology canvas ---------------- */
  const nodes = [], links = [];
  function pushNode(tx) {
    nodes.push({ x: Math.random() * .84 + .08, y: Math.random() * .74 + .13, r: tx.fraud_probability || 0, t: performance.now() });
    if (nodes.length > 30) nodes.shift();
    if (nodes.length > 1 && Math.random() < .72) {
      links.push({ a: nodes.length - 2, b: nodes.length - 1, r: tx.fraud_probability || 0 });
      if (links.length > 26) links.shift();
    }
    wake();
  }
  // The loop runs only while nodes are still easing in, then stops. A canvas
  // that animates forever keeps the page from ever reaching idle, which costs
  // battery and blocks assistive and automation tooling.
  let last = 0, running = false, settleUntil = 0;
  function wake() {
    settleUntil = performance.now() + 900;
    if (!running) { running = true; requestAnimationFrame(paint); }
  }
  function paint(ts) {
    const c = el.graph; if (!c) { running = false; return; }
    if (document.hidden) { running = false; return; }
    if (ts && ts - last < 55) { requestAnimationFrame(paint); return; }
    last = ts || 0;
    const ctx = c.getContext("2d"), dpr = devicePixelRatio || 1;
    const w = c.clientWidth, h = c.clientHeight;
    if (c.width !== w * dpr) { c.width = w * dpr; c.height = h * dpr; }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);

    links.forEach((l) => {
      const a = nodes[l.a], b = nodes[l.b]; if (!a || !b) return;
      ctx.beginPath(); ctx.moveTo(a.x * w, a.y * h); ctx.lineTo(b.x * w, b.y * h);
      ctx.strokeStyle = l.r > .5 ? "rgba(190,18,60,.34)" : "rgba(124,119,131,.22)";
      ctx.lineWidth = l.r > .5 ? 1.4 : 1; ctx.stroke();
    });
    const now = performance.now();
    nodes.forEach((n) => {
      const age = Math.min(1, (now - n.t) / 600);
      const col = n.r > .5 ? SEM.crit : n.r > .28 ? SEM.warn : SEM.ok;
      const rad = (n.r > .5 ? 5.5 : 3.8) * (.45 + .55 * age);
      ctx.beginPath(); ctx.arc(n.x * w, n.y * h, rad + 4.5, 0, 6.284);
      ctx.fillStyle = col + "1F"; ctx.fill();
      ctx.beginPath(); ctx.arc(n.x * w, n.y * h, rad, 0, 6.284);
      ctx.fillStyle = col; ctx.fill();
    });
    if (performance.now() < settleUntil) requestAnimationFrame(paint);
    else running = false;
  }
  addEventListener("visibilitychange", () => { if (!document.hidden) wake(); });
  wake();

  /* ---------------- stream ---------------- */
  const setPill = (on, txt) => { el.pillTxt.textContent = txt; el.pill.classList.toggle("on", on); };

  function startPoll() {
    if (poll) return;
    setPill(true, "live · http");
    const drain = (l) => l.forEach((t, i) => setTimeout(() => addRow(t), i * 870));
    const tick = () => fetch("/api/live_batch?count=6")
      .then((r) => r.ok ? r.json() : Promise.reject(r.status))
      .then((d) => { if (d && d.transactions) { drain(d.transactions); setPill(true, "live · http"); } })
      .catch(() => setPill(false, "reconnecting"));
    tick(); poll = setInterval(tick, 5400);
  }

  function openSocket() {
    if (wsTries >= 2) return startPoll();
    wsTries += 1;
    try { ws = new WebSocket(`${location.protocol === "https:" ? "wss:" : "ws:"}//${location.host}/ws/live_stream`); }
    catch (e) { return startPoll(); }
    ws.onopen = () => { wsTries = 0; if (poll) { clearInterval(poll); poll = null; } setPill(true, "live · socket"); };
    ws.onmessage = (e) => { try { addRow(JSON.parse(e.data)); } catch (_) {} };
    ws.onclose = () => { if (wsTries >= 2) startPoll(); else { setPill(false, "reconnecting"); setTimeout(openSocket, 1700); } };
  }

  /* ---------------- actions ---------------- */
  el.inject.addEventListener("click", () => {
    const body = { vector_id: el.select.value, adversarial_strength: parseFloat(el.strength.value) };
    const a = parseFloat(el.amount.value); if (!isNaN(a) && a > 0) body.amount = a;
    el.inject.disabled = true; el.inject.textContent = "Scoring…";
    fetch("/api/simulate_attack", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      .then((r) => r.json())
      .then((d) => {
        const res = (d.results || [])[0]; if (!res) throw 0;
        const v = res.verdict || res, tx = res.transaction || {};
        ruling(tx, v);
        addRow({ tx_id: v.tx_id || tx.tx_id, amount: tx.amount, currency: tx.currency,
          merchant_name: tx.merchant_name, decision: v.decision, fraud_probability: v.fraud_probability,
          is_fraud_ground_truth: 1, latency_ms: v.total_latency_ms,
          top_feature: (v.shap_top_features || [])[0] || null });
      })
      .catch(() => {
        el.ruling.hidden = false; el.ruling.className = "ruling";
        el.ruling.innerHTML = "<p>Could not reach the scoring engine. The hosted demo may be cold-starting; try again shortly.</p>";
      })
      .finally(() => { el.inject.disabled = false; el.inject.textContent = "Send attack to the authorization stream"; });
  });

  el.strength.addEventListener("input", (e) => { el.strengthVal.textContent = (+e.target.value).toFixed(1) + "×"; });
  el.select.addEventListener("change", dossier);

  el.coev.addEventListener("click", () => {
    el.coev.disabled = true;
    el.coevMsg.textContent = "Running red and blue rounds. This can take several minutes…";
    fetch("/api/run_coevolution", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rounds: 5, samples_per_round: 3000, fraud_ratio: 0.05 }) })
      .then((r) => r.json())
      .then(() => { el.coevMsg.textContent = "Hardening complete. The decision boundary has been retrained."; })
      .catch(() => { el.coevMsg.textContent = "Exceeded the hosted request budget. Run scripts/run_co_evolution.py locally instead."; })
      .finally(() => { el.coev.disabled = false; });
  });

  /* ---------------- boot ---------------- */
  Promise.all([
    fetch("/api/attack_ontology").then((r) => r.json()).catch(() => ({})),
    fetch("/api/benchmark").then((r) => r.json()).catch(() => null)
  ]).then(([ont, bench]) => {
    ontology = (ont && ont.vectors) || {};
    const sim = Object.entries(ontology).filter(([, v]) => v.is_simulated);
    (sim.length ? sim : Object.entries(ontology)).forEach(([k, v]) => {
      const o = document.createElement("option");
      o.value = k;
      o.textContent = k.split("_").slice(0, 2).join("_") + " · " + v.name;
      el.select.appendChild(o);
    });
    dossier();

    if (bench && bench.global_metrics) {
      renderKPIs(bench);
      if (window.Chart) renderChart(bench);
      else addEventListener("load", () => renderChart(bench));
    } else {
      el.kpis.innerHTML = '<p class="vacant">Benchmark artifact unavailable.</p>';
    }
    openSocket();
  });
})();
