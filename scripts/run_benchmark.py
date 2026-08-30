"""
MasterShield AI - Benchmark CLI Runner
Mastercard Innovation Challenge @ GFF 2026

Usage:
    python scripts/run_benchmark.py --samples 20000 --fraud-ratio 0.005
"""

import os
# Pin thread counts for bit-reproducibility in HistGradientBoostingClassifier
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from closed_loop.benchmark_suite import benchmark_suite
from closed_loop.co_evolution_engine import coevolution_engine


def main():
    parser = argparse.ArgumentParser(description="MasterShield AI Benchmark Evaluation Runner")
    parser.add_argument("--samples", type=int, default=20000, help="Total transactions in benchmark test set")
    parser.add_argument("--fraud-ratio", type=float, default=0.005, help="Realistic fraud ratio (default: 0.005 / 0.5%)")
    parser.add_argument("--train-first", action="store_true", default=True, help="Run initial co-evolution training")
    
    args = parser.parse_args()
    
    if args.train_first:
        print("[*] Initializing and training MasterShield AI defense models with Co-Evolution...")
        coevolution_engine.run_full_coevolution(base_samples_per_round=3000, fraud_ratio=0.05)
        
    print(f"\n[*] Executing Benchmark on {args.samples} transactions (Realistic Fraud Rate: {args.fraud_ratio:.2%})...")
    results = benchmark_suite.run_benchmark(n_samples=args.samples, fraud_ratio=args.fraud_ratio, seed=999)
    print("[SUCCESS] Benchmark Execution Complete.")


if __name__ == "__main__":
    main()
