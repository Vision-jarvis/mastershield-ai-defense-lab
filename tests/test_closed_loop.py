"""
MasterShield AI - Closed-Loop Co-Evolution Integration Tests
Mastercard Innovation Challenge @ GFF 2026
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from closed_loop.co_evolution_engine import coevolution_engine
from closed_loop.benchmark_suite import benchmark_suite


def test_coevolution_round_execution():
    """Runs a 2-round micro co-evolution cycle to verify automated learning pipeline"""
    history = coevolution_engine.run_full_coevolution(base_samples_per_round=400, fraud_ratio=0.08, rounds=2)
    assert len(history) >= 2, "Co-evolution history must contain at least 2 recorded phases"
    # Verify that hard negative mining and retraining hardens defense F1 or suppresses FPR
    assert history[-1]["f1_score"] >= history[0]["f1_score"] or history[-1]["fpr"] <= history[0]["fpr"], "Co-evolution must improve precision/recall balance"
    assert history[-1]["p99_latency_ms"] < 35.0


def test_benchmark_suite_execution():
    """Runs benchmark suite on 500 test transactions"""
    res = benchmark_suite.run_benchmark(n_samples=500, fraud_ratio=0.08, save_artifact=False)
    assert "global_metrics" in res
    assert res["global_metrics"]["roc_auc"] > 0.75
    assert res["global_metrics"]["precision"] > 0.80
    assert res["latency_profile_ms"]["p99"] < 35.0
    assert len(res["per_vector_breakdown"]) > 0
