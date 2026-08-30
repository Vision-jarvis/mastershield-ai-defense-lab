"""
MasterShield AI - Red Team Synthetic Generation Pipeline (MPAM v2.0)
Mastercard Innovation Challenge @ GFF 2026

Generates realistic mixed streams of organic legitimate payment traffic
and adversarial GenAI attack campaigns with stateful entity tracking.
"""

import uuid
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from core.models import PaymentTransaction
from core.telemetry import telemetry_gen
from core.iso20022 import iso_engine
from red_team.attack_catalog import (
    AgenticCommerceHijacker,
    DisputeHallucinationInjector,
    SyntheticIdentityClustering,
    BiometricEvasionGenerator,
    DeepfakeStepUpBypass,
    PaymentRouterEvaporator,
    DynamicQRCamouflage,
    AutonomousMuleSwarm,
    CyclicTransitWashGenerator,
    APPScamGroomingGenerator,
    ActiveLearningPoisoningAttack
)
from config.config import rails_cfg, system_cfg


class RedTeamSimulationPipeline:
    """Orchestrates high-fidelity synthetic transaction generation across all rails"""

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        random.seed(seed)
        
        # Instantiate Active Simulated MPAM v2.0 Generators (covering all 6 attack families)
        self.attack_generators = {
            "ADV_01_AGENTIC_HIJACK": AgenticCommerceHijacker(seed=seed + 1),
            "ADV_02_DISPUTE_HALLUCINATION": DisputeHallucinationInjector(seed=seed + 2),
            "ADV_06_SYNTHETIC_IDENTITY": SyntheticIdentityClustering(seed=seed + 3),
            "ADV_11_BIOMETRIC_EVASION": BiometricEvasionGenerator(seed=seed + 4),
            "ADV_12_DEEPFAKE_STEPUP": DeepfakeStepUpBypass(seed=seed + 5),
            "ADV_16_ROUTER_EVAPORATION": PaymentRouterEvaporator(seed=seed + 6),
            "ADV_21_DYNAMIC_QR_CAMOUFLAGE": DynamicQRCamouflage(seed=seed + 7),
            "ADV_26_AUTONOMOUS_MULE_SWARM": AutonomousMuleSwarm(seed=seed + 8),
            "ADV_28_CYCLIC_TRANSIT_WASH": CyclicTransitWashGenerator(seed=seed + 9),
            "ADV_22_APP_SCAM_GROOMING": APPScamGroomingGenerator(seed=seed + 10),
            "ADV_30_DEFENSE_POISONING_ATTACK": ActiveLearningPoisoningAttack(seed=seed + 11)
        }

    def generate_benign_transaction(
        self,
        timestamp: Optional[datetime] = None,
        round_idx: int = 0
    ) -> PaymentTransaction:
        """Generates an authentic legitimate payment transaction with heavy-tailed spend and community structure"""
        sender = random.choice(telemetry_gen.cardholders)
        mcht = random.choice(telemetry_gen.merchants)
        mcc = mcht["mcc"]
        merchant_name = mcht["merchant_name"]
        receiver = mcht["account"]
        
        amount = telemetry_gen.sample_transaction_amount(mcc)
        
        if "@" in receiver:
            rail = "UPI_REALTIME_INSTANT"
            currency = "INR"
        elif "BANK" in receiver:
            rail = "FEDNOW_ISO20022"
            currency = "USD"
        else:
            rail = random.choice(["CARD_NOT_PRESENT_ECOM", "CARD_PRESENT_EMV", "AGENTIC_COMMERCE_AP2P"])
            currency = "USD"
            
        is_vpn = bool(self.rng.rand() < 0.055)
        ip, country, city = telemetry_gen.sample_ip_and_geo(is_vpn=is_vpn)
        
        tx_time = timestamp or telemetry_gen.sample_diurnal_timestamp(datetime.utcnow())
        
        is_power_user = bool(self.rng.rand() < 0.15)
        biometrics = telemetry_gen.generate_benign_biometrics(is_power_user=is_power_user)
        
        agentic_ctx = None
        if rail == "AGENTIC_COMMERCE_AP2P":
            agentic_ctx = telemetry_gen.generate_benign_agentic_context(merchant_name, amount)
            
        # Velocity metadata accumulated strictly from entity state
        past_tx_count, past_vol = telemetry_gen.get_and_update_sender_velocity(sender, tx_time, amount)
        inflow_count = telemetry_gen.get_and_update_receiver_inflow(receiver)

        return PaymentTransaction(
            tx_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            timestamp=tx_time,
            sender_pan_or_account=sender,
            receiver_pan_or_account=receiver,
            amount=amount,
            currency=currency,
            payment_rail=rail,
            mcc=mcc,
            merchant_name=merchant_name,
            merchant_id=mcht["merchant_id"],
            ip_address=ip,
            geo_country=country,
            geo_city=city,
            device_fingerprint=f"fp_{uuid.uuid4().hex[:8]}",
            is_vpn_or_tor=is_vpn,
            biometrics=biometrics,
            agentic=agentic_ctx,
            is_fraud=0,
            attack_vector="BENIGN_ORGANIC",
            simulation_round=round_idx,
            sender_past_tx_count_24h=past_tx_count,
            sender_past_volume_24h=past_vol,
            receiver_inflow_count_24h=inflow_count,
            iso_message_type="pacs.008.001.10"
        )

    def generate_synthetic_dataset(
        self,
        total_samples: int = 10000,
        fraud_ratio: float = 0.005,
        round_idx: int = 0,
        adversarial_strength: float = 1.0,
        seed: Optional[int] = None
    ) -> List[PaymentTransaction]:
        """Generates a complete mixed dataset of legitimate and novel GenAI attacks with seed isolation"""
        if seed is not None:
            local_rng = np.random.RandomState(seed)
        else:
            local_rng = self.rng
            
        num_fraud = max(1, int(total_samples * fraud_ratio))
        num_benign = total_samples - num_fraud
        
        dataset: List[PaymentTransaction] = []
        
        for i in range(num_benign):
            sample_time = telemetry_gen.sample_diurnal_timestamp(datetime.utcnow())
            tx = self.generate_benign_transaction(timestamp=sample_time, round_idx=round_idx)
            dataset.append(tx)

        vector_keys = list(self.attack_generators.keys())
        fraud_per_vector = max(1, num_fraud // len(vector_keys))
        
        for vec_key in vector_keys:
            gen = self.attack_generators[vec_key]
            generated_for_vec = 0
            while generated_for_vec < fraud_per_vector:
                attack_txs = gen.generate_attack(
                    round_idx=round_idx,
                    adversarial_strength=adversarial_strength
                )
                for atx in attack_txs:
                    dataset.append(atx)
                    generated_for_vec += 1
                    if generated_for_vec >= fraud_per_vector:
                        break

        local_rng.shuffle(dataset)
        return dataset

    def export_to_dataframe(self, transactions: List[PaymentTransaction]) -> pd.DataFrame:
        """Flattens transaction objects into a clean tabular DataFrame for modeling without leaks"""
        records = []
        for tx in transactions:
            rec = {
                "tx_id": tx.tx_id,
                "timestamp": tx.timestamp,
                "sender_account": tx.sender_pan_or_account,
                "receiver_account": tx.receiver_pan_or_account,
                "amount": tx.amount,
                "currency": tx.currency,
                "payment_rail": tx.payment_rail,
                "mcc": tx.mcc,
                "merchant_name": tx.merchant_name,
                "ip_address": tx.ip_address,
                "geo_country": tx.geo_country,
                "device_fingerprint": tx.device_fingerprint,
                "is_vpn_or_tor": int(tx.is_vpn_or_tor),
                "is_fraud": tx.is_fraud,
                "attack_vector": tx.attack_vector,
                "simulation_round": tx.simulation_round,
                "sender_past_tx_count_24h": tx.sender_past_tx_count_24h,
                "sender_past_volume_24h": tx.sender_past_volume_24h,
                "receiver_inflow_count_24h": tx.receiver_inflow_count_24h
            }
            
            if tx.biometrics:
                rec["bio_mouse_speed_mean"] = tx.biometrics.mouse_speed_mean
                rec["bio_mouse_speed_std"] = tx.biometrics.mouse_speed_std
                rec["bio_mouse_accel_jitter"] = tx.biometrics.mouse_acceleration_jitter
                rec["bio_keystroke_dwell"] = tx.biometrics.keystroke_dwell_mean
                rec["bio_keystroke_flight"] = tx.biometrics.keystroke_flight_time
                rec["bio_touch_entropy"] = tx.biometrics.touch_pressure_entropy
                rec["bio_deepfake_score"] = tx.biometrics.deepfake_visual_artifact_score
                rec["bio_voice_anomaly"] = tx.biometrics.voice_spectral_anomaly_score
            else:
                rec["bio_mouse_speed_mean"] = 240.0
                rec["bio_mouse_speed_std"] = 45.0
                rec["bio_mouse_accel_jitter"] = 12.0
                rec["bio_keystroke_dwell"] = 110.0
                rec["bio_keystroke_flight"] = 85.0
                rec["bio_touch_entropy"] = 0.85
                rec["bio_deepfake_score"] = 0.02
                rec["bio_voice_anomaly"] = 0.02

            if tx.agentic:
                rec["agent_semantic_deviation"] = tx.agentic.semantic_deviation_score
                rec["agent_budget_overrun_ratio"] = tx.amount / max(1.0, tx.agentic.authorized_budget)
                rec["agent_tool_call_depth"] = tx.agentic.tool_call_depth
                rec["agent_untrusted_redirect"] = int(tx.agentic.untrusted_domain_redirect)
            else:
                rec["agent_semantic_deviation"] = 0.0
                rec["agent_budget_overrun_ratio"] = 0.5
                rec["agent_tool_call_depth"] = 0
                rec["agent_untrusted_redirect"] = 0

            records.append(rec)
            
        return pd.DataFrame(records)


red_team_sim = RedTeamSimulationPipeline()
