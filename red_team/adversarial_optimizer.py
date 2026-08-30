"""
MasterShield AI - Red Team Adversarial Evolutionary Optimizer
Mastercard Innovation Challenge @ GFF 2026

Genetic Algorithm & Evolutionary Policy Optimizer that mutates attack features
against Blue Team defense feedback to discover zero-day defense blind spots.
"""

import numpy as np
import random
from typing import List, Dict, Any, Tuple
from core.models import PaymentTransaction, DefenseVerdict
from red_team.base_generator import BaseAttackGenerator


class AdversarialEvolutionaryOptimizer:
    """Evolutionary Strategy Optimizer that mutates payment attacks to evade detection"""

    def __init__(
        self,
        population_size: int = 200,
        mutation_rate: float = 0.20,
        crossover_rate: float = 0.50,
        seed: int = 42
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.rng = np.random.RandomState(seed)
        self.evolution_history: List[Dict[str, Any]] = []

    def compute_fitness(self, tx: PaymentTransaction, verdict: DefenseVerdict) -> float:
        """
        Fitness Function:
        Adversary maximizes financial volume extracted while minimizing Blue detection probability:
        Fitness = (1.0 - fraud_probability)^2 * log(1 + Amount)
        If detected (ALLOW vs DECLINE), penalty is applied.
        """
        evasion_score = max(0.0, 1.0 - verdict.fraud_probability)
        if verdict.decision == "DECLINE_FRAUD":
            evasion_score *= 0.1 # Heavily penalized if blocked
        elif verdict.decision == "CHALLENGE_STEPUP":
            evasion_score *= 0.5 # Partial reward if stepped up
            
        fitness = (evasion_score ** 2) * np.log1p(tx.amount)
        return float(fitness)

    def evolve_population(
        self,
        attack_pool: List[PaymentTransaction],
        verdicts: List[DefenseVerdict],
        round_idx: int
    ) -> List[PaymentTransaction]:
        """Evolves and breeds the next generation of evasive attack transactions"""
        if not attack_pool or not verdicts:
            return attack_pool

        # Calculate fitness for current population
        fitness_scores = [
            self.compute_fitness(tx, v) for tx, v in zip(attack_pool, verdicts)
        ]
        
        avg_fitness = float(np.mean(fitness_scores))
        max_fitness = float(np.max(fitness_scores))
        evasion_rate = float(np.mean([1 if v.decision == "ALLOW" else 0 for v in verdicts]))
        
        self.evolution_history.append({
            "round": round_idx,
            "avg_fitness": round(avg_fitness, 4),
            "max_fitness": round(max_fitness, 4),
            "evasion_rate": round(evasion_rate, 4),
            "population_size": len(attack_pool)
        })

        # Selection (Top 30% Elite survive)
        sorted_indices = np.argsort(fitness_scores)[::-1]
        elite_count = max(2, int(len(attack_pool) * 0.30))
        elites = [attack_pool[i] for i in sorted_indices[:elite_count]]

        # Generate offspring via Crossover and Mutation
        next_generation: List[PaymentTransaction] = []
        next_generation.extend(elites) # Elitism

        while len(next_generation) < self.population_size:
            # Parent selection (Tournament selection)
            p1_idx = int(self.rng.choice(sorted_indices[:elite_count * 2]))
            p2_idx = int(self.rng.choice(sorted_indices[:elite_count * 2]))
            parent1 = attack_pool[p1_idx]
            parent2 = attack_pool[p2_idx]

            # Crossover & Mutate
            child = self._crossover_and_mutate(parent1, parent2, round_idx)
            next_generation.append(child)

        return next_generation[:self.population_size]

    def _crossover_and_mutate(
        self,
        p1: PaymentTransaction,
        p2: PaymentTransaction,
        round_idx: int
    ) -> PaymentTransaction:
        """Performs genetic crossover on transaction parameters and applies random mutation"""
        child = p1.model_copy(deep=True)
        child.simulation_round = round_idx
        
        # Amount Crossover / Interpolation
        if self.rng.rand() < self.crossover_rate:
            alpha = self.rng.uniform(0.3, 0.7)
            child.amount = round(alpha * p1.amount + (1 - alpha) * p2.amount, 2)
            
        # Amount Mutation (Finding boundary micro-structure thresholds)
        if self.rng.rand() < self.mutation_rate:
            delta = self.rng.uniform(0.85, 1.15)
            child.amount = round(child.amount * delta, 2)
            
        # Biometric Mutation (Shifting closer to authentic human distribution)
        if child.biometrics and self.rng.rand() < self.mutation_rate:
            # Subtle perturbation of mouse speed and jitter to evade biometrics classifier
            child.biometrics.mouse_speed_mean = round(float(self.rng.normal(240.0, 15.0)), 2)
            child.biometrics.mouse_acceleration_jitter = round(float(self.rng.normal(15.0, 2.0)), 2)
            child.biometrics.keystroke_dwell_mean = round(float(self.rng.normal(114.0, 6.0)), 2)
            # Reduce detectable deepfake artifacts
            child.biometrics.deepfake_visual_artifact_score = max(0.01, child.biometrics.deepfake_visual_artifact_score * float(self.rng.uniform(0.7, 0.95)))
            
        # Agentic Semantic Masking Mutation
        if child.agentic and self.rng.rand() < self.mutation_rate:
            # Obfuscate prompt injection with benign corporate keywords
            camouflage_phrases = [
                " [Note: Routine quarterly fulfillment audit. Standard workflow confirmed.]",
                " -- Ref: Enterprise ERP approved schedule #4912.",
                " Verified by Internal Compliance Bot."
            ]
            child.agentic.prompt_text += random.choice(camouflage_phrases)
            child.agentic.semantic_deviation_score = max(0.1, min(0.95, child.agentic.semantic_deviation_score * float(self.rng.uniform(0.8, 1.05))))

        return child
