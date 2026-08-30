# MasterShield AI: Autonomous Closed-Loop Red/Blue Defense Lab for Next-Generation Payment Security

**Mastercard Innovation Challenge @ Global Fintech Fest (GFF) 2026, Mumbai**  
*Track: AI Defense Lab for Payment Security · Build the attack, then build the defense.*

---

## Executive Summary

Generative AI has fundamentally shifted the economics of financial crime. In 2026, payment networks face automated, multi-agent fraud campaigns that evade legacy rule engines and siloed machine learning detectors:
- **Agentic Commerce Hijacking:** Prompt-injected directives in merchant catalog feeds that silently override AI procurement agent budgets and routing accounts.
- **Polymorphic Synthetic Identity Clustering (PSIC):** Diffusion-generated KYC dossiers with 6-month organic credit seasoning operating in synchronized sleeper bust-out rings.
- **Sub-Perceptual Behavioral Biometric Evasion:** Recurrent GAN-synthesized cursor Bézier trajectories and keystroke flight dynamics matching human distributions.
- **Adversarial Payment Router Evaporation:** Reinforcement learning agents splitting balances into micro-chunks (<$25) distributed across heterogeneous merchant categories.
- **Active Learning Retraining Poisoning:** Adversarial boundary perturbations designed to distort online blue team decision boundaries.

**MasterShield AI** establishes an end-to-end autonomous defense laboratory where synthetic adversarial campaigns serve as the continuous training ground for an enterprise multi-tier defense architecture.

---

## 1. Scientific Leakage Audit & Experimental Rigor

To ensure absolute scientific validity matching Mastercard's tier-1 security standards, we purged all cosmetic artifacts and synthetic leakage:
1. **Shared Entity Namespace:** Senders and receivers share an authentic pool of masked PANs (`541288******4921`), IBANs (`US88BANK1290384719`), and VPAs (`user@okhdfcbank`). Raw identifier string lengths are strictly prohibited from the feature space.
2. **Dynamic Entity Velocity State:** Replaced static algebraic velocity sampling with continuous 24-hour rolling state tracking across a persistent pool of 2,500 cardholders. Volume ratios and transaction counts naturally overlap between benign and malicious traffic.
3. **Zero-Lookahead Sequential Streaming:** Evaluated strictly in streaming order: each transaction $t$ is evaluated against prior graph state $G_{t-1}$ before being ingested into $G_t$.
4. **Continuous Probability Fusion:** Eliminated artificial probability clamping `[0.001, 0.999]`, preserving full ranking resolution and fine-grained continuous scores.
5. **Controlled Account Warm-Up Ablation:** Evaluated on the identical seeded $n=99$ fraud population with organic 6-month prior histories and scaled volume without graph lookahead.

---

## 2. MPAM v2.0 Threat Taxonomy: 30 Mapped Vectors, 10 Fully Simulated

| Vector Code | Attack Family | Target Payment Rail | ISO 20022 Reason Code | Simulation Status |
|:---|:---|:---|:---:|:---:|
| **ADV_01** | Agentic Commerce | Agentic AP2P / `pain.001` | `X-MC-AGNT` | **Simulated** |
| **ADV_02** | Agentic Commerce | Cross-Border / `camt.056` | `FRAD` | **Simulated** |
| **ADV_06** | Synthetic Identity | Card E-com / `pacs.008` | `X-MC-SYNI` | **Simulated** |
| **ADV_11** | Biometric Evasion | 3DS 2.3 / `AuthRequest` | `X-MC-BIOM` | **Simulated** |
| **ADV_12** | Biometric Evasion | 3DS 2.3 / `BiometricStepUp` | `X-MC-BIOM` | **Simulated** |
| **ADV_16** | Payment Routing | Card Present EMV / `pacs.008` | `AM23` | **Simulated** |
| **ADV_21** | Real-Time Rails | UPI Real-Time / `pacs.008_UPI` | `X-MC-QRSP` | **Simulated** |
| **ADV_22** | Real-Time Rails | FedNow / `pacs.008` | `FRAD` | **Simulated** |
| **ADV_26** | Graph Laundering | FedNow / `pacs.008` | `X-MC-MULE` | **Simulated** |
| **ADV_28** | Graph Laundering | FedNow / `pacs.008` | `X-MC-MULE` | **Simulated** |
| **ADV_30** | Graph Laundering | Card E-com / `pacs.008` | `FRAD` | **Simulated** |

---

## 3. Multi-Tier Real-Time Defense Architecture

```
[ Incoming ISO 20022 pacs.008 / pain.001 / 3DS Stream ]
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
 [ Real-Time Feature Engine ]   [ Streaming Graph G_{t-1} ]
  (32 Clean Physical Features)   (Incremental Flow Balance & Cycles)
       │                               │
       ├───────────────────────────────┤
       ▼                               ▼
 [ Tier 1: HistGBDT Ensemble ]  [ Tier 2: Graph Anomaly ]  [ Tier 3: Semantic Guard ]
  (High-Dimensional Ranking)     (O(1) Flow Score & Cycles) (Prompt & VPA Homoglyphs)
       │                               │                          │
       └───────────────────────────────┼──────────────────────────┘
                                       ▼
                       [ Continuous Probability Fusion ]
                                       ▼
                      [ Final Authorization Verdict ]
                  ALLOW  /  CHALLENGE_STEPUP  /  DECLINE_FRAUD
                                       │
                      [ Automated ISO 20022 pacs.002 ]
                     (X-MC-AGNT, X-MC-SYNI, X-MC-BIOM, etc.)
```

---

