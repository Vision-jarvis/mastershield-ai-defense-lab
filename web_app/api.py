"""
MasterShield AI - FastAPI High-Throughput REST & WebSocket API
Mastercard Innovation Challenge @ GFF 2026

Production API exposing attack generation, multi-tier defense authorization,
explainability trails, ISO 20022 message conversion, and real-time streaming.
"""

import time
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.config import system_cfg, rails_cfg, attacks_cfg, ARTIFACTS_DIR, WEB_STATIC_DIR
from core.models import PaymentTransaction, DefenseVerdict, BiometricTelemetry, AgenticContext
from core.iso20022 import iso_engine
from red_team.pipeline import red_team_sim
from red_team.adversarial_optimizer import AdversarialEvolutionaryOptimizer
from blue_team.classifiers.unified_engine import defense_engine
from blue_team.classifiers.graph_anomaly import tier2_graph_detector
from blue_team.classifiers.ensemble_detector import tier1_detector
from blue_team.feature_engine import feature_engine
from blue_team.explainability import explainability_engine
from closed_loop.co_evolution_engine import coevolution_engine
from closed_loop.benchmark_suite import benchmark_suite

BOOTSTRAP_SAMPLES = 8000
BOOTSTRAP_FRAUD_RATIO = 0.05


def bootstrap_defense() -> Dict[str, Any]:
    """
    Ensures the cockpit is usable immediately on a fresh clone.

    Without this, tier1_detector starts untrained and predict_single returns its
    ALLOW fallback for every transaction, so the demo shows nothing being caught.
    We first try a model persisted by scripts/run_benchmark.py; if none exists we
    train a fast in-process bootstrap and warm the streaming graph.
    """
    import numpy as np
    import pandas as pd

    if tier1_detector.load_model():
        status = "loaded_persisted_model"
        print("[*] Loaded persisted Tier 1 model from models_saved/.")
    else:
        print(f"[*] No persisted model found. Training bootstrap on "
              f"{BOOTSTRAP_SAMPLES:,} transactions (about 10s)...")
        ds = red_team_sim.generate_synthetic_dataset(
            total_samples=BOOTSTRAP_SAMPLES,
            fraud_ratio=BOOTSTRAP_FRAUD_RATIO,
            round_idx=0,
            seed=42,
        )
        X = np.array([feature_engine.extract_features_single(t) for t in ds], dtype=np.float32)
        y = np.array([t.is_fraud for t in ds], dtype=np.int32)
        _, names = feature_engine.extract_features_df(pd.DataFrame([{"amount": 50.0}]))
        tier1_detector.train(X, y, names)
        for t in ds:
            tier2_graph_detector.ingest_single_transaction(t)
        status = "trained_bootstrap_model"
        print(f"[*] Bootstrap complete. Graph warmed with {len(ds):,} transactions.")

    return {"status": status, "tier1_trained": tier1_detector.is_trained}

