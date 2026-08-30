"""
MasterShield AI - Explainability & ISO 20022 Compliance Engine
Mastercard Innovation Challenge @ GFF 2026

Transforms complex ML feature attributions into human-readable compliance summaries
and generates compliant ISO 20022 pacs.002 / camt.056 audit artifacts.
"""

from typing import Dict, List, Any, Optional
from core.models import PaymentTransaction, DefenseVerdict
from core.iso20022 import iso_engine
from config.config import rails_cfg


class ExplainabilityEngine:
    """Generates regulatory explainability reports and ISO 20022 rejection messages"""

    @staticmethod
    def generate_audit_trail(tx: PaymentTransaction, verdict: DefenseVerdict) -> Dict[str, Any]:
        """Generates comprehensive regulatory audit report for the payment authorization"""
        iso_status = "ACCP" if verdict.decision == "ALLOW" else "RJCT"
        reason_desc = rails_cfg.ISO_REJECTION_CODES.get(
            verdict.iso_rejection_code or "FRAD",
            "High Probability Anomaly Detected"
        )
        
        # Build ISO 20022 pacs.002 message
        pacs002 = iso_engine.generate_pacs_002(
            original_tx_id=tx.tx_id,
            status=iso_status,
            reason_code=verdict.iso_rejection_code,
            narrative=f"MasterShield AI: {verdict.mitigation_playbook}"
        )
        
        # Build ISO 20022 camt.056 recall if high severity mule/prompt attack
        camt056 = None
        if verdict.risk_tier == "CRITICAL" and verdict.iso_rejection_code in ["MULE", "AGNT"]:
            camt056 = iso_engine.generate_camt_056(
                original_tx_id=tx.tx_id,
                reason_code=verdict.iso_rejection_code,
                narrative="Immediate Automated Recall: High Severity GenAI Adversarial Infection"
            )

        return {
            "tx_id": tx.tx_id,
            "timestamp": tx.timestamp.isoformat() if hasattr(tx.timestamp, "isoformat") else str(tx.timestamp),
            "amount": tx.amount,
            "currency": tx.currency,
            "payment_rail": tx.payment_rail,
            "decision": verdict.decision,
            "risk_score": verdict.fraud_probability,
            "risk_tier": verdict.risk_tier,
            "flagged_vector": verdict.flagged_attack_vector or "NONE",
            "iso_rejection_code": verdict.iso_rejection_code or "NONE",
            "iso_rejection_description": reason_desc,
            "top_contributing_features": verdict.shap_top_features,
            "mitigation_playbook": verdict.mitigation_playbook,
            "latency_breakdown_ms": {
                "tier1_ensemble": verdict.tier1_latency_ms,
                "tier2_graph": verdict.tier2_latency_ms,
                "tier3_semantic": verdict.tier3_latency_ms,
                "total": verdict.total_latency_ms
            },
            "iso_pacs002_payload": pacs002,
            "iso_camt056_payload": camt056
        }


explainability_engine = ExplainabilityEngine()
