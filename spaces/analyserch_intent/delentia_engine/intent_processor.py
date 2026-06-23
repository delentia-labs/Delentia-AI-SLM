"""
DelentiaEngine — Unified Pipeline Coordinator
Orchestrates: FDIA Gate → Memory → Core Engine → Escalation Router

This is the single entry point for all Analyserch processing in app.py.
Replaces the previous: IntentCompiler + _call_llm() pattern.

Usage:
    engine = DelentiaEngine()  # singleton, shared across requests
    result = engine.process(query="...", mode="standard")
    # result.confidence → drives escalation
    # result.cache_hit → indicates warm recall
    # result.escalation_level → shows what LLM was used (if any)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import time

from .fdia_gate import FDIAGate, GIGOResult, GIGOStatus
from .memory_layer import MemoryLayer, MemoryHit
from .core_engine import AnalysearchCoreEngine, AnalysearchResult, AnalysearchMode
from .escalation_router import EscalationRouter, EscalationLevel, EscalationResult

logger = logging.getLogger(__name__)


@dataclass
class EngineResult:
    """
    Unified result from DelentiaEngine pipeline.
    All fields needed by app.py UI rendering.
    """
    # Input
    query: str
    mode: str

    # FDIA Gate
    gigo: GIGOResult

    # Core Engine
    keywords: List[Any]                    # List[KeywordResult]
    analysis: Dict[str, Any]
    synthesis: Dict[str, Any]
    mirror_state: Optional[Any]            # MirrorState | None
    research_sources: List[Dict]
    intent_preserved: bool
    confidence: float                      # 0.0 - 1.0

    # Memory
    cache_hit: bool
    cache_access_count: int

    # Escalation
    escalation_level: EscalationLevel
    escalation_result: EscalationResult

    # Routing
    routing_hint: Dict[str, Any]

    # Metadata
    processing_time_ms: float
    engine_version: str = "delentia-native-v1"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def effective_confidence(self) -> float:
        """Confidence after escalation boost (if any)"""
        boost = self.escalation_result.confidence_boost if self.escalation_result.triggered else 0.0
        return min(self.confidence + boost, 1.0)

    @property
    def primary_engine(self) -> str:
        """Human-readable engine name for UI display"""
        if self.cache_hit:
            return "Delentia OS Memory (Warm Recall)"
        if self.escalation_result.triggered:
            model = self.escalation_result.model_used or "external LLM"
            return f"Delentia OS Native + {model}"
        return "Delentia OS Native (ALGO-41/05/26)"

    @property
    def provider_badge(self) -> str:
        """Short badge text for UI"""
        if self.cache_hit:
            return "MEMORY"
        if self.escalation_result.triggered:
            return f"NATIVE+{self.escalation_level.value.upper()}"
        return "NATIVE"

    @property
    def top_keywords_str(self) -> str:
        """Comma-separated top keywords for display"""
        return ", ".join(k.keyword for k in self.keywords[:5]) if self.keywords else "none"


class DelentiaEngine:
    """
    Singleton engine for the Analyserch Intent pipeline.
    
    Thread-safe: Memory layer uses internal locks.
    Initialize once at module level, reuse across requests.
    """

    def __init__(self):
        self.fdia_gate = FDIAGate()
        self.memory = MemoryLayer()
        self.core = AnalysearchCoreEngine()
        self.escalation = EscalationRouter()
        self._request_count = 0
        self._blocked_count = 0
        self._cache_hit_count = 0
        logger.info(
            "DelentiaEngine initialized — "
            "FDIA Gate + Memory Layer + Core Engine + Escalation Router"
        )

    def process(self, query: str, mode: str = "standard") -> EngineResult:
        """
        Full pipeline: FDIA → Memory → Core → Escalation → Result
        
        Args:
            query: Natural language intent query
            mode: "quick" | "standard" | "deep" | "mirror"
            
        Returns:
            EngineResult with all data needed for UI rendering.
        """
        t_start = time.perf_counter()
        self._request_count += 1

        # ── Step 1: FDIA Gate ────────────────────────────────────────────
        gigo = self.fdia_gate.validate(query)
        logger.info(f"FDIA: {gigo.status.value} (score={gigo.fdia_score:.3f})")

        if gigo.is_blocked:
            self._blocked_count += 1
            total_ms = (time.perf_counter() - t_start) * 1000
            # Return early — no memory check, no processing
            return EngineResult(
                query=query, mode=mode, gigo=gigo,
                keywords=[], analysis={}, synthesis={},
                mirror_state=None, research_sources=[],
                intent_preserved=False, confidence=0.0,
                cache_hit=False, cache_access_count=0,
                escalation_level=EscalationLevel.NONE,
                escalation_result=EscalationResult(
                    level=EscalationLevel.NONE, triggered=False,
                    reason="Blocked by FDIA Gate"
                ),
                routing_hint={},
                processing_time_ms=round(total_ms, 2),
            )

        # ── Step 2: Memory Check ─────────────────────────────────────────
        cache_key = f"{query.lower().strip()}::{mode}"
        memory_hit: Optional[MemoryHit] = self.memory.recall(cache_key)

        if memory_hit:
            self._cache_hit_count += 1
            total_ms = (time.perf_counter() - t_start) * 1000
            logger.info(f"⚡ Warm recall: {total_ms:.1f}ms (×{memory_hit.access_count})")

            # Reconstruct EngineResult from cached data
            cached = memory_hit.result
            return EngineResult(
                query=query, mode=mode,
                gigo=gigo,
                keywords=cached.get("keywords", []),
                analysis=cached.get("analysis", {}),
                synthesis=cached.get("synthesis", {}),
                mirror_state=None,  # Don't cache MirrorState objects
                research_sources=cached.get("research_sources", []),
                intent_preserved=cached.get("intent_preserved", True),
                confidence=memory_hit.confidence,
                cache_hit=True,
                cache_access_count=memory_hit.access_count,
                escalation_level=EscalationLevel(cached.get("escalation_level", "none")),
                escalation_result=EscalationResult(
                    level=EscalationLevel.NONE, triggered=False,
                    reason="Served from memory cache"
                ),
                routing_hint=cached.get("routing_hint", {}),
                processing_time_ms=round(total_ms, 2),
            )

        # ── Step 3: Core Engine (Delentia OS Native) ─────────────────────
        try:
            native: AnalysearchResult = self.core.analyze(
                query=query,
                mode=AnalysearchMode(mode) if mode in AnalysearchMode._value2member_map_ else AnalysearchMode.STANDARD,
                max_mirror_iterations=3,
            )
        except Exception as e:
            logger.error(f"Core engine error: {e}")
            # Create minimal fallback result
            native = None

        if native is None:
            total_ms = (time.perf_counter() - t_start) * 1000
            return self._error_result(query, mode, gigo, "Core engine error", total_ms)

        # ── Step 4: Escalation Decision ──────────────────────────────────
        escalation_level = self.escalation.decide(
            confidence=native.confidence,
            mode=mode,
            query_length=len(query),
        )

        # Convert keywords to serializable dicts for caching
        keywords_dicts = [
            {
                "keyword": k.keyword, "score": k.score, "entropy": k.entropy,
                "frequency": k.frequency, "domain": k.domain,
                "category": k.category, "definition": k.definition,
                "implications": k.implications,
            }
            for k in native.keywords
        ]

        escalation_result = self.escalation.escalate(
            level=escalation_level,
            query=query,
            native_result={
                "confidence": native.confidence,
                "analysis": native.analysis,
                "synthesis": native.synthesis,
                "keywords": keywords_dicts,
            },
        )

        # ── Step 5: Store in Memory ──────────────────────────────────────
        total_ms = (time.perf_counter() - t_start) * 1000

        final_confidence = min(native.confidence + escalation_result.confidence_boost, 1.0)

        cache_payload = {
            "keywords": keywords_dicts,
            "analysis": native.analysis,
            "synthesis": native.synthesis,
            "research_sources": native.research_sources,
            "intent_preserved": native.intent_preserved,
            "routing_hint": native.routing_hint,
            "escalation_level": escalation_level.value,
        }

        self.memory.store(
            query=cache_key,
            result=cache_payload,
            confidence=final_confidence,
            processing_time_ms=total_ms,
        )

        logger.info(
            f"Pipeline complete: {total_ms:.1f}ms | "
            f"conf={final_confidence:.2f} | "
            f"escalation={escalation_level.value} | "
            f"keywords={len(native.keywords)}"
        )

        return EngineResult(
            query=query, mode=mode, gigo=gigo,
            keywords=native.keywords,
            analysis=native.analysis,
            synthesis=native.synthesis,
            mirror_state=native.mirror_state,
            research_sources=native.research_sources,
            intent_preserved=native.intent_preserved,
            confidence=final_confidence,
            cache_hit=False,
            cache_access_count=0,
            escalation_level=escalation_level,
            escalation_result=escalation_result,
            routing_hint=native.routing_hint,
            processing_time_ms=round(total_ms, 2),
        )

    def get_stats(self) -> Dict[str, Any]:
        """System-wide statistics"""
        return {
            "requests": self._request_count,
            "blocked": self._blocked_count,
            "cache_hits": self._cache_hit_count,
            "cache_hit_rate": f"{self._cache_hit_count / max(self._request_count, 1):.1%}",
            "memory": self.memory.get_stats(),
            "core": self.core.get_stats(),
            "escalation": self.escalation.get_stats(),
        }

    def _error_result(self, query: str, mode: str, gigo: GIGOResult, error: str, ms: float) -> EngineResult:
        return EngineResult(
            query=query, mode=mode, gigo=gigo,
            keywords=[], analysis={"error": error}, synthesis={},
            mirror_state=None, research_sources=[],
            intent_preserved=False, confidence=0.0,
            cache_hit=False, cache_access_count=0,
            escalation_level=EscalationLevel.NONE,
            escalation_result=EscalationResult(
                level=EscalationLevel.NONE, triggered=False, reason=error
            ),
            routing_hint={},
            processing_time_ms=round(ms, 2),
        )
