"""
MasterShield AI - Co-Evolution Loop CLI Runner
Mastercard Innovation Challenge @ GFF 2026

Usage:
    python scripts/run_co_evolution.py --rounds 5 --samples-per-round 3000
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from closed_loop.co_evolution_engine import coevolution_engine


def main():
    parser = argparse.ArgumentParser(description="MasterShield AI Autonomous Co-Evolution Hardening Runner")
    parser.add_argument("--rounds", type=int, default=5, help="Number of adversarial hardening rounds")
    parser.add_argument("--samples-per-round", type=int, default=3000, help="Transactions per round")
    parser.add_argument("--fraud-ratio", type=float, default=0.08, help="Fraud ratio in training")
    
    args = parser.parse_args()
    
    print(f"[*] Starting {args.rounds}-Round Closed-Loop Co-Evolution Hardening...")
    history = coevolution_engine.run_full_coevolution(
        base_samples_per_round=args.samples_per_round,
        fraud_ratio=args.fraud_ratio
    )
    print(f"[SUCCESS] Co-Evolution Successfully Completed ({len(history)} rounds).")


if __name__ == "__main__":
    main()
