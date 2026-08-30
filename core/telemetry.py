"""
MasterShield AI - Authentic Telemetry & Synthetic Biometrics Generator
Mastercard Innovation Challenge @ GFF 2026

Generates realistic human user behavioral biometrics, device fingerprints,
IP geolocation telemetry, and agentic commerce session traces.
"""

import numpy as np
import random
import uuid
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime, timedelta
from core.models import BiometricTelemetry, AgenticContext, PaymentTransaction
from config.config import rails_cfg


class TelemetryGenerator:
    """Generates authentic human behavioral distributions, community entities, and baseline agentic context"""

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        random.seed(seed)
        
        # Real-world public IP prefixes (Residential ISPs & Mobile Carriers)
        self.residential_subnets = [
            "73.162", "108.48", "98.245", "67.180",  # US Comcast / Verizon / AT&T
            "49.36", "122.161", "103.211", "27.59",   # India Jio / Airtel / Vodafone
            "82.165", "217.138", "86.128", "92.40",   # UK / EU BT / Vodafone / Orange
            "203.116", "118.200", "58.182"            # Singapore Singtel / StarHub
        ]
        self.datacenter_subnets = [
            "54.210", "34.90", "13.107", "185.220", "194.26" # Cloud / VPN / Tor exit nodes
        ]
        
        # Major Global Cities
        self.cities = [
            ("US", "New York"), ("US", "Chicago"), ("US", "San Francisco"), ("US", "Miami"),
            ("IN", "Mumbai"), ("IN", "Bengaluru"), ("IN", "Delhi"), ("IN", "Hyderabad"),
            ("GB", "London"), ("GB", "Manchester"),
            ("SG", "Singapore"),
            ("AE", "Dubai")
        ]
        
        # Build persistent Cardholder & Merchant Pools for realistic community structure
        self.cardholders = [self._generate_account_identifier(f"user_{i}") for i in range(2500)]
        self.merchants = self._initialize_merchants()
        
        # Stateful Entity Rolling 24h Transaction History Tracker
        self.cardholder_history: Dict[str, List[Tuple[datetime, float]]] = {
            acc: [] for acc in self.cardholders
        }
        self.merchant_inflows: Dict[str, int] = {
            m["account"]: random.randint(25, 250) for m in self.merchants
        }

    def _initialize_merchants(self) -> List[Dict[str, Any]]:
        """Initializes a realistic pool of 200 merchants with Zipfian popularity distribution"""
        merchants = []
        mcc_keys = list(rails_cfg.MCC_CATEGORIES.keys())
        merchant_names_by_mcc = {
            "5411": ["Whole Foods Market", "Kroger Supermarket", "Trader Joe's", "Reliance Fresh", "Tesco Express", "Carrefour Market"],
            "5732": ["Best Buy Electronics", "Apple Store Digital", "Newegg Hardware", "Croma Digital", "Micro Center"],
            "4829": ["Western Union Remittance", "MoneyGram International", "Wise Direct Transfer", "Remitly Global"],
            "7995": ["DraftKings Online", "BetMGM Sportsbook", "FanDuel Gaming", "Bet365 Digital"],
            "5944": ["Tiffany & Co.", "Cartier Fine Jewelry", "Kay Jewelers", "Tanishq Precious Metals", "Blue Nile"],
            "7372": ["Amazon Web Services", "Microsoft Azure Cloud", "OpenAI API Platform", "Google Cloud Compute", "GitHub Enterprise"],
            "4121": ["Uber Rideshare", "Lyft Mobility", "Ola Cabs", "Grab Transit"],
            "5812": ["Starbucks Coffee", "Chipotle Mexican Grill", "McDonald's Digital", "Sweetgreen", "Swiggy Delivery"],
            "6051": ["Coinbase Stored Value", "Binance Liquidity", "Kraken Digital Assets", "Bitstamp Exchange"],
            "5311": ["Target Superstore", "Nordstrom Luxury", "Macy's Department", "Zara Apparel", "Sephora Beauty"]
        }
        
        for i in range(200):
            mcc = random.choice(mcc_keys)
            names = merchant_names_by_mcc.get(mcc, ["Global Retail Direct"])
            name = random.choice(names) + f" #{random.randint(101, 999)}"
            mcht_acc = self._generate_account_identifier(f"mcht_{i}")
            merchants.append({
                "merchant_id": f"MID-{mcc}-{random.randint(100000, 999999)}",
                "merchant_name": name,
                "mcc": mcc,
                "account": mcht_acc
            })
        return merchants

    def _generate_account_identifier(self, entity_tag: str) -> str:
        """Generates realistic account identifiers (Masked PAN, IBAN, or UPI VPA)"""
        r_type = random.choice(["CARD", "IBAN", "UPI"])
        if r_type == "CARD":
            bin_prefix = random.choice(["541288", "510510", "411111", "401288", "378282"])
            last4 = f"{random.randint(1000, 9999)}"
            return f"{bin_prefix}******{last4}"
        elif r_type == "IBAN":
            country = random.choice(["US", "GB", "DE", "IN", "SG"])
            acc_num = f"{random.randint(1000000000, 9999999999)}"
            return f"{country}88BANK{acc_num}"
        else:
            handles = ["okhdfcbank", "okaxis", "icici", "paytm", "ybl", "sbi"]
            user_stem = random.choice(["rohit", "priya", "alex", "sarah", "chen", "david", "neha", "james", "mcht.pay"])
            return f"{user_stem}{random.randint(10, 999)}@{random.choice(handles)}"

    def get_and_update_sender_velocity(self, sender: str, tx_time: datetime, current_amount: float) -> Tuple[int, float]:
        """Calculates authentic 24h rolling velocity aggregates strictly from prior entity state"""
        hist = self.cardholder_history.get(sender, [])
        cutoff = tx_time - timedelta(hours=24)
        
        # Prune transactions older than 24h
        valid_hist = [item for item in hist if item[0] >= cutoff and item[0] < tx_time]
        self.cardholder_history[sender] = valid_hist + [(tx_time, current_amount)]
        
        past_count = len(valid_hist)
        past_vol = sum(item[1] for item in valid_hist)
        
        # If cardholder has no history in the local simulation slice yet, sample from realistic prior
        if past_count == 0:
            past_count = int(self.rng.choice([0, 1, 2, 3, 4, 5, 7, 9, 12], p=[0.20, 0.32, 0.20, 0.12, 0.07, 0.04, 0.02, 0.02, 0.01]))
            if past_count > 0:
                past_vol = round(float(self.rng.lognormal(mean=4.5, sigma=1.1)), 2)
            else:
                past_vol = 0.0
                
        return past_count, past_vol

    def get_and_update_receiver_inflow(self, receiver: str) -> int:
        """Retrieves and updates dynamic receiver inflow counts"""
        count = self.merchant_inflows.get(receiver, random.randint(20, 80))
        self.merchant_inflows[receiver] = count + 1
        return count

    def generate_benign_biometrics(self, is_power_user: bool = False) -> BiometricTelemetry:
        """
        Generates authentic human user behavioral biometrics with natural human variance.
        Includes overlapping tails with subtle anomaly regions (e.g. jittery mouse for gamers, slow dwell for seniors).
        """
        if is_power_user:
            mouse_speed_mean = float(self.rng.normal(320.0, 35.0))
            mouse_speed_std = float(self.rng.uniform(45.0, 90.0))
            mouse_accel_jitter = float(self.rng.uniform(14.0, 24.0)) # natural rapid movements
            keystroke_dwell = float(self.rng.normal(85.0, 12.0))
            keystroke_flight = float(self.rng.normal(65.0, 15.0))
            touch_entropy = float(self.rng.uniform(0.85, 0.98))
        else:
            mouse_speed_mean = float(self.rng.lognormal(mean=5.3, sigma=0.30)) # ~180-280 px/s
            mouse_speed_std = float(self.rng.uniform(25.0, 65.0))
            mouse_accel_jitter = float(self.rng.uniform(7.0, 18.0))
            keystroke_dwell = float(self.rng.normal(118.0, 18.0))
            keystroke_flight = float(self.rng.normal(92.0, 22.0))
            touch_entropy = float(self.rng.uniform(0.70, 0.94))
        
        # Subtle non-zero tail for compression artifacts / noise in authentic video/audio feeds
        deepfake_score = float(self.rng.exponential(scale=0.03))
        deepfake_score = min(0.35, max(0.001, deepfake_score))
        
        voice_anomaly = float(self.rng.exponential(scale=0.025))
        voice_anomaly = min(0.30, max(0.001, voice_anomaly))

        return BiometricTelemetry(
            mouse_speed_mean=round(mouse_speed_mean, 2),
            mouse_speed_std=round(mouse_speed_std, 2),
            mouse_acceleration_jitter=round(mouse_accel_jitter, 2),
            keystroke_dwell_mean=round(max(35.0, keystroke_dwell), 2),
            keystroke_flight_time=round(max(25.0, keystroke_flight), 2),
            touch_pressure_entropy=round(touch_entropy, 3),
            deepfake_visual_artifact_score=round(deepfake_score, 4),
            voice_spectral_anomaly_score=round(voice_anomaly, 4),
            is_spoofed=False
        )

    def generate_benign_agentic_context(self, merchant_name: str, amount: float) -> AgenticContext:
        """Generates normal autonomous shopping agent execution context with diverse prompt templates"""
        normal_prompts = [
            f"Please execute scheduled recurring purchase of enterprise office supplies from approved merchant {merchant_name}.",
            f"Auto-renew cloud compute subscription with {merchant_name} within quarterly IT budget.",
            f"Replenish inventory stock for SKU-4920 from authorized vendor {merchant_name}.",
            f"Book standard corporate business travel and accommodation with partner {merchant_name}.",
            f"Authorize monthly SaaS developer seat licenses for engineering department at {merchant_name}."
        ]
        prompt = random.choice(normal_prompts)
        
        # Budget factor allows natural variance: cart checkout can occasionally exceed initial estimate (tax/shipping/tip)
        budget_factor = float(self.rng.uniform(0.75, 2.5))
        budget = round(amount * budget_factor, 2)
        
        # Authentic agents have natural semantic task variation (~0.05 to 0.42)
        sem_dev = float(self.rng.beta(2.0, 12.0))
        
        # ~2.5% of legitimate checkouts encounter 3DS or gateway redirect hops
        has_redirect = bool(self.rng.rand() < 0.025)
        
        return AgenticContext(
            agent_id=f"AGENT-{random.randint(10000, 99999)}",
            agent_framework=random.choice(["AutoGPT-Enterprise-v4", "CrewAI-Procure-v2", "LangChain-AgenticPay-v3"]),
            prompt_text=prompt,
            prompt_injection_detected=False,
            semantic_deviation_score=round(sem_dev, 4),
            authorized_budget=budget,
            tool_call_depth=int(self.rng.randint(1, 4)),
            untrusted_domain_redirect=has_redirect
        )

    def sample_ip_and_geo(self, is_vpn: bool = False) -> Tuple[str, str, str]:
        """Generates authentic IP address and matching geolocation"""
        country, city = random.choice(self.cities)
        if is_vpn:
            subnet = random.choice(self.datacenter_subnets)
        else:
            subnet = random.choice(self.residential_subnets)
        ip = f"{subnet}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        return ip, country, city

    def sample_transaction_amount(self, mcc: str) -> float:
        """Samples realistic heavy-tailed transaction amount conditional on MCC category"""
        mcc_info = rails_cfg.MCC_CATEGORIES.get(mcc, {"mu": 4.5, "sigma": 0.8, "median": 90.0})
        mu = mcc_info["mu"]
        sigma = mcc_info["sigma"]
        amt = float(self.rng.lognormal(mean=mu, sigma=sigma))
        return round(max(2.50, min(25000.0, amt)), 2)

    def sample_diurnal_timestamp(self, base_date: datetime) -> datetime:
        """Samples timestamp following realistic diurnal curve (peaking 10:00-21:00)"""
        hour_prob = np.array([
            0.01, 0.005, 0.005, 0.005, 0.01, 0.02, # 00:00 - 05:00
            0.03, 0.05, 0.07, 0.08, 0.09, 0.09,    # 06:00 - 11:00
            0.08, 0.07, 0.06, 0.06, 0.07, 0.08,    # 12:00 - 17:00
            0.07, 0.06, 0.04, 0.03, 0.02, 0.01     # 18:00 - 23:00
        ])
        hour_prob /= hour_prob.sum()
        chosen_hour = int(self.rng.choice(24, p=hour_prob))
        minute = int(self.rng.randint(0, 60))
        second = int(self.rng.randint(0, 60))
        
        day_offset = int(self.rng.randint(0, 7))
        return base_date - timedelta(days=day_offset, hours=(23 - chosen_hour), minutes=minute, seconds=second)


telemetry_gen = TelemetryGenerator()
