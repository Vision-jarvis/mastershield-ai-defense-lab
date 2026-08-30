"""
MasterShield AI - Autonomous Red/Blue Co-Evolutionary Engine
Mastercard Innovation Challenge @ GFF 2026

Coordinates multi-round adversarial co-evolution with seed-disjoint holdout validation:
Red mutates attack parameters to find blind spots; Blue isolates hard-negatives and hardens its decision frontier.
"""

import time
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

from core.models import PaymentTransaction, DefenseVerdict
from red_team.pipeline import red_team_sim
from red_team.adversarial_optimizer import AdversarialEvolutionaryOptimizer
from blue_team.classifiers.unified_engine import defense_engine
from blue_team.classifiers.ensemble_detector import tier1_detector
from blue_team.classifiers.graph_anomaly import tier2_graph_detector
from blue_team.online_learning import hard_negative_miner
from blue_team.feature_engine import feature_engine
from config.config import defense_cfg, system_cfg


class CoEvolutionEngine:
    """Master Closed-Loop Co-Evolutionary Orchestrator"""

    def __init__(self, rounds: int = 5, seed: int = 42):
        self.rounds = rounds
        self.seed = seed
        self.red_optimizer = AdversarialEvolutionaryOptimizer(seed=seed)
        self.round_history: List[Dict[str, Any]] = []

    def run_full_coevolution(
        self,
        base_samples_per_round: int = 4000,
        fraud_ratio: float = 0.05,
        rounds: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Executes full multi-round adversarial hardening cycle with seed-disjoint holdout splits"""
        num_rounds = rounds or self.rounds
        print(f"[*] Initializing MasterShield AI Co-Evolution Loop ({num_rounds} Rounds)...")
        
        # Reset dynamic graph state for clean training
        tier2_graph_detector.reset_state()

        # Round 0: Initial Seed Training
        print("[+] Round 0: Generating initial seed dataset & training baseline defense...")
        initial_dataset = red_team_sim.generate_synthetic_dataset(
            total_samples=base_samples_per_round,
            fraud_ratio=fraud_ratio,
            round_idx=0,
            seed=self.seed
        )
        
        # Seed Graph with initial benign & attack edges
        tier2_graph_detector.update_graph(initial_dataset)
        
        # Train initial Tier 1 model
        X_init = np.array([feature_engine.extract_features_single(tx) for tx in initial_dataset], dtype=np.float32)
        y_init = np.array([tx.is_fraud for tx in initial_dataset], dtype=np.int32)
        _, f_names = feature_engine.extract_features_df(pd.DataFrame([{"amount": 50}]))
        tier1_detector.train(X_init, y_init, f_names)
        
        # Evaluate initial baseline on an independent holdout split (seed=1000)
        holdout_0 = red_team_sim.generate_synthetic_dataset(
            total_samples=1500,
            fraud_ratio=fraud_ratio,
            round_idx=0,
            seed=1000
        )
        verdicts_0 = [defense_engine.evaluate_transaction(tx) for tx in holdout_0]
        self._record_round_metrics(0, holdout_0, verdicts_0, "INITIAL_BASELINE")

        # Start Co-Evolution Rounds 1 to K
        current_attack_pool = [tx for tx in initial_dataset if tx.is_fraud == 1]
        
        for r in range(1, num_rounds + 1):
            print(f"\n[>>>] --- CO-EVOLUTION ROUND {r} OF {num_rounds} ---")
            
            # Step A: Red Team Evolving Attacks
            print(f"  [Red Team] Mutating and evolving attack population against current defense...")
            evolved_attacks = self.red_optimizer.evolve_population(
                attack_pool=current_attack_pool,
                verdicts=[v for tx, v in zip(holdout_0, verdicts_0) if tx.is_fraud == 1][:len(current_attack_pool)],
                round_idx=r
            )
            
            # Generate new benign volume for this training round with deterministic seed
            rng = np.random.RandomState(self.seed + 100 * r)
            benign_batch = [
                red_team_sim.generate_benign_transaction(round_idx=r)
                for _ in range(int(base_samples_per_round * (1 - fraud_ratio)))
            ]
            
            # Combine into round training batch
            round_train_batch = benign_batch + evolved_attacks
            rng.shuffle(round_train_batch)
            
            # Step B: Blue Team Evaluates Incoming Training Batch & Mines Hard Negatives
            print(f"  [Blue Team] Real-time scoring {len(round_train_batch)} incoming training transactions...")
            train_verdicts = []
            for tx in round_train_batch:
                v = defense_engine.evaluate_transaction(tx)
                train_verdicts.append(v)
                tier2_graph_detector.ingest_single_transaction(tx)
                
            # Step C: Active Hard-Negative Mining
            mine_res = hard_negative_miner.inspect_and_mine(round_train_batch, train_verdicts, r)
            print(f"  [Active Learning] Mined {mine_res['mined_false_negatives']} False Negatives & {mine_res['mined_false_positives']} False Positives.")
            
            # Step D: Blue Team Retraining & Decision Boundary Hardening
            print(f"  [Blue Team] Retraining decision boundary with mined hard-negatives...")
            hard_negative_miner.retrain_defense_with_hard_negatives(round_train_batch, r)
            
            # Step E: Post-Hardening Evaluation on SEED-DISJOINT Holdout Test Split (seed=2000+r)
            holdout_test = red_team_sim.generate_synthetic_dataset(
                total_samples=1500,
                fraud_ratio=fraud_ratio,
                round_idx=r,
                seed=2000 + r
            )
            test_verdicts = [defense_engine.evaluate_transaction(tx) for tx in holdout_test]
            self._record_round_metrics(r, holdout_test, test_verdicts, "HOLD_OUT_EVALUATION")
            
            # Update attack pool for next round
            current_attack_pool = [tx for tx in round_train_batch if tx.is_fraud == 1]
            holdout_0 = holdout_test
            verdicts_0 = test_verdicts

        print("\n[SUCCESS] MasterShield AI Co-Evolution Finished Successfully.")
        return self.round_history

    def _record_round_metrics(
        self,
        round_idx: int,
        transactions: List[PaymentTransaction],
        verdicts: List[DefenseVerdict],
        phase: str
    ):
        """Calculates and logs symmetric round metrics on unseen holdout splits"""
        y_true = np.array([tx.is_fraud for tx in transactions])
        y_pred_probs = np.array([v.fraud_probability for v in verdicts])
        decisions = [v.decision for v in verdicts]
        
        # Binary prediction strictly at calibrated decision threshold
        tau = tier1_detector.decision_threshold
        y_pred = np.where(y_pred_probs >= tau, 1, 0)
        
        total_tx = len(transactions)
        total_fraud = int(np.sum(y_true == 1))
        total_benign = int(np.sum(y_true == 0))
        
        tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        fn = int(np.sum((y_true == 1) & (y_pred == 0)))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        tn = int(np.sum((y_true == 0) & (y_pred == 0)))
        
        recall = tp / max(1, total_fraud)
        precision = tp / max(1, tp + fp)
        fpr = fp / max(1, total_benign)
        f1 = 2 * (precision * recall) / max(1e-5, (precision + recall))
        
        latencies = [v.total_latency_ms for v in verdicts]
        avg_lat = float(np.mean(latencies))
        p99_lat = float(np.percentile(latencies, 99))
        
        evasion_rate = fn / max(1, total_fraud)
        
        round_summary = {
            "round": round_idx,
            "phase": phase,
            "total_transactions": total_tx,
            "fraud_count": total_fraud,
            "recall": round(recall, 4),
            "precision": round(precision, 4),
            "fpr": round(fpr, 5),
            "f1_score": round(f1, 4),
            "evasion_rate": round(evasion_rate, 4),
            "avg_latency_ms": round(avg_lat, 2),
            "p99_latency_ms": round(p99_lat, 2),
            "sla_compliant": p99_lat < system_cfg.TOTAL_P99_SLA_MS
        }
        
        print(f"    --> Round {round_idx} Result: Recall={round_summary['recall']:.2%}, FPR={round_summary['fpr']:.4%}, F1={round_summary['f1_score']:.4f}, EvasionRate={round_summary['evasion_rate']:.2%}, P99 Latency={p99_lat:.2f}ms")
        self.round_history.append(round_summary)


coevolution_engine = CoEvolutionEngine()