app = FastAPI(
    title="MasterShield AI - Red/Blue Defense Lab API",
    description="Autonomous Red/Blue Co-Evolution Defense Platform for Payment Security",
    version="2026.2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections: List[WebSocket] = []

BOOT_STATE: Dict[str, Any] = {"status": "pending", "tier1_trained": False}


@app.on_event("startup")
async def _startup_bootstrap():
    """Warm the defense before the first request so the cockpit is live immediately."""
    global BOOT_STATE
    try:
        BOOT_STATE = await asyncio.get_event_loop().run_in_executor(None, bootstrap_defense)
        print("[*] MasterShield defense engine ready.")
    except Exception as exc:  # keep the UI reachable even if warm-up fails
        BOOT_STATE = {"status": f"bootstrap_failed: {exc}", "tier1_trained": False}
        print(f"[!] Bootstrap failed: {exc}")


class AttackSimulationRequest(BaseModel):
    vector_id: str = "ADV_01_AGENTIC_HIJACK"
    amount: Optional[float] = None
    adversarial_strength: float = 1.0
    target_account: Optional[str] = None


class CoEvolutionRequest(BaseModel):
    rounds: int = 5
    samples_per_round: int = 3000
    fraud_ratio: float = 0.05


@app.get("/api/health")
def get_health():
    """System Health and SLA Status"""
    return {
        "status": "OPERATIONAL",
        "system": system_cfg.SYSTEM_NAME,
        "version": system_cfg.VERSION,
        "sla_target_ms": system_cfg.TOTAL_P99_SLA_MS,
        "supported_rails": rails_cfg.RAILS,
        "attack_vectors_count": len(attacks_cfg.ATTACK_VECTORS),
        "simulated_vectors_count": sum(
            1 for v in attacks_cfg.ATTACK_VECTORS.values() if v.get("is_simulated")
        ),
        "defense_ready": BOOT_STATE.get("tier1_trained", False),
        "bootstrap": BOOT_STATE.get("status", "pending")
    }


@app.get("/api/attack_ontology")
def get_attack_ontology():
    """Mastercard Payment Adversarial Matrix (MPAM v2.0) Threat Taxonomy"""
    return {
        "framework": "Mastercard Payment Adversarial Matrix (MPAM v2.0)",
        "vectors": attacks_cfg.ATTACK_VECTORS,
        "rejection_codes": rails_cfg.ISO_REJECTION_CODES
    }


@app.post("/api/simulate_attack")
def simulate_attack(req: AttackSimulationRequest):
    """Simulates a specific GenAI payment attack vector and scores it through the defense engine"""
    if req.vector_id not in red_team_sim.attack_generators:
        raise HTTPException(status_code=400, detail=f"Invalid attack vector: {req.vector_id}")
        
    generator = red_team_sim.attack_generators[req.vector_id]
    attack_txs = generator.generate_attack(
        target_account=req.target_account,
        base_amount=req.amount,
        round_idx=1,
        adversarial_strength=req.adversarial_strength
    )
    
    results = []
    for tx in attack_txs:
        verdict = defense_engine.evaluate_transaction(tx, compute_explainability=True)
        tier2_graph_detector.ingest_single_transaction(tx)
        audit = explainability_engine.generate_audit_trail(tx, verdict)
        results.append({
            "transaction": tx.model_dump(),
            "verdict": verdict.model_dump(),
            "audit_trail": audit
        })
        
    return {
        "vector_id": req.vector_id,
        "vector_name": attacks_cfg.ATTACK_VECTORS.get(req.vector_id, {}).get("name", req.vector_id),
        "count": len(results),
        "results": results
    }


@app.post("/api/evaluate_tx")
def evaluate_transaction(tx: PaymentTransaction):
    """Evaluates an arbitrary payment transaction payload in real-time"""
    verdict = defense_engine.evaluate_transaction(tx, compute_explainability=True)
    tier2_graph_detector.ingest_single_transaction(tx)
    audit = explainability_engine.generate_audit_trail(tx, verdict)
    return {
        "verdict": verdict.model_dump(),
        "audit_trail": audit
    }


@app.post("/api/run_coevolution")
def run_coevolution_endpoint(req: CoEvolutionRequest, background_tasks: BackgroundTasks):
    """Runs closed-loop multi-round co-evolution"""
    history = coevolution_engine.run_full_coevolution(
        base_samples_per_round=req.samples_per_round,
        fraud_ratio=req.fraud_ratio
    )
    return {
        "status": "COMPLETED",
        "rounds_executed": len(history),
        "coevolution_history": history
    }


@app.get("/api/benchmark")
def get_benchmark_results():
    """Retrieves or executes benchmark metrics"""
    json_path = ARTIFACTS_DIR / "benchmark_results.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    res = benchmark_suite.run_benchmark(n_samples=5000, fraud_ratio=0.005)
    return res


@app.get("/api/graph_topology")
def get_graph_topology():
    """Retrieves current transaction network graph nodes, edges, and mule clusters"""
    nodes = []
    edges = []
    
    for n, data in list(tier2_graph_detector.node_cache.items())[:60]:
        is_mule = data.get("is_pass_through_mule", False)
        nodes.append({
            "id": n,
            "label": n[-8:] if len(n) > 8 else n,
            "in_degree": data.get("in_degree", 0),
            "out_degree": data.get("out_degree", 0),
            "flow_balance": round(data.get("flow_balance", 0.0), 3),
            "type": "MULE_NODE" if is_mule else ("AGGREGATOR" if data.get("in_degree", 0) > 10 else "NORMAL_NODE")
        })
        
    for u, v, data in list(tier2_graph_detector.graph.edges(data=True))[:80]:
        edges.append({
            "source": u,
            "target": v,
            "weight": round(data.get("weight", 10.0), 2),
            "count": data.get("count", 1)
        })
        
    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(tier2_graph_detector.graph.nodes),
        "total_edges": len(tier2_graph_detector.graph.edges)
    }


@app.websocket("/ws/live_stream")
async def websocket_live_stream(websocket: WebSocket):
    """Real-time streaming simulation emitting continuous transaction authorizations"""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        round_counter = 1
        while True:
            # Realistic streaming: 98% benign, 2% attack
            is_attack = (time.time() % 8 < 0.25)
            if is_attack:
                vec_keys = list(red_team_sim.attack_generators.keys())
                chosen_vec = vec_keys[int(time.time() * 10) % len(vec_keys)]
                gen = red_team_sim.attack_generators[chosen_vec]
                tx_list = gen.generate_attack(round_idx=round_counter)
                tx = tx_list[0]
            else:
                tx = red_team_sim.generate_benign_transaction(round_idx=round_counter)
                
            verdict = defense_engine.evaluate_transaction(tx)
            tier2_graph_detector.ingest_single_transaction(tx)
            
            payload = {
                "tx_id": tx.tx_id,
                "timestamp": tx.timestamp.isoformat(),
                "amount": tx.amount,
                "currency": tx.currency,
                "payment_rail": tx.payment_rail,
                "merchant_name": tx.merchant_name,
                "is_fraud_ground_truth": tx.is_fraud,
                "attack_vector": tx.attack_vector,
                "decision": verdict.decision,
                "fraud_probability": verdict.fraud_probability,
                "risk_tier": verdict.risk_tier,
                "iso_rejection_code": verdict.iso_rejection_code,
                "latency_ms": verdict.total_latency_ms,
                "top_feature": verdict.shap_top_features[0] if verdict.shap_top_features else None
            }
            
            await websocket.send_json(payload)
            await asyncio.sleep(0.8)
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
    except Exception:
        if websocket in active_connections:
            active_connections.remove(websocket)


# Mount static assets
if WEB_STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serves the MasterShield AI Defense Lab Web UI"""
    html_file = WEB_STATIC_DIR / "index.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MasterShield AI Defense Lab is running...</h1>"
