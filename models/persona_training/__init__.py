"""
Persona Training Module

This module provides tools for training AI agents based on persona filling logic.
"""

from .train import (
    load_persona,
    load_filling_logic,
    load_training_examples,
    create_training_dataset,
    train_persona_model,
    PersonaConfig,
    FillingLogic,
    TrainingExample
)

from .agent import PersonaAgent, FillResult

__all__ = [
    'PersonaAgent',
    'FillResult',
    'load_persona',
    'load_filling_logic', 
    'load_training_examples',
    'create_training_dataset',
    'train_persona_model',
    'PersonaConfig',
    'FillingLogic',
    'TrainingExample'
]
