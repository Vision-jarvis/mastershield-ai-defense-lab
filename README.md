# MasterShield AI: Autonomous Closed-Loop Red/Blue Defense Lab for Next-Gen Payment Security

[![Mastercard Innovation Challenge @ GFF 2026](https://img.shields.io/badge/Mastercard_Innovation_Challenge-GFF_2026-EB001B.svg)](https://globalfintechfest.com)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production_API-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Tests Passing](https://img.shields.io/badge/Tests-9%2F9_Passing-00E599.svg)]()
[![ROC-AUC](https://img.shields.io/badge/ROC--AUC-0.9768-00F0FF.svg)]()
[![Precision](https://img.shields.io/badge/Precision-100.0%25-F79E1B.svg)]()

> **Submission for the Mastercard Innovation Challenge @ Global Fintech Fest (GFF) 2026, Mumbai**  
> **Track:** AI Defense Lab for Payment Security · *Build the attack, then build the defense.*

---

## 📌 Executive Summary & The Closed-Loop Paradigm

Generative AI has fundamentally shifted payment fraud economics. Modern payment networks face novel, dynamic, and automated attack vectors that bypass traditional static velocity rules, siloed heuristic models, and point-in-time KYC checks:
- **Agentic Commerce Goal Drift & Hijacking:** Indirect prompt injection targeting autonomous AI procurement agents.
- **Polymorphic Synthetic Identity Clustering (PSIC):** Diffusion-generated KYC identities coordinated in sleeper bust-out rings.
- **Sub-Perceptual Behavioral Biometric Evasion:** GAN-generated human mouse and keystroke dynamics mimicking genuine biological distributions.
- **Micro-Structuring & MCC Hopping:** Reinforcement-learning transaction fragmentation slipping beneath static velocity rules.
- **Multimodal 3DS 2.3 Deepfake Bypasses:** Real-time neural voice clones and 3D facial synthesis defeating step-up challenges.
- **Active Learning Feedback Poisoning:** Adversarial boundary perturbations targeting online retraining buffers.

**MasterShield AI** is an end-to-end, closed-loop adversarial defense lab that **unifies the three pillars into a continuous self-reinforcing co-evolutionary cycle**:
1. **IDENTIFY:** Exhaustive threat taxonomy mapping **30 emerging threat vectors** across 6 fraud families in the *Mastercard Payment Adversarial Matrix (MPAM v2.0)*, with **10 active generator families fully simulated**.
2. **GENERATE:** High-fidelity synthetic generation pipeline featuring persistent 2,500 cardholder communities, rolling entity transaction history accumulation, heavy-tailed MCC amounts, and diurnal seasonality.
3. **DEFEND:** Multi-tiered real-time defense engine combining Tier-1 HistGBDT Ensemble (<1.5ms) with cost-sensitive sample weighting, Tier-2 Dynamic Streaming Graph Anomaly Network ($O(1)$ flow balance and cycle detection), and Tier-3 Multimodal Semantic & Homoglyph Guards.
4. **CLOSED-LOOP:** Active Hard-Negative Mining with Poison-Defense Sanitization continuously captures evasions and retrains the blue team decision boundary.

---

## 🏛️ System Architecture

```
                                  ┌─────────────────────────────────────────────────────────┐
                                  │       RED TEAM ADVERSARIAL GENERATOR & MUTATOR          │
                                  │   (Agentic, Synthetic KYC, Biometric GAN, Mule Swarm)    │
                                  └───────────────────────────┬─────────────────────────────┘
                                                              │ Synthetic Attack Stream
                                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                MASTERSHIELD AI: MULTI-TIER REAL-TIME DEFENSE PIPELINE                                 │
│                                                                                                                        │
│   ┌───────────────────────────┐    ┌───────────────────────────┐    ┌───────────────────────────┐                     │
│   │   TIER 1: HISTGBDT ENSEMBLE│    │   TIER 2: GRAPH ENGINE    │    │   TIER 3: SEMANTIC GUARD  │                     │
│   │  - 32 Clean Physical Feats│    │  - Streaming Flow Graph G │    │  - Prompt Injection Scanner│                     │
│   │  - Cost-Sensitive Weight  │    │  - O(1) Flow Balance / Cyc│    │  - VPA Homoglyph Guard    │                     │
│   │  - Latency: < 1.5ms       │    │  - Latency: < 1.0ms (O(1))│    │  - Latency: < 1.2ms       │                     │
│   └─────────────┬─────────────┘    └─────────────┬─────────────┘    └─────────────┬─────────────┘                     │
│                 │                                │                                │                                   │
│                 └────────────────────────────────┼────────────────────────────────┘                                   │
│                                                  ▼                                                                    │
│                                ┌───────────────────────────────────┐                                                  │
│                                │   CONTINUOUS PROBABILITY FUSION   │                                                  │
│                                │ (Structural Overrides for Safety) │                                                  │
│                                └─────────────────┬─────────────────┘                                                  │
└──────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┘
                                                   │
               ┌───────────────────────────────────┴───────────────────────────────────┐
               ▼                                                                       ▼
┌──────────────────────────────┐                                        ┌──────────────────────────────┐
│  ACTIVE LEARNING SANITIZER   │                                        │   ISO 20022 COMPLIANCE HUB   │
│  - Hard-Negative Mining      │                                        │  - pacs.002 Rejection (AGNT) │
│  - Poison-Defense Filter     │                                        │  - camt.056 Payment Recall   │
│  - Automated Retraining Loop │                                        │  - Coalitional Occlusion SHAP│
└──────────────┬───────────────┘                                        └──────────────────────────────┘
               │
               └────────────────────── Feedback Loop to Red Team ───────────────────────►
```

---

## 🎯 Pillar 1: IDENTIFY — Threat Taxonomy (MPAM v2.0)

MasterShield AI formalizes the **Mastercard Payment Adversarial Matrix (MPAM v2.0)**: **30 emerging threat vectors mapped**, with **10 active generator families fully simulated**:

| Vector Code | Attack Family | Attack Vector Name | Target Rail & ISO Type | Rejection Code | Simulation Status |
|:---|:---|:---|:---|:---:|:---:|
| **ADV_01** | Agentic Commerce | Agentic Commerce Wallet Hijack (ACWH) | Agentic AP2P / `pain.001` | `X-MC-AGNT` | **Simulated** |
| **ADV_02** | Agentic Commerce | Prompt-Injected Dispute Hallucination | Cross-Border / `camt.056` | `FRAD` | **Simulated** |
| **ADV_06** | Synthetic Identity | Polymorphic Synthetic Sleeper Clusters | Card E-com / `pacs.008` | `X-MC-SYNI` | **Simulated** |
| **ADV_11** | Biometric Evasion | Sub-Perceptual Biometric Evasion (SP-BBS) | 3DS 2.3 / `AuthRequest` | `X-MC-BIOM` | **Simulated** |
| **ADV_12** | Biometric Evasion | Multimodal Deepfake 3DS 2.3 Step-Up | 3DS 2.3 / `BiometricStepUp` | `X-MC-BIOM` | **Simulated** |
| **ADV_16** | Payment Routing | Adversarial Payment Router Evaporation | Card Present EMV / `pacs.008` | `AM23` | **Simulated** |
| **ADV_21** | Real-Time Rails | Dynamic QR & VPA Semantic Camouflage | UPI Real-Time / `pacs.008_UPI` | `X-MC-QRSP` | **Simulated** |
| **ADV_22** | Real-Time Rails | APP Scam Multi-Turn LLM Grooming | FedNow / `pacs.008` | `FRAD` | **Simulated** |
| **ADV_26** | Graph Laundering | Low-Centrality Autonomous Mule Swarm | FedNow / `pacs.008` | `X-MC-MULE` | **Simulated** |
| **ADV_28** | Graph Laundering | Cyclic Multi-Hop Round-Trip Laundering | FedNow / `pacs.008` | `X-MC-MULE` | **Simulated** |
| **ADV_30** | Graph Laundering | Active Learning Feedback Poisoning | Card E-com / `pacs.008` | `FRAD` | **Simulated** |

---

## 📊 Empirical Benchmark Results (Exact Artifact Run)

Measured on a streaming holdout dataset of **20,000 transactions** at realistic **0.50% fraud prevalence** (99 fraud samples, n=9 per vector) under strict sequential zero-lookahead conditions ($G_{t-1} \to \text{score} \to \text{ingest} \to G_t$):

| Evaluation Metric | Static Rules Engine | Standalone Tier 1 GBDT | MasterShield Unified Defense |
|:---|:---:|:---:|:---:|
| **ROC-AUC Score** | N/A | 0.9733 | **0.9768** |
| **PR-AUC Score (at 0.5% Prev)** | N/A | 0.8871 | **0.8856** |
| **Detection Recall** | 40.40% | 79.80% | **80.81%** |
| **Precision (at 0.5% Prev)** | 2.93% | 100.00%* | **100.00%*** |
| **F1-Score** | 0.0546 | 0.8876 | **0.8939** |
| **False Positive Rate (FPR)** | 6.658% | 0.0000%* | **0.0000%*** |
| **Prevented Fraud Dollars** | N/A | N/A | **$356,006.01 (90.3%)** |
| **Latency Profile** | 0.15 ms | 1.10 ms | **P99: 17.47 ms (Avg: 4.96 ms, 97.86% < 9.8ms SLA)** |

*\* Note on Precision & FPR: 100.00% precision / 0.0000% FPR (0 false positives across 19,901 benign transactions) is the modal baseline on single-threaded execution; multi-core thread scheduling observes 91.86% precision / 0.035% FPR (7 false positives out of 19,901 benign transactions).*

### 🔬 Multi-Tier Arbitration Tradeoff
Tier 1 GBDT provides the core continuous statistical ranking. High-confidence structural signals ($P_{\text{graph}} > 0.85$ or $P_{\text{semantic}} > 0.85$) act as safety overrides, elevating recall from **79.80% to 80.81% (+1.01pp)** while preserving high precision on this test stream.

### 🔬 Controlled Account Warm-Up Ablation Finding (Zero Graph Lookahead)
Evaluated across the exact same 99 fraud transactions without graph lookahead where attacking accounts were seasoned with 4–8 organic prior transactions and realistic volume scaling ($\text{past\_vol} = \text{amount} \times U(0.8, 3.0)$):
- **Baseline Recall:** **80.81%**
- **Warmed-Up Evasion Recall:** **79.80%** (Delta: 1.01% drop)
- **Methodological Note:** Our preliminary warm-up ablation measured a 1.01% delta when isolated from graph state. Fully isolating streaming graph topological evolution from warm-up substitutions requires replaying the 20,000 transaction stream end-to-end.

### 🔬 Adversarial Evasion Gaps & The Feedback Poisoning Frontier (n=9 per vector)
- **High Detection Recall (100.0%):** `ADV_01` (Agentic Hijack), `ADV_02` (Dispute Hallucination), `ADV_06` (Synthetic Identity), `ADV_12` (Deepfake Step-Up), `ADV_21` (Dynamic QR Camouflage), `ADV_26` (Mule Swarm), `ADV_28` (Cyclic Transit Wash).
- **Subtle Evasion Vectors:** `ADV_16` Router Evaporation (88.9%), `ADV_22` APP Scam Grooming (88.9%).
- **Sub-Perceptual Biometrics Gap (`ADV_11`):** **11.11% Recall (1/9 declined, 1 stepped up)**. Recurrent GAN-synthesized cursor tremors match genuine human distributions, evading single-transaction anomaly thresholds.
- **Active Poisoning Gap (`ADV_30`):** **0.0% point-of-sale recall (0/9 declined)**. In our evaluation, `ADV_30` boundary-perturbation attacks bypass point-of-sale scoring and pass candidate sanitization checks (since perturbations operate subtly within benign physical limits: $\text{deepfake} \le 0.11$, $\text{semantic deviation} = 0.0$, $\text{amount} < \$1,000$). This demonstrates an open closed-loop vulnerability where poisoned chargeback feedback reaches the retraining buffer. Building adaptive statistical isolation forest filters derived from measured `ADV_30` boundary distributions is the immediate next co-evolutionary research frontier.

### ⚡ Latency Profile & Stand-In Processing (STIP) Path
- **Mean Latency:** **4.96 ms** (P50: 4.70 ms, P90: 6.15 ms, P95: 6.83 ms).
- **P99 Latency:** **17.47 ms** (97.86% compliance against 9.8ms SLA).
- **Max Latency Tail:** Spans **49.0–129.1 ms** across runs depending on initial cold-start NetworkX cache allocations. In production card authorization networks, requests exceeding 100ms fall back to Stand-In Processing (STIP); compiling the graph engine into C++ / GraphBLAS is the designated deployment path to eliminate cold-start spikes.

### 🔁 Reproducibility Note
Seeded initialization makes data generation and call sequences deterministic. `HistGradientBoostingClassifier` histogram binning is OpenMP thread-order sensitive across different CPU core counts; pinning environment thread variables (`OMP_NUM_THREADS=1`) reproduces the exact single-threaded baseline.

---

## 🚀 Quick Start Guide

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/Vision-jarvis/mastershield-ai-defense-lab.git
cd mastershield-ai-defense-lab

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Comprehensive Benchmarks (20,000 Transactions)
```bash
python scripts/run_benchmark.py --samples 20000 --fraud-ratio 0.005
```

### 3. Run Autonomous Closed-Loop Co-Evolution Hardening
```bash
python scripts/run_co_evolution.py --rounds 5 --samples-per-round 3000
```

### 4. Launch the Interactive Web Cockpit
```bash
python web_app/server.py --port 8000
# Open your browser at http://localhost:8000
```

### 5. Generate the Solution Walkthrough Document (.docx)
```bash
python scripts/generate_docs.py
# Produces: Mastercard_AI_Defense_Lab_Solution_Walkthrough.docx
```

### 6. Run Test Suite
```bash
pytest tests/ -v
```

---

## 📜 Submission Artifacts Checklist

- [x] **1. Code Repository:** Complete, runnable, clean, documented architecture (`config/`, `core/`, `red_team/`, `blue_team/`, `closed_loop/`, `web_app/`, `tests/`, `scripts/`).
- [x] **2. Solution Walkthrough Document:** Word document (`Mastercard_AI_Defense_Lab_Solution_Walkthrough.docx`) detailing threat taxonomy, mathematical formulations, simulation engine, multi-tier defense, benchmark results, and production payment deployment blueprint.
- [x] **3. Working Web Prototype:** Production FastAPI + Real-Time WebSocket dark-mode cybersecurity cockpit with Mastercard brand aesthetics, live simulation stream, dynamic graph visualizer, attack injection studio, SHAP explainability, and ISO 20022 message payload inspector.
- [x] **4. Final Technical Summary Report:** [`MasterShield_AI_Defense_Lab_Final_Report.md`](./MasterShield_AI_Defense_Lab_Final_Report.md).

---

## 👥 Authors & Recognition
- **MasterShield AI Team** · Mastercard Innovation Challenge @ GFF 2026 (9–11 September, Jio World Centre, Mumbai).
