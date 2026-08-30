"""
MasterShield AI - Unified Hierarchical Multi-Tier Defense Engine
Mastercard Innovation Challenge @ GFF 2026

Coordinates Tier 1 (GBDT Ensemble), Tier 2 (Streaming Graph Anomaly), and Tier 3 (Semantic & Homoglyph Guard)
into an enterprise-grade, low-latency payment authorization pipeline.
Tier 1 provides continuous statistical discrimination; Tiers 2 & 3 provide topological and semantic evidence
for ISO 20022 routing, mitigation playbooks, and targeted risk escalation.
"""

import time
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

from core.models import PaymentTransaction, DefenseVerdict
from core.iso20022 import iso_engine
from config.config import system_cfg, rails_cfg
from blue_team.feature_engine import feature_engine
from blue_team.classifiers.ensemble_detector import tier1_detector
from blue_team.classifiers.graph_anomaly import tier2_graph_detector
from blue_team.classifiers.semantic_guard import tier3_semantic_guard


class MasterShieldUnifiedDefenseEngine:
    """Unified AI Defense Engine for Real-Time Payment Authorization"""

    def __init__(self):
        self.tier1 = tier1_detector
        self.tier2 = tier2_graph_detector
        self.tier3 = tier3_semantic_guard
        self.feature_eng = feature_engine

    def _fuse_tier_probabilities(self, p1: float, p2: float, p3: float) -> float:
        """
        Continuous Calibrated Probability Fusion:
        Preserves full fine-grained ranking resolution from Tier 1 without artificial clamping or saturation.
        Specialized graph/semantic signals elevate risk when deterministic structural anomalies are confirmed.
        """
        prob = float(p1)
        if p2 > 0.85:
            prob = max(prob, float(p2))
        if p3 > 0.85:
            prob = max(prob, float(p3))
        return prob

    def evaluate_transaction(self, tx: PaymentTransaction, compute_explainability: bool = False) -> DefenseVerdict:
        """
        Executes end-to-end multi-tier risk evaluation.
        Total SLA budget: < 10.0ms.
        """
        start_time = time.perf_counter()
        
        # 1. Real-Time Feature Extraction (<0.8ms)
        f_vec = self.feature_eng.extract_features_single(tx)
        
        # 2. Tier 1: Quantized Ensemble Inference (<1.2ms)
        p_tier1, d_tier1, lat_t1 = self.tier1.predict_single(f_vec)
        
        # 3. Tier 2: Streaming Graph Anomaly Scoring (<1.0ms)
        p_tier2, meta_t2, lat_t2 = self.tier2.score_transaction(tx)
        
        # 4. Tier 3: Semantic Guard & Agentic Inspection (<1.2ms)
        p_tier3, meta_t3, lat_t3 = self.tier3.evaluate_transaction(tx)
        
        # 5. Multi-Tier Probability Fusion (Continuous, Unclipped)
        fused_prob = self._fuse_tier_probabilities(p_tier1, p_tier2, p_tier3)
        
        # Determine Decision & Risk Tier using calibrated threshold
        tau_decline = self.tier1.decision_threshold
        tau_stepup = self.tier1.stepup_threshold
        
        if fused_prob >= tau_decline:
            decision = "DECLINE_FRAUD"
            risk_tier = "CRITICAL" if fused_prob > min(0.98, tau_decline + 0.10) else "HIGH"
        elif fused_prob >= tau_stepup:
            decision = "CHALLENGE_STEPUP"
            risk_tier = "MEDIUM"
        else:
            decision = "ALLOW"
            risk_tier = "LOW"
            
        # Determine Flagged Attack Vector & ISO Reason Code
        flagged_vector, iso_code, playbook = self._determine_iso_classification(
            tx, fused_prob, p_tier1, p_tier2, p_tier3, meta_t2, meta_t3
        )
        
        # Explainability (Feature Attribution relative to baseline) computed when requested
        shap_feats = []
        if compute_explainability and decision != "ALLOW":
            shap_feats = self.tier1.explain_prediction(f_vec, top_k=4)
            
        total_lat_ms = (time.perf_counter() - start_time) * 1000.0
        sla_breached = total_lat_ms > system_cfg.TOTAL_P99_SLA_MS

        return DefenseVerdict(
            tx_id=tx.tx_id,
            decision=decision,
            fraud_probability=round(fused_prob, 4),
            risk_tier=risk_tier,
            flagged_attack_vector=flagged_vector,
            iso_rejection_code=iso_code if decision == "DECLINE_FRAUD" else None,
            shap_top_features=shap_feats,
            mitigation_playbook=playbook,
            tier1_latency_ms=round(lat_t1, 3),
            tier2_latency_ms=round(lat_t2, 3),
            tier3_latency_ms=round(lat_t3, 3),
            total_latency_ms=round(total_lat_ms, 3),
            sla_breached=sla_breached
        )

    def _determine_iso_classification(
        self,
        tx: PaymentTransaction,
        fused_prob: float,
        p1: float,
        p2: float,
        p3: float,
        m2: Dict[str, Any],
        m3: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str], str]:
        """Maps multi-tier signals to authentic ISO 20022 and Mastercard Extension Codes"""
        if fused_prob < 0.28:
            return None, None, "Transaction approved. Settle via standard ISO 20022 clearing."
            
        # 1. Agentic / Prompt Injection Flag
        if m3.get("agentic_risk", 0) > 0.60 or "PROMPT" in m3.get("agentic_reason", "") or "DRIFT" in m3.get("agentic_reason", ""):
            return (
                "ADV_01_AGENTIC_HIJACK",
                "X-MC-AGNT",
                "Trigger ISO 20022 pacs.002 RJCT (X-MC-AGNT). Revoke agent API session token. Require human cardholder re-auth."
            )
            
        # 2. Deepfake / Biometric Spoofing
        if tx.biometrics and (tx.biometrics.deepfake_visual_artifact_score > 0.40 or tx.biometrics.voice_spectral_anomaly_score > 0.40):
            return (
                "ADV_12_DEEPFAKE_STEPUP",
                "X-MC-BIOM",
                "Trigger ISO 20022 pacs.002 RJCT (X-MC-BIOM). Escalate out-of-band hardware token verification. Lock compromised biometric template."
            )
            
        # 3. Dynamic QR Homoglyph
        if m3.get("vpa_homoglyph_detected", False):
            return (
                "ADV_21_DYNAMIC_QR_CAMOUFLAGE",
                "X-MC-QRSP",
                "Decline real-time payment clearance (X-MC-QRSP). Flag fraudulent VPA in central settlement registry."
            )
            
        # 4. Mule Swarm / Topological Cycle
        if p2 > 0.70 or "MULE" in m2.get("flagged_pattern", "") or "CYCLE" in m2.get("flagged_pattern", ""):
            return (
                "ADV_26_AUTONOMOUS_MULE_SWARM",
                "X-MC-MULE",
                "Trigger ISO 20022 camt.056 FI-to-FI recall alert (X-MC-MULE). Freeze downstream pass-through settlement node."
            )
            
        # 5. Micro-Structuring Velocity Surge
        if tx.amount < 30.0 and tx.sender_past_tx_count_24h >= 4:
            return (
                "ADV_16_ROUTER_EVAPORATION",
                "AM23",
                "Decline micro-transaction velocity surge (ISO 20022 AM23). Rate-limit cardholder token across acquiring channels."
            )
            
        # 6. High-Value Account Takeover / APP Scam
        if tx.amount > 3000.0 and tx.sender_past_volume_24h < 200.0:
            return (
                "ADV_22_APP_SCAM_GROOMING",
                "FRAD",
                "Decline via ISO 20022 pacs.002 RJCT (Reason: FRAD). Out-of-band step-up challenge required for abnormal volume."
            )
            
        # Default Fraud
        return (
            "GENERIC_ADV_FRAUD",
            "FRAD",
            "Decline via ISO 20022 pacs.002 RJCT (Reason: FRAD). Add PAN/Account to high-risk surveillance watchlist."
        )


defense_engine = MasterShieldUnifiedDefenseEngine()
