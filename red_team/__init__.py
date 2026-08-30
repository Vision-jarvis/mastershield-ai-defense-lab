# Red Team Package
from .base_generator import BaseAttackGenerator
from .attack_catalog import (
    AgenticCommerceHijacker,
    SyntheticIdentityClustering,
    BiometricEvasionGenerator,
    PaymentRouterEvaporator,
    DeepfakeStepUpBypass,
    DisputeHallucinationInjector,
    DynamicQRCamouflage,
    AutonomousMuleSwarm
)
from .adversarial_optimizer import AdversarialEvolutionaryOptimizer
from .pipeline import RedTeamSimulationPipeline, red_team_sim