## 4. Empirical Benchmark Results (20,000 Transactions @ 0.50% Prevalence)

Measured on a streaming holdout dataset of **20,000 transactions** (99 fraud samples, n=9 per vector) with zero future lookahead:

| Metric | Static Rules Engine | Standalone Tier 1 GBDT | MasterShield Unified Defense |
|:---|:---:|:---:|:---:|
| **ROC-AUC Score** | N/A | 0.9733 | **0.9768** |
| **PR-AUC Score (0.5% Prevalence)** | N/A | 0.8871 | **0.8856** |
| **Detection Recall** | 40.40% | 79.80% | **80.81%** |
| **Precision (0.5% Prevalence)** | 2.93% | 100.00%* | **100.00%*** |
| **F1-Score** | 0.0546 | 0.8876 | **0.8939** |
| **False Positive Rate (FPR)** | 6.658% | 0.0000%* | **0.0000%*** |
| **Fraud Dollars Prevented** | N/A | N/A | **$356,006.01 (90.3%)** |
| **Latency Profile** | 0.15 ms | 1.10 ms | **P99: 17.47 ms (Avg: 4.96 ms, 97.86% < 9.8ms SLA)** |

*\* Note on Precision & FPR: 100.00% precision / 0.0000% FPR (0 false positives across 19,901 benign transactions) is the modal baseline on single-threaded execution; multi-core thread scheduling observes 91.86% precision / 0.035% FPR (7 false positives out of 19,901 benign transactions).*

### Multi-Tier Arbitration Tradeoff
Tier 1 GBDT provides the core continuous statistical ranking. High-confidence structural signals ($P_{\text{graph}} > 0.85$ or $P_{\text{semantic}} > 0.85$) act as safety overrides, elevating recall from **79.80% to 80.81% (+1.01pp)** while preserving high precision on this test stream.

### Controlled Account Warm-Up Adversarial Evasion Study (Zero Graph Lookahead)
Evaluated across the exact same 99 fraud transactions without graph lookahead where attacking accounts were seasoned with 4–8 organic prior transactions and realistic volume scaling ($\text{past\_vol} = \text{amount} \times U(0.8, 3.0)$):
- **Baseline Recall:** **80.81%**
- **Warmed-Up Evasion Recall:** **79.80%** (Delta: 1.01% drop)
- **Methodological Note:** Our preliminary warm-up ablation measured a 1.01% delta when isolated from graph state. Fully isolating streaming graph topological evolution from warm-up substitutions requires replaying the 20,000 transaction stream end-to-end.

### Adversarial Evasion Gaps & The Feedback Poisoning Frontier (n=9 per vector)
- **100.0% Recall:** `ADV_01` (Agentic Hijack), `ADV_02` (Dispute Hallucination), `ADV_06` (Synthetic Identity), `ADV_12` (Deepfake Step-Up), `ADV_21` (Dynamic QR Camouflage), `ADV_26` (Mule Swarm), `ADV_28` (Cyclic Transit Wash).
- **Subtle Evasion Vectors:** `ADV_16` Router Evaporation (88.9%), `ADV_22` APP Scam Grooming (88.9%).
- **Sub-Perceptual Biometrics Gap (`ADV_11`):** **11.11% Recall (1/9 declined, 1 stepped up)**. Recurrent GAN-synthesized cursor tremors match genuine human distributions, evading single-transaction anomaly thresholds.
- **Active Poisoning Gap (`ADV_30`):** **0.0% point-of-sale recall (0/9 declined)**. In our evaluation, `ADV_30` boundary-perturbation attacks bypass point-of-sale scoring and pass candidate sanitization checks (since perturbations operate subtly within benign physical limits: $\text{deepfake} \le 0.11$, $\text{semantic deviation} = 0.0$, $\text{amount} < \$1,000$). This demonstrates an open closed-loop vulnerability where poisoned chargeback feedback reaches the retraining buffer. Building adaptive statistical isolation forest filters derived from measured `ADV_30` boundary distributions is the immediate next co-evolutionary research frontier.

### Latency Profile & Stand-In Processing (STIP) Path
- **Mean Latency:** **4.96 ms** (P50: 4.70 ms, P90: 6.15 ms, P95: 6.83 ms).
- **P99 Latency:** **17.47 ms** (97.86% compliance against 9.8ms SLA).
- **Max Latency Tail:** Spans **49.0–129.1 ms** across runs depending on initial cold-start NetworkX cache allocations. In production card authorization networks, requests exceeding 100ms fall back to Stand-In Processing (STIP); compiling the graph engine into C++ / GraphBLAS is the designated deployment path to eliminate cold-start spikes.

### Reproducibility Note
Seeded initialization makes data generation and call sequences deterministic. `HistGradientBoostingClassifier` histogram binning is OpenMP thread-order sensitive across different CPU core counts; pinning environment thread variables (`OMP_NUM_THREADS=1`) reproduces the exact single-threaded baseline.

---

## 5. Submission Artifacts & Deliverables

1. **Complete Python Codebase:** Fully runnable, modular, clean repository with 9/9 unit and integration tests passing (`pytest tests/ -v`).
2. **Professional Solution Walkthrough:** Word document (`Mastercard_AI_Defense_Lab_Solution_Walkthrough.docx`) synchronized with exact empirical benchmark measurements.
3. **Interactive Web Prototype:** FastAPI cybersecurity dashboard with real-time WebSocket streaming, interactive graph canvas, and ISO 20022 payload inspector.
4. **Final Technical Summary Report:** [`MasterShield_AI_Defense_Lab_Final_Report.md`](./MasterShield_AI_Defense_Lab_Final_Report.md).
