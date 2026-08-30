"""
MasterShield AI - Red Team Unit & Integration Tests
Mastercard Innovation Challenge @ GFF 2026
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from red_team.pipeline import red_team_sim
from red_team.adversarial_optimizer import AdversarialEvolutionaryOptimizer
from config.config import attacks_cfg


def test_all_attack_vectors_generate_valid_transactions():
    """Verifies that all 8 attack vectors produce valid PaymentTransaction objects"""
    for vec_id, gen in red_team_sim.attack_generators.items():
        tx_list = gen.generate_attack(round_idx=1, adversarial_strength=1.0)
        assert len(tx_list) > 0, f"Generator {vec_id} returned empty transaction list"
        
        for tx in tx_list:
            assert tx.is_fraud == 1, f"Attack transaction {tx.tx_id} must have is_fraud=1"
            assert tx.attack_vector == vec_id
            assert tx.amount > 0, "Transaction amount must be positive"
            assert len(tx.sender_pan_or_account) > 0
            assert len(tx.receiver_pan_or_account) > 0


def test_benign_transaction_generator():
    """Verifies benign transactions follow organic baseline distributions"""
    tx = red_team_sim.generate_benign_transaction(round_idx=0)
    assert tx.is_fraud == 0
    assert tx.attack_vector == "BENIGN_ORGANIC"
    assert tx.amount > 0
    if tx.biometrics:
        assert tx.biometrics.is_spoofed is False
        assert tx.biometrics.deepfake_visual_artifact_score < 0.15


def test_adversarial_mutation():
    """Verifies evolutionary mutation perturbs transaction parameters without corrupting schema"""
    optimizer = AdversarialEvolutionaryOptimizer(mutation_rate=0.5, seed=42)
    gen = red_team_sim.attack_generators["ADV_01_AGENTIC_HIJACK"]
    original_tx = gen.generate_attack()[0]
    
    mutated = optimizer._crossover_and_mutate(original_tx, original_tx, round_idx=2)
    assert mutated.simulation_round == 2
    assert mutated.is_fraud == 1
    assert mutated.amount > 0
