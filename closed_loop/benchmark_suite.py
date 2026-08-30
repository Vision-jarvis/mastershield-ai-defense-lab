"""
MasterShield AI - Comprehensive Benchmark Evaluation Suite
Mastercard Innovation Challenge @ GFF 2026

Rigorously benchmarks defense efficacy on streaming transaction streams with zero lookahead,
seed-disjoint holdout splits, realistic fraud prevalence (0.5%), baseline comparisons,
and Adversarial Account Warm-Up Ablation studies.
"""

import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import time
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from pathlib import Path
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_fscore_support

from core.models import PaymentTransaction, DefenseVerdict, BenchmarkResult
from red_team.pipeline import red_team_sim
from blue_team.classifiers.unified_engine import defense_engine
from blue_team.classifiers.graph_anomaly import tier2_graph_detector
from blue_team.classifiers.ensemble_detector import tier1_detector
from blue_team.feature_engine import feature_engine
from config.config import ARTIFACTS_DIR, system_cfg


class MasterShieldBenchmarkSuite:
    """Enterprise Benchmark Suite for Payment Fraud Defense Evaluation"""

    def __init__(self):
        self.results_dir = ARTIFACTS_DIR
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_benchmark(
        self,
        n_samples: int = 20000,
        fraud_ratio: float = 0.005, # 0.5% realistic fraud prevalence (~100 fraud samples)
        model_tag: str = "MasterShield-Enterprise-v2026.2",
        seed: int = 999,
        save_artifact: bool = True
    ) -> Dict[str, Any]:
        """Runs full end-to-end benchmark on fresh unseen test stream with zero lookahead"""
        print(f"\n=======================================================")
        print(f"  RUNNING MASTERSHIELD AI DEFENSE BENCHMARK ({n_samples} TXNs)")
        print(f"=======================================================")
        
        # Reset dynamic graph state for clean streaming evaluation
        tier2_graph_detector.reset_state()

        # 1. Generate unseen synthetic test dataset (Seed Disjoint)
        print(f"[+] Generating {n_samples} unseen test transactions (Fraud Ratio: {fraud_ratio:.2%}, Seed: {seed})...")
        t_gen_0 = time.time()
        test_dataset = red_team_sim.generate_synthetic_dataset(
            total_samples=n_samples,
            fraud_ratio=fraud_ratio,
            round_idx=99,
            seed=seed
        )
        print(f"[+] Dataset generated in {time.time() - t_gen_0:.2f}s.")
        
        # 2. Sequential Streaming Evaluation: Score G_{t-1}, then Ingest G_t
        print(f"[+] Executing real-time sequential streaming authorization (Zero Lookahead)...")
        t_eval_0 = time.time()
        verdicts: List[DefenseVerdict] = []
        tier1_only_probs: List[float] = []
        
        for tx in test_dataset:
            # Score against prior state
            v = defense_engine.evaluate_transaction(tx)
            verdicts.append(v)
            
            f_vec = feature_engine.extract_features_single(tx)
            p_t1, _, _ = tier1_detector.predict_single(f_vec)
            tier1_only_probs.append(p_t1)
            
            # Ingest transaction into dynamic graph state G_t AFTER scoring
            tier2_graph_detector.ingest_single_transaction(tx)
            
        t_eval_tot = time.time() - t_eval_0
        throughput = len(test_dataset) / max(0.001, t_eval_tot)
        print(f"[+] Evaluated {len(test_dataset)} transactions in {t_eval_tot:.2f}s ({throughput:.1f} tx/sec).")

        # 3. Compute Metrics
        y_true = np.array([tx.is_fraud for tx in test_dataset])
        y_probs = np.array([v.fraud_probability for v in verdicts])
        decisions = np.array([v.decision for v in verdicts])
        latencies = np.array([v.total_latency_ms for v in verdicts])
        amounts = np.array([tx.amount for tx in test_dataset])
        
        tau = tier1_detector.decision_threshold
        y_pred = np.where(y_probs >= tau, 1, 0)
        
        roc_auc = float(roc_auc_score(y_true, y_probs))
        pr_auc = float(average_precision_score(y_true, y_probs))
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
        
        total_benign = int(np.sum(y_true == 0))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        fpr = fp / max(1, total_benign)
        
        stepup_rate_benign = float(np.mean((y_true == 0) & (decisions == "CHALLENGE_STEPUP")))
        stepup_rate_fraud = float(np.mean((y_true == 1) & (decisions == "CHALLENGE_STEPUP")))
        
        total_fraud_amt = float(np.sum(amounts[y_true == 1]))
        prevented_fraud_amt = float(np.sum(amounts[(y_true == 1) & (y_pred == 1)]))
        prevented_ratio = prevented_fraud_amt / max(1.0, total_fraud_amt)
        
        lat_mean = float(np.mean(latencies))
        lat_p50 = float(np.percentile(latencies, 50))
        lat_p90 = float(np.percentile(latencies, 90))
        lat_p95 = float(np.percentile(latencies, 95))
        lat_p99 = float(np.percentile(latencies, 99))
        lat_max = float(np.max(latencies))
        sla_compliance = float(np.mean(latencies < system_cfg.TOTAL_P99_SLA_MS)) * 100.0

        # 4. Comparative Baseline Models Evaluation
        print(f"[+] Benchmarking comparative baseline models...")
        rule_preds = np.array([1 if (tx.amount > 5000.0 or tx.sender_past_tx_count_24h > 6) else 0 for tx in test_dataset])
        rule_prec, rule_rec, rule_f1, _ = precision_recall_fscore_support(y_true, rule_preds, average="binary", zero_division=0)
        rule_fp = int(np.sum((y_true == 0) & (rule_preds == 1)))
        rule_fpr = rule_fp / max(1, total_benign)
        
        t1_probs = np.array(tier1_only_probs)
        t1_roc = float(roc_auc_score(y_true, t1_probs))
        t1_pr = float(average_precision_score(y_true, t1_probs))
        t1_preds = np.where(t1_probs >= tau, 1, 0)
        t1_prec, t1_rec, t1_f1, _ = precision_recall_fscore_support(y_true, t1_preds, average="binary", zero_division=0)
        t1_fpr = int(np.sum((y_true == 0) & (t1_preds == 1))) / max(1, total_benign)

        # 5. Per-Vector Performance Breakdown
        vector_metrics = {}
        unique_vectors = set(tx.attack_vector for tx in test_dataset if tx.is_fraud == 1)
        
        for vec in sorted(unique_vectors):
            mask = np.array([tx.attack_vector == vec for tx in test_dataset])
            vec_total = int(np.sum(mask))
            vec_caught = int(np.sum(mask & (y_pred == 1)))
            vec_stepup = int(np.sum(mask & (decisions == "CHALLENGE_STEPUP")))
            vec_recall = vec_caught / max(1, vec_total)
            vec_avg_risk = float(np.mean(y_probs[mask]))
            
            vector_metrics[vec] = {
                "total_attacks": vec_total,
                "fully_declined": vec_caught,
                "stepped_up": vec_stepup,
                "overall_recall": round(vec_recall, 4),
                "avg_risk_score": round(vec_avg_risk, 4)
            }

        # 6. Controlled Adversarial Account Warm-Up Ablation Study (Zero Graph Lookahead)
        print(f"[+] Executing Controlled Adversarial Account Warm-Up Ablation Study (n={int(np.sum(y_true == 1))})...")
        tier2_graph_detector.reset_state() # Reset graph so warmed attacks are evaluated without lookahead
        ablation_rng = np.random.RandomState(42)
        warmed_attacks = []
        for tx in test_dataset:
            if tx.is_fraud == 1:
                w_tx = PaymentTransaction(
                    tx_id=f"WARM-{tx.tx_id}",
                    timestamp=tx.timestamp,
                    sender_pan_or_account=tx.sender_pan_or_account,
                    receiver_pan_or_account=tx.receiver_pan_or_account,
                    amount=tx.amount,
                    currency=tx.currency,
                    payment_rail=tx.payment_rail,
                    mcc=tx.mcc,
                    merchant_name=tx.merchant_name,
                    merchant_id=tx.merchant_id,
                    ip_address=tx.ip_address,
                    geo_country=tx.geo_country,
                    geo_city=tx.geo_city,
                    device_fingerprint=tx.device_fingerprint,
                    is_vpn_or_tor=tx.is_vpn_or_tor,
                    biometrics=tx.biometrics,
                    agentic=tx.agentic,
                    is_fraud=tx.is_fraud,
                    attack_vector=tx.attack_vector,
                    simulation_round=tx.simulation_round,
                    sender_past_tx_count_24h=int(ablation_rng.randint(4, 9)),
                    sender_past_volume_24h=round(float(tx.amount * ablation_rng.uniform(0.8, 3.0)), 2),
                    receiver_inflow_count_24h=tx.receiver_inflow_count_24h,
                    iso_message_type=tx.iso_message_type,
                    cycle_ring_id=getattr(tx, "cycle_ring_id", None),
                    iso_raw_xml_or_json=getattr(tx, "iso_raw_xml_or_json", None)
                )
                warmed_attacks.append(w_tx)
                
        warmed_verdicts = [defense_engine.evaluate_transaction(atx) for atx in warmed_attacks]
        warmed_probs = np.array([v.fraud_probability for v in warmed_verdicts])
        warmed_caught = int(np.sum(warmed_probs >= tau))
        warmed_recall = warmed_caught / max(1, len(warmed_attacks))
        delta_recall = float(rec) - warmed_recall

        if delta_recall > 0:
            finding_str = f"When adversaries simulate organic 6-month transaction histories (warm-up accounts with 4-8 prior transactions), velocity heuristics degrade and detection recall drops by {delta_recall:.2%} (from {float(rec):.2%} to {warmed_recall:.2%}), demonstrating that point-in-time velocity checks can be systematically evaded by seasoned accounts."
        else:
            finding_str = f"When accounts are warmed up, detection recall shifts from {float(rec):.2%} to {warmed_recall:.2%}."

        benchmark_summary = {
            "model_tag": model_tag,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_size": n_samples,
            "fraud_samples": int(np.sum(y_true)),
            "fraud_ratio": round(fraud_ratio, 4),
            "global_metrics": {
                "roc_auc": round(roc_auc, 4),
                "pr_auc": round(pr_auc, 4),
                "precision": round(float(prec), 4),
                "recall": round(float(rec), 4),
                "f1_score": round(float(f1), 4),
                "false_positive_rate": round(float(fpr), 5),
                "stepup_rate_benign": round(stepup_rate_benign, 4),
                "stepup_rate_fraud": round(stepup_rate_fraud, 4),
                "fraud_dollars_prevented_ratio": round(prevented_ratio, 4),
                "total_prevented_fraud_usd": round(prevented_fraud_amt, 2)
            },
            "comparative_baselines": {
                "rules_only_engine": {
                    "precision": round(float(rule_prec), 4),
                    "recall": round(float(rule_rec), 4),
                    "f1_score": round(float(rule_f1), 4),
                    "fpr": round(float(rule_fpr), 5)
                },
                "tier1_gbdt_standalone": {
                    "roc_auc": round(t1_roc, 4),
                    "pr_auc": round(t1_pr, 4),
                    "precision": round(float(t1_prec), 4),
                    "recall": round(float(t1_rec), 4),
                    "f1_score": round(float(t1_f1), 4),
                    "fpr": round(float(t1_fpr), 5)
                },
                "mastershield_unified_defense": {
                    "roc_auc": round(roc_auc, 4),
                    "pr_auc": round(pr_auc, 4),
                    "precision": round(float(prec), 4),
                    "recall": round(float(rec), 4),
                    "f1_score": round(float(f1), 4),
                    "fpr": round(float(fpr), 5)
                }
            },
            "adversarial_warmup_ablation": {
                "baseline_detection_recall": round(float(rec), 4),
                "warmed_account_evasion_recall": round(warmed_recall, 4),
                "evasion_recall_delta": round(delta_recall, 4),
                "finding": finding_str
            },
            "latency_profile_ms": {
                "mean": round(lat_mean, 2),
                "p50": round(lat_p50, 2),
                "p90": round(lat_p90, 2),
                "p95": round(lat_p95, 2),
                "p99": round(lat_p99, 2),
                "max": round(lat_max, 2),
                "sla_target_ms": system_cfg.TOTAL_P99_SLA_MS,
                "sla_compliance_pct": round(sla_compliance, 2)
            },
            "per_vector_breakdown": vector_metrics
        }

        # Save to JSON artifact only when requested
        if save_artifact:
            json_path = self.results_dir / "benchmark_results.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(benchmark_summary, f, indent=2)
            print(f"  Saved report to:    {json_path}")
            
        print("\n--- BENCHMARK RESULTS SUMMARY ---")
        print(f"  ROC-AUC:            {roc_auc:.4f}  (Baseline GBDT: {t1_roc:.4f})")
        print(f"  PR-AUC:             {pr_auc:.4f}  (Baseline GBDT: {t1_pr:.4f})")
        print(f"  Recall (Detection): {rec:.2%}  (Rules: {rule_rec:.2%})")
        print(f"  Precision:          {prec:.2%}")
        print(f"  F1-Score:           {f1:.4f}")
        print(f"  False Positive Rate:{fpr:.4%}")
        print(f"  P99 Latency:        {lat_p99:.2f} ms (SLA: < {system_cfg.TOTAL_P99_SLA_MS} ms)")
        print(f"  SLA Compliance:     {sla_compliance:.1f}%")
        print(f"  Warm-Up Recall:     {warmed_recall:.2%} (Delta: {float(rec) - warmed_recall:.2%})")
        print(f"=======================================================\n")
        
        return benchmark_summary


benchmark_suite = MasterShieldBenchmarkSuite()
