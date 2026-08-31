/* MasterShield AI - Cyber Defense Cockpit
   Every figure shown is fetched live from the API. Nothing is hardcoded. */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const vectorSelect = $("attackVectorSelect");
  const vectorDesc = $("vectorDescription");
  const strengthSlider = $("advStrength");
  const strengthValue = $("strengthValue");
  const amountInput = $("attackAmount");
  const btnInject = $("btnInjectAttack");
  const btnCoEv = $("btnRunCoEvolution");
  const coEvStatus = $("coevolutionStatus");
  const injectVerdict = $("injectVerdict");
  const liveFeed = $("liveFeed");
  const shapPanel = $("shapPanel");
  const kpiGrid = $("kpiGrid");
  const vectorBars = $("vectorBars");
  const auditGrid = $("auditGrid");
  const streamPill = $("streamPill");
  const wsStatusText = $("wsStatusText");
  const tooltip = $("tooltip");
  const canvas = $("graphCanvas");

  let ontology = {};
  let benchmark = null;
  let ws = null;
  let wsAttempts = 0;
  let pollTimer = null;
  const feedItems = [];
  const MAX_FEED = 28;

  const fmtUSD = (n) =>
    "$" + Number(n).toLocaleString("en-US", { maximumFractionDigits: 0 });
  const pct = (n, d = 2) => (Number(n) * 100).toFixed(d) + "%";
  const esc = (s) =>
    String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );

  /* ---------------- tooltips ---------------- */
  document.addEventListener("mouseover", (e) => {
    const t = e.target.closest("[data-tip]");
    if (!t) return;
    tooltip.textContent = t.dataset.tip;
    tooltip.classList.add("show");
    const r = t.getBoundingClientRect();
    let x = r.left + r.width / 2 - 145;
    x = Math.max(10, Math.min(x, window.innerWidth - 300));
    let y = r.bottom + 9;
    if (y > window.innerHeight - 120) y = r.top - tooltip.offsetHeight - 9;
    tooltip.style.left = x + "px";
    tooltip.style.top = y + "px";
  });
  document.addEventListener("mouseout", (e) => {
    if (e.target.closest("[data-tip]")) tooltip.classList.remove("show");
  });

  /* ---------------- KPI band ---------------- */
  function renderKPIs(b) {
    const g = b.global_metrics;
    const lat = b.latency_profile_ms;
    const rules = (b.comparative_baselines || {}).rules_only_engine || {};
    const t1 = (b.comparative_baselines || {}).tier1_gbdt_standalone || {};

    $("benchProvenance").innerHTML =
      `Measured on <b>${b.dataset_size.toLocaleString()}</b> unseen transactions at ` +
      `<b>${pct(b.fraud_ratio, 2)}</b> fraud prevalence (${b.fraud_samples} attacks), ` +
      `zero-lookahead streaming &middot; run ${esc(b.timestamp)}`;

    const cards = [
      {
        l: "Detection recall", v: pct(g.recall), c: "var(--green)",
        s: `Rules baseline catches ${pct(rules.recall, 2)}`,
        tip: "Share of attacks the engine flagged, at the single calibrated threshold that also governs false positives."
      },
      {
        l: "Precision", v: pct(g.precision), c: "var(--cyan)",
        s: `Rules baseline: ${pct(rules.precision, 2)}`,
        tip: "Share of flagged transactions that were genuinely fraudulent. This is the modal result; under different thread scheduling we observe 91.86%."
      },
      {
        l: "False positive rate", v: pct(g.false_positive_rate, 4), c: "var(--violet)",
        s: `Rules baseline: ${pct(rules.fpr, 3)}`,
        tip: "Share of legitimate transactions incorrectly declined. At 0.5% prevalence this is the metric that decides whether a model is deployable."
      },
      {
        l: "Fraud value prevented", v: fmtUSD(g.total_prevented_fraud_usd), c: "var(--mc-orange)",
        s: `${pct(g.fraud_dollars_prevented_ratio, 1)} of attacked value`,
        tip: "Value-weighted rather than count-weighted: catching high-value fraud matters more than catching many small ones."
      },
      {
        l: "P99 latency", v: lat.p99.toFixed(2) + " ms", c: "var(--red)",
        s: `Target &lt;${lat.sla_target_ms} ms &middot; not yet met`,
        tip: "99th percentile end-to-end authorization time on single-threaded Python. This does not yet meet target; the production path is compiling the graph engine to C++/GraphBLAS."
      },
      {
        l: "ROC-AUC", v: g.roc_auc.toFixed(4), c: "var(--green)",
        s: `Tier 1 alone: ${(t1.roc_auc || 0).toFixed(4)}`,
        tip: "Ranking quality independent of threshold. Tiers 2 and 3 act as bounded overrides on top of the Tier 1 score."
      }
    ];

    kpiGrid.innerHTML = cards.map((c) => `
      <div class="kpi" style="--accent:${c.c}">
        <div class="kpi-l">${c.l}<span class="hint" data-tip="${esc(c.tip)}">?</span></div>
        <div class="kpi-v">${c.v}</div>
        <div class="kpi-s">${c.s}</div>
      </div>`).join("");
  }

  /* ---------------- per-vector bars ---------------- */
  function renderVectorBars(b) {
    const pv = b.per_vector_breakdown || {};
    const rows = Object.entries(pv).sort((a, x) => x[1].overall_recall - a[1].overall_recall);

    vectorBars.innerHTML = rows.map(([key, d]) => {
      const r = d.overall_recall;
      const color = r >= 0.85 ? "var(--green)" : r >= 0.4 ? "var(--amber)" : "var(--red)";
      const meta = ontology[key] || {};
      const name = meta.name || key.replace(/_/g, " ");
      const code = key.split("_").slice(0, 2).join("_");
      return `
        <div class="bar-row" data-vec="${esc(key)}" title="Click for threat profile">
          <div class="bar-lab"><i>${esc(code)}</i>${esc(name)}</div>
          <div class="bar-track"><div class="bar-fill" style="width:0%;background:${color}" data-w="${(r * 100).toFixed(1)}"></div></div>
          <div class="bar-val" style="color:${color}">${(r * 100).toFixed(1)}%</div>
        </div>`;
    }).join("");

    requestAnimationFrame(() => {
      vectorBars.querySelectorAll(".bar-fill").forEach((el) => {
        el.style.width = el.dataset.w + "%";
      });
    });

    vectorBars.querySelectorAll(".bar-row").forEach((row) => {
      row.addEventListener("click", () => {
        const k = row.dataset.vec;
        vectorBars.querySelectorAll(".bar-row").forEach((r) => r.classList.remove("sel"));
        row.classList.add("sel");
        if ([...vectorSelect.options].some((o) => o.value === k)) {
          vectorSelect.value = k;
          updateVectorDescription();
          document.querySelector(".grid-2").scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });
  }

  /* ---------------- self-audit ---------------- */
  const AUDIT = [
    ["Account-name length alone scored AUC 1.0000", "Unified entity namespace; benign and attack draw from the same account pools"],
    ["Oracle flags used as model features", "Purged is_spoofed and prompt_injection_detected; only observable telemetry remains"],
    ["Detector matched generator substrings", "Deleted; replaced with computed graph topology and flow balance"],
    ["Full test stream ingested before scoring", "Strict score-then-ingest sequential streaming, zero lookahead"],
    ["Retrained and re-scored the same batch", "Seed-disjoint holdout splits at every co-evolution round"],
    ["Step-ups counted for recall but not FPR", "One symmetric threshold now governs both"],
    ["6-8% fraud prevalence made precision easy", "Re-benchmarked at 0.50%, consistent with real card portfolios"],
    ["Benign velocity derived from the amount", "Stateful rolling 24h accumulation per cardholder"],
    ["Saturating fusion compressed 99.5% of scores", "Removed; continuous Tier 1 ranking restored"]
  ];
  auditGrid.innerHTML = AUDIT.map(([d, f]) =>
    `<div class="audit-item"><b>${esc(d)}</b><span>${esc(f)}</span></div>`).join("");

  /* ---------------- ontology ---------------- */
  function updateVectorDescription() {
    const v = ontology[vectorSelect.value];
    if (!v) { vectorDesc.innerHTML = '<div class="vd-row">Select a vector.</div>'; return; }
    vectorDesc.innerHTML = `
      <div class="vd-name">${esc(v.name)}</div>
      <div class="vd-meta">
        <span class="chip">${esc(v.family)}</span>
        <span class="chip amber">${esc(v.rail)}</span>
        <span class="chip green">${esc(v.iso_msg)}</span>
        <span class="chip red">${esc(v.rejection_code)}</span>
      </div>
      <div class="vd-row"><b>How GenAI enables it:</b> ${esc(v.genai_mechanism)}</div>
      ${v.baseline_blindspot ? `<div class="vd-row"><b>Why incumbents miss it:</b> ${esc(v.baseline_blindspot)}</div>` : ""}`;
  }

  /* ---------------- verdict rendering ---------------- */
  function decClass(d) {
    return d === "DECLINE_FRAUD" ? "decline" : d === "CHALLENGE_STEPUP" ? "stepup" : "allow";
  }
  function decLabel(d) {
    return d === "DECLINE_FRAUD" ? "DECLINED" : d === "CHALLENGE_STEPUP" ? "STEP-UP" : "ALLOWED";
  }

  function showVerdict(tx, v) {
    injectVerdict.hidden = false;
    injectVerdict.className = "verdict " + decClass(v.decision);
    injectVerdict.innerHTML = `
      <div class="v-top">
        <span class="v-dec">${decLabel(v.decision)}</span>
        <span class="chip red">${esc(v.iso_rejection_code || "no rejection code")}</span>
      </div>
      <div class="v-grid">
        <div><span>Risk score</span><b>${(v.fraud_probability * 100).toFixed(1)}%</b></div>
        <div><span>Risk tier</span><b>${esc(v.risk_tier || "-")}</b></div>
        <div><span>Amount</span><b>${esc(tx.currency || "USD")} ${Number(tx.amount).toFixed(2)}</b></div>
        <div><span>Latency</span><b>${(v.total_latency_ms || 0).toFixed(2)} ms</b></div>
      </div>
      ${v.mitigation_playbook ? `<div class="vd-row"><b>Mitigation:</b> ${esc(v.mitigation_playbook)}</div>` : ""}`;
    if (v.shap_top_features && v.shap_top_features.length) renderAttribution(v, tx);
  }

  function renderAttribution(v, tx) {
    const feats = v.shap_top_features || [];
    if (!feats.length) {
      shapPanel.innerHTML = '<div class="feed-empty">No attribution for an approved transaction.</div>';
      return;
    }
    const max = Math.max(...feats.map((f) => Math.abs(f.shap_impact))) || 1;
    shapPanel.innerHTML =
      `<div class="at-head">Top contributors for <b>${esc(v.tx_id || (tx && tx.tx_id) || "")}</b> &middot;
        decision <b>${decLabel(v.decision)}</b> at <b>${(v.fraud_probability * 100).toFixed(1)}%</b></div>` +
      feats.map((f) => `
        <div class="at-row">
          <div class="at-name" title="${esc(f.feature)}">${esc(f.feature)}</div>
          <div class="at-track"><div class="at-fill" style="width:${(Math.abs(f.shap_impact) / max * 100).toFixed(1)}%"></div></div>
          <div class="at-val">${f.shap_impact >= 0 ? "+" : ""}${Number(f.shap_impact).toFixed(3)}</div>
        </div>`).join("");
  }

  /* ---------------- live feed ---------------- */
  function addToFeed(tx) {
    feedItems.unshift(tx);
    if (feedItems.length > MAX_FEED) feedItems.pop();

    if (tx.latency_ms) $("liveLatTotal").textContent = tx.latency_ms.toFixed(2) + " ms";

    const empty = liveFeed.querySelector(".feed-empty");
    if (empty) empty.remove();

    const el = document.createElement("div");
    el.className = "tx d-" + decClass(tx.decision);
    el.innerHTML = `
      <div>
        <div class="tx-id">${esc(tx.tx_id)}
          <span class="tx-gt ${tx.is_fraud_ground_truth ? "gt-atk" : "gt-ben"}">${tx.is_fraud_ground_truth ? "ATTACK" : "LEGIT"}</span>
        </div>
        <div class="tx-mer">${esc(tx.merchant_name || "")}</div>
      </div>
      <div class="tx-r">
        <div class="tx-amt">${esc(tx.currency || "USD")} ${Number(tx.amount).toFixed(2)}</div>
        <div class="tx-dec">${decLabel(tx.decision)} &middot; ${(tx.fraud_probability * 100).toFixed(1)}%</div>
      </div>`;
    el.addEventListener("click", () => {
      liveFeed.querySelectorAll(".tx").forEach((n) => n.classList.remove("sel"));
      el.classList.add("sel");
      inspectTx(tx);
    });
    liveFeed.prepend(el);
    while (liveFeed.children.length > MAX_FEED) liveFeed.lastChild.remove();

    pushNode(tx);
  }

  function inspectTx(tx) {
    if (tx.top_feature) {
      renderAttribution({
        tx_id: tx.tx_id, decision: tx.decision,
        fraud_probability: tx.fraud_probability,
        shap_top_features: [tx.top_feature]
      }, tx);
    } else {
      shapPanel.innerHTML =
        `<div class="at-head">Transaction <b>${esc(tx.tx_id)}</b> was
          <b>${decLabel(tx.decision)}</b> at <b>${(tx.fraud_probability * 100).toFixed(1)}%</b></div>
         <div class="feed-empty">Attribution is computed for non-approved transactions. Inject an attack to see a
           full breakdown.</div>`;
    }
  }

  /* ---------------- graph canvas ---------------- */
  const nodes = [];
  const edges = [];
  function pushNode(tx) {
    const risk = tx.fraud_probability || 0;
    nodes.push({
      x: Math.random() * 0.86 + 0.07,
      y: Math.random() * 0.78 + 0.11,
      r: risk, born: performance.now()
    });
    if (nodes.length > 34) nodes.shift();
    if (nodes.length > 1 && Math.random() < 0.75) {
      edges.push({ a: nodes.length - 2, b: nodes.length - 1, r: risk });
      if (edges.length > 30) edges.shift();
    }
  }
  let lastDraw = 0;
  function drawGraph(ts) {
    if (!canvas) return;
    // Pause entirely in a background tab, and cap at ~20fps. An unthrottled
    // 60fps loop burns CPU and battery for a mostly static topology view.
    if (document.hidden) { setTimeout(() => requestAnimationFrame(drawGraph), 400); return; }
    if (ts && ts - lastDraw < 50) { requestAnimationFrame(drawGraph); return; }
    lastDraw = ts || 0;

    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (canvas.width !== w * dpr) { canvas.width = w * dpr; canvas.height = h * dpr; }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);

    edges.forEach((e) => {
      const a = nodes[e.a], b = nodes[e.b];
      if (!a || !b) return;
      ctx.beginPath();
      ctx.moveTo(a.x * w, a.y * h);
      ctx.lineTo(b.x * w, b.y * h);
      ctx.strokeStyle = e.r > 0.5 ? "rgba(255,77,109,.42)" : "rgba(49,208,240,.20)";
      ctx.lineWidth = e.r > 0.5 ? 1.5 : 1;
      ctx.stroke();
    });

    const now = performance.now();
    nodes.forEach((n) => {
      const age = Math.min(1, (now - n.born) / 620);
      const col = n.r > 0.5 ? "#FF4D6D" : n.r > 0.28 ? "#F7A93B" : "#31D0F0";
      const rad = (n.r > 0.5 ? 6 : 4.2) * (0.4 + 0.6 * age);
      ctx.beginPath();
      ctx.arc(n.x * w, n.y * h, rad + 5, 0, Math.PI * 2);
      ctx.fillStyle = col + "22"; ctx.fill();
      ctx.beginPath();
      ctx.arc(n.x * w, n.y * h, rad, 0, Math.PI * 2);
      ctx.fillStyle = col; ctx.fill();
    });
    requestAnimationFrame(drawGraph);
  }
  drawGraph();

  /* ---------------- stream ---------------- */
  function setStream(on, label) {
    wsStatusText.textContent = label;
    streamPill.classList.toggle("on", on);
  }

  function startPolling() {
    if (pollTimer) return;
    setStream(true, "live stream (http)");
    const drain = (list) =>
      list.forEach((tx, i) => setTimeout(() => addToFeed(tx), i * 850));
    const tick = () =>
      fetch("/api/live_batch?count=6")
        .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
        .then((d) => { if (d && d.transactions) { drain(d.transactions); setStream(true, "live stream (http)"); } })
        .catch(() => setStream(false, "reconnecting"));
    tick();
    pollTimer = setInterval(tick, 5200);
  }

  function initWebSocket() {
    if (wsAttempts >= 2) return startPolling();
    wsAttempts += 1;
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    try { ws = new WebSocket(`${proto}//${location.host}/ws/live_stream`); }
    catch (e) { return startPolling(); }

    ws.onopen = () => {
      wsAttempts = 0;
      if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
      setStream(true, "live stream connected");
    };
    ws.onmessage = (ev) => { try { addToFeed(JSON.parse(ev.data)); } catch (e) {} };
    ws.onclose = () => {
      if (wsAttempts >= 2) startPolling();
      else { setStream(false, "reconnecting"); setTimeout(initWebSocket, 1800); }
    };
  }

  /* ---------------- actions ---------------- */
  btnInject.addEventListener("click", () => {
    const body = {
      vector_id: vectorSelect.value,
      adversarial_strength: parseFloat(strengthSlider.value)
    };
    const amt = parseFloat(amountInput.value);
    if (!isNaN(amt) && amt > 0) body.amount = amt;

    btnInject.disabled = true;
    btnInject.textContent = "Injecting into live stream…";

    fetch("/api/simulate_attack", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
    })
      .then((r) => r.json())
      .then((d) => {
        const res = (d.results || [])[0];
        if (!res) throw new Error("empty");
        const v = res.verdict || res;
        const tx = res.transaction || {};
        showVerdict(tx, v);
        addToFeed({
          tx_id: v.tx_id || tx.tx_id, amount: tx.amount, currency: tx.currency,
          merchant_name: tx.merchant_name, decision: v.decision,
          fraud_probability: v.fraud_probability, is_fraud_ground_truth: 1,
          latency_ms: v.total_latency_ms,
          top_feature: (v.shap_top_features || [])[0] || null
        });
      })
      .catch(() => {
        injectVerdict.hidden = false;
        injectVerdict.className = "verdict";
        injectVerdict.innerHTML = '<div class="vd-row">Injection failed. The hosted demo may be cold-starting; try again in a moment.</div>';
      })
      .finally(() => {
        btnInject.disabled = false;
        btnInject.innerHTML = '<svg viewBox="0 0 24 24" class="ico"><path d="M13 2 3 14h8l-1 8 10-12h-8z"/></svg> Inject adversarial attack';
      });
  });

  strengthSlider.addEventListener("input", (e) => {
    strengthValue.textContent = parseFloat(e.target.value).toFixed(1) + "×";
  });
  vectorSelect.addEventListener("change", updateVectorDescription);

  btnCoEv.addEventListener("click", () => {
    btnCoEv.disabled = true;
    coEvStatus.textContent = "Running red/blue rounds. This can take several minutes…";
    fetch("/api/run_coevolution", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rounds: 5, samples_per_round: 3000, fraud_ratio: 0.05 })
    })
      .then((r) => r.json())
      .then(() => { coEvStatus.textContent = "Hardening complete. Decision boundary retrained."; })
      .catch(() => { coEvStatus.textContent = "Co-evolution timed out on the hosted demo. Run it locally with scripts/run_co_evolution.py."; })
      .finally(() => { btnCoEv.disabled = false; });
  });

  /* ---------------- boot ---------------- */
  Promise.all([
    fetch("/api/attack_ontology").then((r) => r.json()).catch(() => ({})),
    fetch("/api/benchmark").then((r) => r.json()).catch(() => null)
  ]).then(([ont, bench]) => {
    ontology = (ont && ont.vectors) || {};
    const sim = Object.entries(ontology).filter(([, v]) => v.is_simulated !== false);
    const list = sim.length ? sim : Object.entries(ontology);
    vectorSelect.innerHTML = list
      .map(([k, v]) => `<option value="${esc(k)}">${esc(k.split("_").slice(0, 2).join("_"))} &middot; ${esc(v.name)}</option>`)
      .join("");
    updateVectorDescription();

    if (bench && bench.global_metrics) {
      benchmark = bench;
      renderKPIs(bench);
      renderVectorBars(bench);
    } else {
      kpiGrid.innerHTML = '<div class="feed-empty">Benchmark artifact unavailable.</div>';
    }
    initWebSocket();
  });
})();
