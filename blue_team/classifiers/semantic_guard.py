"""
MasterShield AI - Tier 3 Multimodal & Agentic Semantic Guard
Mastercard Innovation Challenge @ GFF 2026

Specialized semantic guard detecting prompt injections, dispute manipulation,
agentic commerce goal drift, and homoglyphic VPA camouflage (<2.0ms P99).
"""

import time
import re
from typing import Dict, List, Any, Tuple, Optional
from core.models import PaymentTransaction, AgenticContext


class Tier3SemanticGuard:
    """Tier 3 Semantic & Prompt Injection Guard for Agentic and ISO 20022 Streams"""

    def __init__(self):
        # Generalized semantic intent tokens for prompt injections & jailbreaks
        self.injection_keywords = [
            ["system", "override"],
            ["ignore", "instruction"],
            ["ignore", "budget"],
            ["disregard", "policy"],
            ["prompt", "inject"],
            ["directive", "transfer"],
            ["directive", "re-allocate"],
            ["auto-approve", "chargeback"],
            ["immediate", "provisional"],
            ["non_rebuttable", "fraud"],
            ["emergency", "protocol"],
            ["bypass", "authorization"]
        ]
        
        # Financial brand watchlist for homoglyph / brand confusion analysis
        self.target_brands = ["mastercard", "visa", "apple", "amazon", "fednow", "paypal", "tatacliq", "flipkart", "paytm", "icici", "hdfc"]
        self.suspicious_modifiers = ["refund", "auth", "support", "billing", "settle", "care", "claim", "kyc", "desk"]

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Computes Levenshtein edit distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
            
        prev_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row
        return prev_row[-1]

    def scan_text(self, text: Optional[str]) -> Tuple[float, List[str]]:
        """Scans unstructured text for adversarial intent and instruction hijacking"""
        if not text or len(text.strip()) == 0:
            return 0.0, []
            
        text_lower = text.lower()
        matched_pairs = []
        
        for pair in self.injection_keywords:
            if all(k in text_lower for k in pair):
                matched_pairs.append(" + ".join(pair))
                
        if matched_pairs:
            confidence = min(0.96, 0.72 + 0.08 * len(matched_pairs))
            return confidence, matched_pairs
            
        return 0.02, []

    def inspect_agentic_context(self, agentic: Optional[AgenticContext]) -> Tuple[float, str]:
        """Evaluates autonomous AI agent context for goal drift and authorization breach"""
        if not agentic:
            return 0.0, "NO_AGENTIC_CONTEXT"
            
        risk = 0.05
        reason = "AGENTIC_NORMAL"
        
        # 1. Check prompt text for semantic injections
        inj_score, patterns = self.scan_text(agentic.prompt_text)
        if inj_score > 0.60:
            risk = max(risk, inj_score)
            reason = f"PROMPT_INJECTION_DETECTED: {len(patterns)} token pairs"
            
        # 2. Continuous semantic goal drift
        if agentic.semantic_deviation_score > 0.60:
            drift_risk = min(0.95, 0.60 + 0.50 * (agentic.semantic_deviation_score - 0.60))
            risk = max(risk, drift_risk)
            reason = f"AGENT_GOAL_DRIFT (Score: {agentic.semantic_deviation_score:.2f})"
            
        # 3. Untrusted domain redirect
        if agentic.untrusted_domain_redirect:
            risk = max(risk, 0.85)
            reason = "UNTRUSTED_DOMAIN_REDIRECT"

        return float(risk), reason

    def inspect_vpa_homoglyphs(self, vpa_or_account: str) -> Tuple[float, bool]:
        """Detects homoglyphs, visual edit distance spoofs, and brand keyword camouflage in VPAs"""
        vpa_lower = vpa_or_account.lower()
        if "@" not in vpa_lower:
            return 0.02, False
            
        handle_part = vpa_lower.split("@")[0]
        tokens = re.split(r"[._\-]", handle_part)
        
        # 1. Homoglyph normalization check
        normalized_token_str = handle_part.replace("1", "l").replace("0", "o").replace("3", "e").replace("@", "a")
        
        for brand in self.target_brands:
            # Check direct homoglyph replacement
            if brand in normalized_token_str and brand not in handle_part:
                return 0.92, True
                
            # Check Levenshtein distance on individual tokens (only for length >= 6 and edit distance == 1)
            for token in tokens:
                if len(token) >= 6 and len(brand) >= 6:
                    dist = self._levenshtein_distance(token, brand)
                    if dist == 1 and len(token) == len(brand):
                        return 0.88, True
                        
            # Check high-value brand + suspicious consumer keyword combination (e.g. mastercard.refunds)
            if brand in ["mastercard", "apple", "amazon", "fednow", "tatacliq"] and brand in handle_part:
                for mod in ["refund", "auth", "billing", "settle", "claim", "kyc"]:
                    if mod in handle_part:
                        return 0.90, True
                        
        return 0.02, False

    def evaluate_transaction(self, tx: PaymentTransaction) -> Tuple[float, Dict[str, Any], float]:
        """
        Real-time semantic guard evaluation (<1.5ms).
        Returns: (semantic_risk_score, metadata, latency_ms)
        """
        t0 = time.perf_counter()
        
        # 1. Agentic Context Scan
        ag_risk, ag_reason = self.inspect_agentic_context(tx.agentic)
        
        # 2. ISO 20022 Remittance / Dispute text scan
        rmt_text = ""
        if tx.iso_raw_xml_or_json and "CdtTrfTxInf" in tx.iso_raw_xml_or_json:
            rmt_text = tx.iso_raw_xml_or_json["CdtTrfTxInf"].get("RmtInf", {}).get("Ustrd", "")
            
        rmt_risk, patterns = self.scan_text(rmt_text)
        
        # 3. VPA Homoglyph Scan for Real-Time Rails
        vpa_risk, has_homoglyph = self.inspect_vpa_homoglyphs(tx.receiver_pan_or_account)
        
        overall_risk = max(ag_risk, rmt_risk, vpa_risk)
        t_lat = (time.perf_counter() - t0) * 1000.0
        
        metadata = {
            "agentic_risk": round(ag_risk, 3),
            "agentic_reason": ag_reason,
            "remittance_injection_risk": round(rmt_risk, 3),
            "vpa_homoglyph_detected": has_homoglyph
        }
        return float(overall_risk), metadata, round(t_lat, 3)


tier3_semantic_guard = Tier3SemanticGuard()
