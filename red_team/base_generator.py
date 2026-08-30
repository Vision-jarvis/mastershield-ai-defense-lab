"""
MasterShield AI - Red Team Base Adversarial Generator
Mastercard Innovation Challenge @ GFF 2026

Abstract class and common utilities for generating high-fidelity synthetic payment attacks.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
import random
from datetime import datetime, timedelta
from core.models import PaymentTransaction, BiometricTelemetry, AgenticContext
from core.iso20022 import iso_engine


class BaseAttackGenerator(ABC):
    """Abstract Base Class for GenAI Payment Fraud Vector Generators"""

    def __init__(self, vector_id: str, vector_name: str, seed: int = 42):
        self.vector_id = vector_id
        self.vector_name = vector_name
        self.rng = np.random.RandomState(seed)
        self.seed = seed

    @abstractmethod
    def generate_attack(
        self,
        target_account: Optional[str] = None,
        base_amount: Optional[float] = None,
        round_idx: int = 0,
        adversarial_strength: float = 1.0
    ) -> List[PaymentTransaction]:
        """Generates one or more attack transactions representing this vector"""
        pass

    def mutate_payload(self, tx: PaymentTransaction, mutation_rate: float = 0.15) -> PaymentTransaction:
        """Mutates transaction parameters to evade learned defense decision boundaries"""
        mutated = tx.model_copy(deep=True)
        
        # Perturb amount slightly
        if random.random() < mutation_rate:
            jitter = random.uniform(0.92, 1.08)
            mutated.amount = round(mutated.amount * jitter, 2)
            
        # Perturb behavioral biometrics
        if mutated.biometrics and random.random() < mutation_rate:
            mutated.biometrics.mouse_speed_mean += float(self.rng.normal(0, 15.0))
            mutated.biometrics.mouse_acceleration_jitter += float(self.rng.normal(0, 2.0))
            mutated.biometrics.keystroke_dwell_mean += float(self.rng.normal(0, 5.0))
            
        # Perturb agentic context
        if mutated.agentic and random.random() < mutation_rate:
            mutated.agentic.semantic_deviation_score = max(0.01, min(0.99, mutated.agentic.semantic_deviation_score + float(self.rng.normal(0, 0.05))))
            
        return mutated
