"""
delentia_engine — Delentia OS Native Processing Package
Ported from Delentia-OS for HF Space deployment (Option A: direct copy)

Pipeline:
  FDIA Gate → Memory Check → AnalysearchEngine → EscalationRouter → Result

No external LLMs required for standard operation.
External LLMs called ONLY via EscalationRouter when confidence < threshold.
"""

from .intent_processor import DelentiaEngine, EngineResult
from .core_engine import AnalysearchCoreEngine, AnalysearchResult, AnalysearchMode
from .memory_layer import MemoryLayer, MemoryHit
from .fdia_gate import FDIAGate, GIGOResult, GIGOStatus
from .escalation_router import EscalationRouter, EscalationLevel, EscalationResult

__all__ = [
    "DelentiaEngine",
    "EngineResult",
    "MemoryLayer",
    "MemoryHit",
    "FDIAGate",
    "GIGOResult",
    "EscalationRouter",
    "EscalationLevel",
]

__version__ = "1.0.0"
