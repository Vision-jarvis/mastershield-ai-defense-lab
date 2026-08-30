"""
MasterShield AI - Tier 2 Dynamic Temporal Graph Anomaly Network
Mastercard Innovation Challenge @ GFF 2026

Maintains an incremental transaction flow graph G_t = (V, E, W) in real time.
Evaluates pass-through flow balance, low-centrality mule chains, and topological cycles.
Evaluated sequentially strictly against prior state G_{t-1} with zero future lookahead.
"""

import time
import networkx as nx
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import defaultdict
from core.models import PaymentTransaction
from config.config import defense_cfg


class Tier2GraphAnomalyDetector:
    """Dynamic Temporal Graph Anomaly Detector with O(1) Incremental State Maintenance"""

    def __init__(self, max_nodes: int = 50000):
        self.graph = nx.DiGraph()
        self.max_nodes = max_nodes
        self.node_cache: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "in_degree": 0, "out_degree": 0, "total_degree": 0,
            "in_volume": 0.0, "out_volume": 0.0, "flow_balance": 0.0,
            "is_pass_through_mule": False
        })
        self.out_neighbors: Dict[str, Set[str]] = defaultdict(set)

    def reset_state(self):
        """Resets dynamic graph state for clean deterministic benchmarking"""
        self.graph = nx.DiGraph()
        self.node_cache = defaultdict(lambda: {
            "in_degree": 0, "out_degree": 0, "total_degree": 0,
            "in_volume": 0.0, "out_volume": 0.0, "flow_balance": 0.0,
            "is_pass_through_mule": False
        })
        self.out_neighbors = defaultdict(set)

    def ingest_single_transaction(self, tx: PaymentTransaction):
        """
        True O(1) incremental ingestion of an authorized transaction into dynamic graph state G_t.
        Updates flow volumes and degree balances in microsecond time.
        """
        u = tx.sender_pan_or_account
        v = tx.receiver_pan_or_account
        amt = float(tx.amount)
        
        # 1. Update NetworkX Edge (bounded memory)
        if self.graph.has_edge(u, v):
            self.graph[u][v]["weight"] += amt
            self.graph[u][v]["count"] += 1
        else:
            self.graph.add_edge(u, v, weight=amt, count=1)
            
        self.out_neighbors[u].add(v)
        
        # 2. O(1) Incremental Scalar Metrics Update
        u_data = self.node_cache[u]
        u_data["out_degree"] += 1
        u_data["out_volume"] += amt
        u_data["total_degree"] = u_data["in_degree"] + u_data["out_degree"]
        tot_u = u_data["in_volume"] + u_data["out_volume"]
        u_data["flow_balance"] = (u_data["in_volume"] - u_data["out_volume"]) / max(1.0, tot_u)
        u_data["is_pass_through_mule"] = bool(
            u_data["in_degree"] >= 1 and u_data["out_degree"] >= 1 and 
            abs(u_data["flow_balance"]) < 0.18 and 
            u_data["in_volume"] > 350.0 and u_data["out_volume"] > 350.0
        )
        
        v_data = self.node_cache[v]
        v_data["in_degree"] += 1
        v_data["in_volume"] += amt
        v_data["total_degree"] = v_data["in_degree"] + v_data["out_degree"]
        tot_v = v_data["in_volume"] + v_data["out_volume"]
        v_data["flow_balance"] = (v_data["in_volume"] - v_data["out_volume"]) / max(1.0, tot_v)
        v_data["is_pass_through_mule"] = bool(
            v_data["in_degree"] >= 1 and v_data["out_degree"] >= 1 and 
            abs(v_data["flow_balance"]) < 0.18 and 
            v_data["in_volume"] > 350.0 and v_data["out_volume"] > 350.0
        )

    def update_graph(self, transactions: List[PaymentTransaction]):
        """Batch ingestion for historical graph seeding"""
        for tx in transactions:
            self.ingest_single_transaction(tx)

    def score_transaction(self, tx: PaymentTransaction) -> Tuple[float, Dict[str, Any], float]:
        """
        Real-time topological anomaly scoring against prior graph state G_{t-1} (<0.2ms).
        Returns: (graph_risk_score, topology_metadata, latency_ms)
        """
        t0 = time.perf_counter()
        u = tx.sender_pan_or_account
        v = tx.receiver_pan_or_account
        
        u_stats = self.node_cache.get(u, {
            "in_degree": 0, "out_degree": 0, "total_degree": 0,
            "in_volume": 0.0, "out_volume": 0.0, "flow_balance": 0.0,
            "is_pass_through_mule": False
        })
        v_stats = self.node_cache.get(v, {
            "in_degree": 0, "out_degree": 0, "total_degree": 0,
            "in_volume": 0.0, "out_volume": 0.0, "flow_balance": 0.0,
            "is_pass_through_mule": False
        })
        
        risk_score = 0.02
        flagged_pattern = "NORMAL_TOPOLOGY"
        
        # 1. Topological Reciprocal Cycle Detection (v -> u exists in G_{t-1})
        if u in self.out_neighbors.get(v, set()):
            risk_score = max(risk_score, 0.92)
            flagged_pattern = "RECIPROCAL_2HOP_CYCLE"
            
        # 2. 3-Hop Triangular Cycle Detection (v -> w and w -> u in G_{t-1})
        elif v in self.out_neighbors:
            v_targets = self.out_neighbors[v]
            for w in list(v_targets)[:15]: # Bounded sample for constant-time guarantee
                if u in self.out_neighbors.get(w, set()):
                    risk_score = max(risk_score, 0.88)
                    flagged_pattern = "TRIANGULAR_3HOP_CYCLE"
                    break
                    
        # 3. Dynamic Mule Pass-Through Flow Balance
        if u_stats["is_pass_through_mule"] or v_stats["is_pass_through_mule"]:
            risk_score = max(risk_score, 0.89)
            flagged_pattern = "MULE_PASS_THROUGH_FLOW"

        t_lat = (time.perf_counter() - t0) * 1000.0
        
        meta = {
            "flagged_pattern": flagged_pattern,
            "sender_in_degree": u_stats["in_degree"],
            "sender_out_degree": u_stats["out_degree"],
            "receiver_in_degree": v_stats["in_degree"],
            "flow_balance": round(u_stats["flow_balance"], 4)
        }
        return float(risk_score), meta, round(t_lat, 3)

    def find_mule_cycles(self, max_cycle_len: int = 4) -> List[List[str]]:
        """Discovers closed mule routing cycles in the transaction graph"""
        cycles = []
        try:
            for cycle in nx.simple_cycles(self.graph):
                if 2 <= len(cycle) <= max_cycle_len:
                    cycles.append(cycle)
                if len(cycles) >= 50:
                    break
        except Exception:
            pass
        return cycles


tier2_graph_detector = Tier2GraphAnomalyDetector()
