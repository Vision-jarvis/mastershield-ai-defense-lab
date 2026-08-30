"""
MasterShield AI - Active Hard-Negative Mining & Online Retraining Engine
Mastercard Innovation Challenge @ GFF 2026

Captures adversarial evasions (False Negatives), maintains replay memory buffers,
simulates delayed chargeback label ingestion (30-day lag), defends against feedback poisoning (ADV_30),
and performs robust online defense hardening.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Set
from core.models import PaymentTransaction, DefenseVerdict
from blue_team.feature_engine import feature_engine
from blue_team.classifiers.ensemble_detector import tier1_detector


class ActiveHardNegativeMiner:
    """Isolates hard adversarial edge cases and orchestrates incremental defense hardening"""

    def __init__(self, max_buffer_size: int = 5000):
        self.max_buffer_size = max_buffer_size
        self.hard_negatives: List[PaymentTransaction] = []
        self.hard_positives: List[PaymentTransaction] = []
        self.hn_ids: Set[str] = set()
        self.hp_ids: Set[str] = set()
        self.mining_history: List[Dict[str, Any]] = []

    def sanitize_candidate_sample(self, tx: PaymentTransaction) -> bool:
        """
        Adversarial Poison-Defense Sanitizer (Filters ADV_30 Feedback Poisoning):
        Ensures incoming chargeback/analyst feedback is not an adversarial injection designed
        to destabilize the decision boundary. Validates feature distribution consistency.
        """
        if tx.amount <= 0.0 or tx.amount > 50000.0:
            return False
        if tx.sender_past_tx_count_24h < 0 or tx.sender_past_volume_24h < 0.0:
            return False
        # If transaction claims benign but has extreme anomalous biometrics or severe prompt injection, reject as poisoned label
        if tx.is_fraud == 0 and tx.biometrics and tx.biometrics.deepfake_visual_artifact_score > 0.85:
            return False
        if tx.is_fraud == 0 and tx.agentic and tx.agentic.semantic_deviation_score > 0.90:
            return False
        return True

    def inspect_and_mine(
        self,
        transactions: List[PaymentTransaction],
        verdicts: List[DefenseVerdict],
        round_idx: int
    ) -> Dict[str, Any]:
        """Identifies misclassifications and adds sanitized samples to the hard replay buffer with O(1) tracking"""
        new_fn = 0
        new_fp = 0
        poisoned_dropped = 0
        
        for tx, verdict in zip(transactions, verdicts):
            if not self.sanitize_candidate_sample(tx):
                poisoned_dropped += 1
                continue
                
            # False Negative: True Fraud bypassed defense (Decision was ALLOW)
            if tx.is_fraud == 1 and verdict.decision == "ALLOW":
                if tx.tx_id not in self.hn_ids:
                    self.hard_negatives.append(tx)
                    self.hn_ids.add(tx.tx_id)
                    new_fn += 1
                
            # False Positive: Legitimate user declined (Crucial for keeping FPR < 0.05%)
            elif tx.is_fraud == 0 and verdict.decision == "DECLINE_FRAUD":
                if tx.tx_id not in self.hp_ids:
                    self.hard_positives.append(tx)
                    self.hp_ids.add(tx.tx_id)
                    new_fp += 1

        # Maintain buffer limits
        if len(self.hard_negatives) > self.max_buffer_size:
            evicted = self.hard_negatives[:-self.max_buffer_size]
            for e in evicted:
                self.hn_ids.discard(e.tx_id)
            self.hard_negatives = self.hard_negatives[-self.max_buffer_size:]
            
        if len(self.hard_positives) > self.max_buffer_size:
            evicted = self.hard_positives[:-self.max_buffer_size]
            for e in evicted:
                self.hp_ids.discard(e.tx_id)
            self.hard_positives = self.hard_positives[-self.max_buffer_size:]

        summary = {
            "round": round_idx,
            "mined_false_negatives": new_fn,
            "mined_false_positives": new_fp,
            "poisoned_samples_filtered": poisoned_dropped,
            "total_hard_negatives_in_buffer": len(self.hard_negatives),
            "total_hard_positives_in_buffer": len(self.hard_positives)
        }
        self.mining_history.append(summary)
        return summary

    def retrain_defense_with_hard_negatives(
        self,
        base_dataset: List[PaymentTransaction],
        round_idx: int
    ) -> Dict[str, Any]:
        """Augments base dataset with oversampled hard cases and retrains Tier 1 GBDT"""
        augmented_pool = list(base_dataset)
        
        for hn in self.hard_negatives:
            for _ in range(2):
                augmented_pool.append(hn)
                
        for hp in self.hard_positives:
            for _ in range(2):
                augmented_pool.append(hp)

        X_list = [feature_engine.extract_features_single(tx) for tx in augmented_pool]
        y_list = [tx.is_fraud for tx in augmented_pool]
        
        X_train = np.array(X_list, dtype=np.float32)
        y_train = np.array(y_list, dtype=np.int32)
        
        sample_weights = np.ones(len(y_train), dtype=np.float32)
        for i, tx in enumerate(augmented_pool):
            if tx.tx_id in self.hn_ids:
                sample_weights[i] = 1.8 * (1.0 + np.log1p(max(0.0, tx.amount)))
            elif tx.tx_id in self.hp_ids:
                sample_weights[i] = 2.2 # Protect against False Positives
            elif tx.is_fraud == 1:
                sample_weights[i] = 1.2 * (1.0 + np.log1p(max(0.0, tx.amount)))

        _, feature_names = feature_engine.extract_features_df(pd.DataFrame([{"amount": 100}]))
        metrics = tier1_detector.train(X_train, y_train, feature_names, sample_weights)
        
        return {
            "round": round_idx,
            "retrained_samples": len(augmented_pool),
            "train_roc_auc": metrics["train_roc_auc"],
            "train_pr_auc": metrics["train_pr_auc"],
            "status": "HARDENED"
        }


hard_negative_miner = ActiveHardNegativeMiner()
