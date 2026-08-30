"""
MasterShield AI - Core Data Models & Schema Definitions
Mastercard Innovation Challenge @ GFF 2026

Pydantic schemas for high-throughput payment transactions, ISO 20022 messages,
behavioral biometrics, agentic contexts, and defense verdicts.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class BiometricTelemetry(BaseModel):
    """Behavioral & Multimodal Biometrics Telemetry"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mouse_speed_mean: float = 240.5          # pixels/sec
    mouse_speed_std: float = 45.2
    mouse_acceleration_jitter: float = 12.8  # curvature / micro-tremor
    keystroke_dwell_mean: float = 112.0      # milliseconds
    keystroke_flight_time: float = 85.0      # milliseconds
    touch_pressure_entropy: float = 0.85     # touch screen entropy
    deepfake_visual_artifact_score: float = 0.02 # 0.0 = authentic, 1.0 = synthetic deepfake
    voice_spectral_anomaly_score: float = 0.01   # 0.0 = authentic, 1.0 = cloned voice
    is_spoofed: bool = False


class AgenticContext(BaseModel):
    """Agentic Commerce (Autonomous AI Shopping Agent) Telemetry"""
    agent_id: Optional[str] = None
    agent_framework: Optional[str] = "AutoGPT-Commerce-v4"
    prompt_text: Optional[str] = ""
    prompt_injection_detected: bool = False
    semantic_deviation_score: float = 0.0    # Deviation from user original shopping intent (0.0 to 1.0)
    authorized_budget: float = 500.0         # Maximum authorized threshold
    tool_call_depth: int = 1                 # Tool invocation nesting depth
    untrusted_domain_redirect: bool = False


class PaymentTransaction(BaseModel):
    """Unified Payment Transaction Schema across Card, RTP, ISO20022 & Agentic Rails"""
    tx_id: str = Field(default_factory=lambda: f"TXN-{uuid.uuid4().hex[:12].upper()}")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender_pan_or_account: str
    receiver_pan_or_account: str
    amount: float
    currency: str = "USD"
    payment_rail: str = "CARD_NOT_PRESENT_ECOM"
    mcc: str = "5411"
    merchant_name: str = "Global Merchant Services"
    merchant_id: str = "MID-883920"
    
    # Network & Device Telemetry
    ip_address: str = "192.168.1.1"
    geo_country: str = "US"
    geo_city: str = "New York"
    device_fingerprint: str = "fp_99a810b4"
    is_vpn_or_tor: bool = False
    
    # Sub-telemetry components
    biometrics: Optional[BiometricTelemetry] = None
    agentic: Optional[AgenticContext] = None
    
    # Labels & Simulation Ground Truth
    is_fraud: int = 0
    attack_vector: str = "BENIGN_ORGANIC"
    simulation_round: int = 0
    
    # Graph & Velocity Metadata
    sender_past_tx_count_24h: int = 1
    sender_past_volume_24h: float = 100.0
    receiver_inflow_count_24h: int = 5
    cycle_ring_id: Optional[str] = None
    
    # Raw ISO 20022 message payload if applicable
    iso_message_type: Optional[str] = "pacs.008.001.10"
    iso_raw_xml_or_json: Optional[Dict[str, Any]] = None


class DefenseVerdict(BaseModel):
    """Real-Time Blue Team Defense Decision & Audit Telemetry"""
    tx_id: str
    decision: str                            # "ALLOW", "CHALLENGE_STEPUP", "DECLINE_FRAUD"
    fraud_probability: float                 # Calibrated fraud risk score [0.0, 1.0]
    risk_tier: str                           # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    flagged_attack_vector: Optional[str] = None
    iso_rejection_code: Optional[str] = None # e.g. "FRAD", "AGNT", "SYNI", "BIOM", "MULE"
    
    # Explainability & Attribution
    shap_top_features: List[Dict[str, Any]] = Field(default_factory=list)
    mitigation_playbook: str = "Proceed with normal ISO 20022 settlement."
    
    # Latency Telemetry (Benchmarking SLAs)
    tier1_latency_ms: float = 1.2
    tier2_latency_ms: float = 2.4
    tier3_latency_ms: float = 1.8
    total_latency_ms: float = 5.4
    sla_breached: bool = False


class BenchmarkResult(BaseModel):
    """Defense Model Benchmark Evaluation Summary"""
    model_name: str
    dataset_size: int
    fraud_rate: float
    roc_auc: float
    pr_auc: float
    precision: float
    recall: float
    f1_score: float
    fpr_at_99_recall: float
    avg_latency_ms: float
    p99_latency_ms: float
    sla_compliance_rate: float
    per_vector_metrics: Dict[str, Dict[str, float]] = Field(default_factory=dict)
