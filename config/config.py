"""
MasterShield AI - Autonomous Red/Blue Co-Evolution Defense Lab for Next-Gen Payment Security
Mastercard Innovation Challenge @ GFF 2026

Configuration Module: Global parameters, attack ontologies (MPAM v2.0), model hyperparameters, and SLAs.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODELS_DIR = BASE_DIR / "models_saved"
WEB_STATIC_DIR = BASE_DIR / "web_app" / "static"

for directory in [DATA_DIR, ARTIFACTS_DIR, MODELS_DIR, WEB_STATIC_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class SystemConfig:
    """Master System Configuration"""
    SYSTEM_NAME: str = "MasterShield AI (AegisPay Defense Lab)"
    VERSION: str = "2026.2-ENTERPRISE"
    RANDOM_SEED: int = 42
    DEBUG: bool = False
    
    # Latency SLA Targets (Milliseconds)
    TIER1_MAX_LATENCY_MS: float = 2.5    # Quantized GBDT Inference
    TIER2_MAX_LATENCY_MS: float = 3.5    # Streaming Graph Anomaly Network
    TIER3_MAX_LATENCY_MS: float = 3.8    # Multimodal Semantic & Homoglyph Guard
    TOTAL_P99_SLA_MS: float = 9.8        # End-to-end P99 budget for payment network authorization
    
    # Realistic Production Benchmark Parameters
    REALISTIC_FRAUD_PREVALENCE: float = 0.002 # 0.20% realistic live network fraud rate
    TARGET_FPR_MAX: float = 0.0005             # Max 0.05% False Positive Rate on legitimate volume
    TARGET_RECALL_MIN: float = 0.900           # Target >= 90% Recall at ultra-low FPR
    TARGET_ROC_AUC: float = 0.940              # Target ROC-AUC on non-leaky feature space
    TARGET_PR_AUC: float = 0.850               # Target PR-AUC at realistic prevalence


@dataclass
class PaymentRailsConfig:
    """Supported Payment Rails and Standards"""
    RAILS: List[str] = field(default_factory=lambda: [
        "CARD_PRESENT_EMV",
        "CARD_NOT_PRESENT_ECOM",
        "AGENTIC_COMMERCE_AP2P",
        "UPI_REALTIME_INSTANT",
        "FEDNOW_ISO20022",
        "CROSSBORDER_SWIFT_GO"
    ])
    
    CURRENCIES: List[str] = field(default_factory=lambda: ["USD", "EUR", "GBP", "INR", "SGD", "AED"])
    
    # Merchant Category Codes (MCC) with typical spend parameters
    MCC_CATEGORIES: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "5411": {"name": "Grocery Stores / Supermarkets", "mu": 3.8, "sigma": 0.5, "median": 45.0},
        "5732": {"name": "Electronic Sales & Hardware", "mu": 5.8, "sigma": 0.8, "median": 330.0},
        "4829": {"name": "Wire Transfer & Remittance", "mu": 6.8, "sigma": 1.1, "median": 890.0},
        "7995": {"name": "Gambling & Betting", "mu": 5.2, "sigma": 1.2, "median": 180.0},
        "5944": {"name": "Jewelry & Precious Metals", "mu": 7.2, "sigma": 1.0, "median": 1340.0},
        "7372": {"name": "Computer Software & AI API Cloud", "mu": 4.5, "sigma": 0.9, "median": 90.0},
        "4121": {"name": "Taxicabs & Rideshare", "mu": 3.2, "sigma": 0.4, "median": 24.0},
        "5812": {"name": "Restaurants & Dining", "mu": 4.1, "sigma": 0.6, "median": 60.0},
        "6051": {"name": "Quasi-Cash & Crypto Exchange", "mu": 7.0, "sigma": 1.1, "median": 1100.0},
        "5311": {"name": "Department Stores & Luxury", "mu": 5.5, "sigma": 0.9, "median": 245.0}
    })
    
    # Authentic ISO 20022 External Codes and Explicit Mastercard Proprietary Extensions (X-MC-*)
    ISO_REJECTION_CODES: Dict[str, str] = field(default_factory=lambda: {
        "FRAD": "Fraudulent Origin (ISO 20022 External Code)",
        "AC06": "Blocked Account Number (ISO 20022 External Code)",
        "AM05": "Duplication / Velocity Limit Exceeded (ISO 20022 External Code)",
        "RR04": "Regulatory / AML Compliance Violation (ISO 20022 External Code)",
        "ED05": "Settlement Failure (ISO 20022 External Code)",
        "X-MC-AGNT": "Agentic Commerce Goal Drift / Injection (Mastercard Extension)",
        "X-MC-SYNI": "Synthetic Identity Ring Flagged (Mastercard Extension)",
        "X-MC-BIOM": "Neuromuscular Biometric Spoof / Deepfake (Mastercard Extension)",
        "X-MC-MULE": "Autonomous Mule Swarm Topology (Mastercard Extension)",
        "X-MC-QRSP": "Real-Time Rail Semantic VPA Camouflage (Mastercard Extension)"
    })


@dataclass
class AttackOntologyConfig:
    """
    Mastercard Payment Adversarial Matrix (MPAM v2.0)
    Comprehensive 30-Vector Threat Taxonomy across 6 Strategic Attack Families.
    """
    ATTACK_VECTORS: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        # --- Family 1: Agentic Commerce & LLM Vulnerabilities ---
        "ADV_01_AGENTIC_HIJACK": {
            "family": "Agentic Commerce",
            "name": "Agentic Commerce Wallet Hijacking (ACWH)",
            "rail": "AGENTIC_COMMERCE_AP2P",
            "iso_msg": "pain.001 / agent.tx.v1",
            "rejection_code": "X-MC-AGNT",
            "genai_mechanism": "Indirect prompt injection embedded in product metadata overriding shopping agent budget limits and redirecting settlement.",
            "baseline_blindspot": "Traditional engines verify agent API keys but lack semantic payload intent inspection.",
            "is_simulated": True
        },
        "ADV_02_DISPUTE_HALLUCINATION": {
            "family": "Agentic Commerce",
            "name": "Prompt-Injected Dispute Hallucination (PIDH)",
            "rail": "CROSSBORDER_SWIFT_GO",
            "iso_msg": "camt.056.001.10",
            "rejection_code": "FRAD",
            "genai_mechanism": "Adversarial prompt injection embedded in chargeback memos manipulating issuing bank dispute LLMs into instant auto-refunds.",
            "baseline_blindspot": "Issuer chargeback resolution bots treat dispute transcript text as trustworthy input.",
            "is_simulated": True
        },
        "ADV_03_SUPPORT_LLM_ATO": {
            "family": "Agentic Commerce",
            "name": "Support Agent Social Engineering & Recovery ATO",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "pain.001.001.11",
            "rejection_code": "X-MC-AGNT",
            "genai_mechanism": "Multi-turn LLM social engineering targeting bank customer service agents to trigger unauthorized 2FA phone/email resets.",
            "baseline_blindspot": "Customer support transcripts are unmonitored by real-time auth scoring engines.",
            "is_simulated": False
        },
        "ADV_04_AUTONOMOUS_PROCUREMENT_DRAIN": {
            "family": "Agentic Commerce",
            "name": "Autonomous B2B ERP Procurement Agent Draining",
            "rail": "FEDNOW_ISO20022",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "X-MC-AGNT",
            "genai_mechanism": "Compromised automated invoice reader LLMs accepting hallucinated vendor accounts with matching po numbers.",
            "baseline_blindspot": "B2B batch payment rails assume internal ERP agent approvals are authenticated.",
            "is_simulated": False
        },
        "ADV_05_AGENT_POISONED_CONTRACT": {
            "family": "Agentic Commerce",
            "name": "Smart Contract / AP2P Dynamic Pricing Exploit",
            "rail": "AGENTIC_COMMERCE_AP2P",
            "iso_msg": "agent.tx.v1",
            "rejection_code": "X-MC-AGNT",
            "genai_mechanism": "Adversarial bidding bots feeding manipulated volatility feeds into autonomous settlement contracts.",
            "baseline_blindspot": "Decentralized AP2P payment contracts execute deterministic logic without semantic sanity guards.",
            "is_simulated": False
        },

        # --- Family 2: Synthetic Identity & KYC Diffusion Sleeper Rings ---
        "ADV_06_SYNTHETIC_IDENTITY": {
            "family": "Synthetic Identity",
            "name": "Polymorphic Synthetic Identity Clusters (PSIC)",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "X-MC-SYNI",
            "genai_mechanism": "Multimodal diffusion models generating synthetic identity documentation with 6-month dormant credit grooming.",
            "baseline_blindspot": "Credit bureau checks pass due to synthetic credit file aging; point-in-time scoring misses synchronized ring activations.",
            "is_simulated": True
        },
        "ADV_07_DEEPFAKE_KYC_LIVENESS": {
            "family": "Synthetic Identity",
            "name": "Deepfake Video KYC & Digital Liveness Injection",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "3DS_2.3_AuthRequest",
            "rejection_code": "X-MC-SYNI",
            "genai_mechanism": "Virtual camera drivers injecting generative 3D facial avatars passing passive and active liveness challenges.",
            "baseline_blindspot": "Standard liveness SDKs focus on blink/head-turn without detecting synthetic facial micro-texture anomalies.",
            "is_simulated": False
        },
        "ADV_08_FAKE_MERCHANT_KYB": {
            "family": "Synthetic Identity",
            "name": "GenAI Shell Merchant KYB Onboarding & Laundering",
            "rail": "CARD_PRESENT_EMV",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "RR04",
            "genai_mechanism": "Automated creation of fake storefronts, corporate filings, and transaction histories to onboard acquiring accounts.",
            "baseline_blindspot": "Acquiring risk reviews check static document consistency without temporal commerce graph analysis.",
            "is_simulated": False
        },
        "ADV_09_FIRST_PARTY_BUSTOUT_FARM": {
            "family": "Synthetic Identity",
            "name": "First-Party Synthetic Bust-Out Collusion",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "X-MC-SYNI",
            "genai_mechanism": "Sleeper networks building high transaction reputation before executing coordinated credit limit exhaustion.",
            "baseline_blindspot": "High historical payment scores mask coordinated sudden bust-out actions across disparate issuers.",
            "is_simulated": False
        },
        "ADV_10_SYNTHETIC_EMPLOYEE_PAYROLL": {
            "family": "Synthetic Identity",
            "name": "Ghost Payroll Synthetic Injection",
            "rail": "FEDNOW_ISO20022",
            "iso_msg": "pain.001.001.11",
            "rejection_code": "RR04",
            "genai_mechanism": "GenAI-generated employee credentials inserted into corporate payroll batches dispersing salary funds to mules.",
            "baseline_blindspot": "Direct deposit rails execute high-volume ACH/instant payouts with minimal receiver verification.",
            "is_simulated": False
        },

        # --- Family 3: Neuromuscular Biometrics & Deepfake Step-Up Bypass ---
        "ADV_11_BIOMETRIC_EVASION": {
            "family": "Biometric Evasion",
            "name": "Sub-Perceptual Behavioral Biometric Evasion (SP-BBS)",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "3DS_2.3_AuthRequest",
            "rejection_code": "X-MC-BIOM",
            "genai_mechanism": "Recurrent GANs synthesizing Bézier cursor trajectories and keystroke dwell dynamics matching legitimate distributions.",
            "baseline_blindspot": "Rule engines flag bot automation (straight lines) but miss adversarial models trained to mimic human tremor variance.",
            "is_simulated": True
        },
        "ADV_12_DEEPFAKE_STEPUP": {
            "family": "Biometric Evasion",
            "name": "Multimodal Deepfake 3DS 2.3 Step-Up Bypass (MDSB)",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "3DS_2.3_BiometricStepUp",
            "rejection_code": "X-MC-BIOM",
            "genai_mechanism": "Real-time zero-shot neural voice cloning combined with 3D NeRF facial reconstruction to defeat step-up video challenges.",
            "baseline_blindspot": "Biometric verifiers evaluate challenge completion without multi-spectral audio/video artifact analysis.",
            "is_simulated": True
        },
        "ADV_13_TOUCH_PRESSURE_INTERPOLATION": {
            "family": "Biometric Evasion",
            "name": "Mobile Touchscreen Pressure & Gyroscope Spoofing",
            "rail": "UPI_REALTIME_INSTANT",
            "iso_msg": "3DS_2.3_AuthRequest",
            "rejection_code": "X-MC-BIOM",
            "genai_mechanism": "Simulated device sensor telemetry (accelerometer, gyroscope, touch surface contact area) during headless payment authorization.",
            "baseline_blindspot": "Mobile SDKs verify presence of sensor streams but lack multi-axis correlation validation.",
            "is_simulated": False
        },
        "ADV_14_VOICE_VISHING_OTP_HARVEST": {
            "family": "Biometric Evasion",
            "name": "LLM Voice-Clone Vishing for Real-Time 3DS OTP",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "3DS_2.3_AuthRequest",
            "rejection_code": "FRAD",
            "genai_mechanism": "Autonomous conversational voice bots calling cardholders during auth to social engineer step-up OTPs in real-time.",
            "baseline_blindspot": "Auth engine observes valid OTP submission without detecting concurrent social engineering calls.",
            "is_simulated": False
        },
        "ADV_15_BEHAVIORAL_REPLAY_INJECTION": {
            "family": "Biometric Evasion",
            "name": "Adversarial Behavioral Replay & Session Hijack",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "3DS_2.3_AuthRequest",
            "rejection_code": "X-MC-BIOM",
            "genai_mechanism": "Injecting previously captured legitimate behavioral telemetry into fraudulent checkout payloads.",
            "baseline_blindspot": "Point scoring validates biometric shape without cryptographic session-nonce binding.",
            "is_simulated": False
        },

        # --- Family 4: Adversarial Payment Routing & Structuring ---
        "ADV_16_ROUTER_EVAPORATION": {
            "family": "Payment Routing",
            "name": "Adversarial Payment Router Evaporation (APRE)",
            "rail": "CARD_PRESENT_EMV",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "AM23",
            "genai_mechanism": "Reinforcement learning policy splitting large balances into micro-chunks below static rules across dynamic MCC categories.",
            "baseline_blindspot": "Single-transaction velocity rules miss distributed low-value transactions spread across distinct acquiring channels.",
            "is_simulated": True
        },
        "ADV_17_BIN_ATTACK_ENUMERATION": {
            "family": "Payment Routing",
            "name": "GenAI-Assisted Smart BIN Enumeration & Card Testing",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "AM23",
            "genai_mechanism": "Predictive models optimizing Luhn check generation and merchant selection to minimize issuer testing alert triggers.",
            "baseline_blindspot": "Card testing engines monitor single-merchant surges while attackers distribute across 500+ small merchant gateways.",
            "is_simulated": False
        },
        "ADV_18_TRANSACTION_LAUNDERING_MCC": {
            "family": "Payment Routing",
            "name": "Transaction Laundering & Adversarial MCC Miscoding",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "RR04",
            "genai_mechanism": "Routing high-risk/illicit transactions through benign low-risk merchant IDs (e.g. digital books) using AI shell sites.",
            "baseline_blindspot": "Payment gateways inspect reported MCC without analyzing underlying transaction text and fulfillment graph.",
            "is_simulated": False
        },
        "ADV_19_MULTI_CURRENCY_ROUNDTRIP": {
            "family": "Payment Routing",
            "name": "Multi-Currency Arbitrage & FX Velocity Exploitation",
            "rail": "CROSSBORDER_SWIFT_GO",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "AM02",
            "genai_mechanism": "Exploiting latency windows in cross-border multi-currency settlement rates through micro-arbitrage swarms.",
            "baseline_blindspot": "Issuer authorization checks domestic limits but misses correlated cross-currency settlement latency exposure.",
            "is_simulated": False
        },
        "ADV_20_REFUND_ARBITRAGE_RING": {
            "family": "Payment Routing",
            "name": "Automated Refund & Merchandise Return Arbitrage",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "FRAD",
            "genai_mechanism": "Generating fake return receipts and tracking numbers to claim automated e-commerce refunds prior to physical audit.",
            "baseline_blindspot": "Refund clearing streams are processed asynchronously with lower fraud scoring scrutiny.",
            "is_simulated": False
        },

        # --- Family 5: Real-Time Rails (UPI / FedNow) & Dynamic QR Exploits ---
        "ADV_21_DYNAMIC_QR_CAMOUFLAGE": {
            "family": "Real-Time Rails",
            "name": "Real-Time Rail Dynamic QR & VPA Semantic Camouflage",
            "rail": "UPI_REALTIME_INSTANT",
            "iso_msg": "pacs.008_UPI_VPA",
            "rejection_code": "X-MC-QRSP",
            "genai_mechanism": "Unicode homoglyphs and generative context masking in payment requests spoofing trusted corporate VPAs.",
            "baseline_blindspot": "String equality checks miss visual homoglyphs and brand context misdirection in real-time settlement rails.",
            "is_simulated": True
        },
        "ADV_22_APP_SCAM_GROOMING": {
            "family": "Real-Time Rails",
            "name": "Authorized Push Payment (APP) LLM Grooming Scam",
            "rail": "FEDNOW_ISO20022",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "FRAD",
            "genai_mechanism": "Automated conversational agents conducting multi-week romance/investment grooming convincing victims to authorize instant transfers.",
            "baseline_blindspot": "Cardholder genuinely authorizes payment from legitimate device with correct 2FA; behavioral auth passes.",
            "is_simulated": True
        },
        "ADV_23_UPI_MANDATE_TRAP": {
            "family": "Real-Time Rails",
            "name": "UPI Auto-Debit Mandate & Collect Request Abuse",
            "rail": "UPI_REALTIME_INSTANT",
            "iso_msg": "pacs.008_UPI_VPA",
            "rejection_code": "X-MC-QRSP",
            "genai_mechanism": "Generative camouflage disguising recurring debit mandates as one-time promotional cashbacks in consumer UPI apps.",
            "baseline_blindspot": "Mandate approvals rely on consumer UI confirmation without centralized intent validation.",
            "is_simulated": False
        },
        "ADV_24_DYNAMIC_QR_STICKER_SWAP": {
            "family": "Real-Time Rails",
            "name": "Physical-Digital Merchant Dynamic QR Hijack",
            "rail": "UPI_REALTIME_INSTANT",
            "iso_msg": "pacs.008_UPI_VPA",
            "rejection_code": "X-MC-QRSP",
            "genai_mechanism": "Dynamic generation of localized merchant QR codes intercepting point-of-sale customer flows.",
            "baseline_blindspot": "Static QR validation misses mismatch between physical geo-location and beneficiary acquiring account.",
            "is_simulated": False
        },
        "ADV_25_INSTANT_RECALL_EVASION": {
            "family": "Real-Time Rails",
            "name": "FedNow / SEPA Instant Fast-Exit Wash",
            "rail": "FEDNOW_ISO20022",
            "iso_msg": "camt.056.001.10",
            "rejection_code": "RR04",
            "genai_mechanism": "Instant automated routing of stolen funds into crypto on-ramps within 3 seconds of real-time rail credit.",
            "baseline_blindspot": "ISO 20022 camt.056 recall requests take minutes/hours, arriving after funds have exited the banking perimeter.",
            "is_simulated": False
        },

        # --- Family 6: Multi-Hop Swarms & Graph Laundering ---
        "ADV_26_AUTONOMOUS_MULE_SWARM": {
            "family": "Graph Laundering",
            "name": "Low-Centrality Autonomous Mule Swarm Orchestration (AMSO)",
            "rail": "FEDNOW_ISO20022",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "X-MC-MULE",
            "genai_mechanism": "Multi-agent autonomous swarms executing low-centrality, multi-hop acyclic money laundering to avoid graph centrality triggers.",
            "baseline_blindspot": "Traditional graph engines monitor high-degree hub nodes; decentralized mesh topologies evade threshold alerts.",
            "is_simulated": True
        },
        "ADV_27_SMURFING_AGGREGATION_RING": {
            "family": "Graph Laundering",
            "name": "High-Frequency Micro-Smurfing & Layering Mesh",
            "rail": "FEDNOW_ISO20022",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "X-MC-MULE",
            "genai_mechanism": "Coordinated micro-deposits from 200+ mules aggregating into intermediate offshore accounts.",
            "baseline_blindspot": "Transaction monitoring rules evaluate accounts in isolation rather than analyzing collective temporal flow balance.",
            "is_simulated": False
        },
        "ADV_28_CYCLIC_TRANSIT_WASH": {
            "family": "Graph Laundering",
            "name": "Cyclic Multi-Hop Round-Trip Laundering Ring",
            "rail": "FEDNOW_ISO20022",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "X-MC-MULE",
            "genai_mechanism": "Algorithmic cyclic flows designed to artificially inflate legitimate account volume before extracting capital.",
            "baseline_blindspot": "Standard relational databases cannot perform real-time cycle detection within 10ms auth budget.",
            "is_simulated": True
        },
        "ADV_29_BNPL_STACKING_COLLUSION": {
            "family": "Graph Laundering",
            "name": "Autonomous BNPL Stacking & Cross-Provider Default",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "FRAD",
            "genai_mechanism": "Coordinated simultaneous BNPL loan originations across 10 fintechs before credit bureau reporting syncs.",
            "baseline_blindspot": "BNPL providers perform point-in-time checks without cross-provider real-time credit commitment sharing.",
            "is_simulated": False
        },
        "ADV_30_DEFENSE_POISONING_ATTACK": {
            "family": "Graph Laundering",
            "name": "Adversarial Active Learning & Feedback Poisoning",
            "rail": "CARD_NOT_PRESENT_ECOM",
            "iso_msg": "pacs.008.001.10",
            "rejection_code": "FRAD",
            "genai_mechanism": "Injecting carefully crafted adversarial false positives/negatives into online retraining buffers to distort blue team decision boundaries.",
            "baseline_blindspot": "Automated online learning pipelines assume incoming analyst/chargeback labels are uncorrupted.",
            "is_simulated": True
        }
    })


@dataclass
class MLDefenseConfig:
    """Machine Learning & Defense Engine Hyperparameters"""
    # Tier 1: Quantized Gradient Boosting Detector
    GBDT_N_ESTIMATORS: int = 200
    GBDT_MAX_DEPTH: int = 6
    GBDT_LEARNING_RATE: float = 0.05
    GBDT_SUBSAMPLE: float = 0.85
    GBDT_COL_SAMPLE: float = 0.85
    
    # Tier 2: Streaming Graph Anomaly Detector
    GRAPH_TIME_WINDOW_HOURS: int = 72
    GRAPH_MIN_CYCLE_LEN: int = 2
    GRAPH_MAX_CYCLE_LEN: int = 4
    
    # Tier 3: Semantic & Homoglyph Guard
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.75
    HOMOGLYPH_EDIT_DISTANCE_MAX: int = 2
    
    # Co-Evolutionary Closed-Loop Settings
    COEVOLUTION_ROUNDS: int = 5
    MUTATION_RATE: float = 0.20
    ADVERSARIAL_POPULATION_SIZE: int = 500
    HARD_NEGATIVE_BUFFER_MAX: int = 2000
    RETRAIN_DELAY_DAYS: int = 30 # Simulated chargeback label maturity


system_cfg = SystemConfig()
rails_cfg = PaymentRailsConfig()
attacks_cfg = AttackOntologyConfig()
defense_cfg = MLDefenseConfig()
