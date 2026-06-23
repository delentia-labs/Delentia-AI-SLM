"""
Escalation Router — External LLM Decision Engine
Determines WHEN and HOW to escalate to external LLMs.

Design Philosophy:
  "Delentia OS first. External LLMs as a last resort."
  
Escalation Levels (tuned for maximum efficiency):
  NONE    → confidence ≥ 0.70, mode QUICK/STANDARD  (native only, $0 cost)
  LITE    → confidence 0.50-0.69                     (native + note, $0 cost)
  TIER_8  → confidence 0.30-0.49 OR mode DEEP        (cheapest LLM, DeepSeek/Qwen)
  TIER_4  → confidence < 0.30 OR mode MIRROR         (strong LLM, Typhoon/DeepSeek)
  TIER_S  → explicit override or critical system call (Claude/GPT-4, rare)

External LLM calls go through OpenRouter via OPENROUTER_API_KEY (env).
If no key configured: stays at NONE/LITE regardless of confidence.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from enum import Enum
import os
import json
import logging

logger = logging.getLogger(__name__)


class EscalationLevel(str, Enum):
    NONE = "none"        # Native Delentia OS only (fastest, $0)
    LITE = "lite"        # Native + confidence warning
    TIER_8 = "tier_8"    # Cheap LLM (DeepSeek, Qwen 2.5 72B) ~$0.0003/1k
    TIER_4 = "tier_4"    # Strong LLM (Typhoon, DeepSeek) ~$0.0008/1k
    TIER_S = "tier_s"    # Sovereign LLM (Claude, GPT-4) ~$0.003/1k


# Tier-to-model mapping (via OpenRouter)
ESCALATION_MODELS: Dict[EscalationLevel, Dict[str, Any]] = {
    EscalationLevel.TIER_8: {
        "models": [
            "qwen/qwen-2.5-72b-instruct",
            "deepseek/deepseek-chat",
        ],
        "max_tokens": 512,
        "temperature": 0.1,
        "cost_estimate": "~$0.0003/1k tokens",
        "description": "Fast & efficient — for moderate enrichment",
    },
    EscalationLevel.TIER_4: {
        "models": [
            "scb10x/typhoon-v1.5x-70b-instruct",
            "deepseek/deepseek-chat",
        ],
        "max_tokens": 1024,
        "temperature": 0.2,
        "cost_estimate": "~$0.0008/1k tokens",
        "description": "Strong reasoning — for complex intent",
    },
    EscalationLevel.TIER_S: {
        "models": [
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4-turbo",
        ],
        "max_tokens": 2048,
        "temperature": 0.3,
        "cost_estimate": "~$0.01/1k tokens",
        "description": "Sovereign — for critical/ambiguous intent",
    },
}

# Escalation prompt for LLM enrichment
ESCALATION_PROMPT_TEMPLATE = """\
You are the Delentia OS Intelligence Escalation Layer.
A native analysis was performed with confidence={confidence:.0%}.
Enrich and validate this intent analysis.

ORIGINAL QUERY: {query}

NATIVE ANALYSIS SUMMARY:
- Keywords: {keywords}
- Query Type: {query_type}
- Disciplines: {disciplines}
- Complexity: {complexity}
- Innovation Potential: {innovation:.0%}

TASK: Provide brief JSON enrichment:
{{
  "enhanced_hypothesis": "...",
  "missing_considerations": ["..."],
  "recommended_architecture": "...",
  "confidence_boost": 0.0-0.3
}}
Respond ONLY with valid JSON."""


@dataclass
class EscalationResult:
    """Result of escalation attempt"""
    level: EscalationLevel
    triggered: bool
    model_used: Optional[str] = None
    enhanced_hypothesis: Optional[str] = None
    missing_considerations: List[str] = field(default_factory=list)
    recommended_architecture: Optional[str] = None
    confidence_boost: float = 0.0
    cost_tokens: int = 0
    latency_ms: float = 0.0
    error: Optional[str] = None
    reason: str = ""


class EscalationRouter:
    """
    Decides when/how to escalate to external LLMs.
    
    Never blocks the pipeline — returns EscalationResult(triggered=False)
    if no escalation needed or if API unavailable.
    """

    # Thresholds (tuned for max system efficiency)
    THRESHOLD_NATIVE = 0.70    # ≥ this → native only (no LLM)
    THRESHOLD_LITE = 0.50      # ≥ this → native + warning
    THRESHOLD_TIER8 = 0.30     # ≥ this → Tier-8 LLM
    # < THRESHOLD_TIER8 → Tier-4 LLM

    def __init__(self):
        self._api_key = (
            os.environ.get("RCT_CORE_BRAIN_KEY")
            or os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        self._base_url = os.environ.get("RCT_MODEL_BACKEND_URL", "https://openrouter.ai/api/v1")
        self._stats = {
            "total_decisions": 0,
            "escalated_tier8": 0,
            "escalated_tier4": 0,
            "escalated_tierS": 0,
            "stayed_native": 0,
            "total_tokens_used": 0,
        }

    def decide(
        self,
        confidence: float,
        mode: str,
        query_length: int = 0,
        force_level: Optional[EscalationLevel] = None,
    ) -> EscalationLevel:
        """
        Determine escalation level based on confidence and mode.
        
        Args:
            confidence: 0.0-1.0 from AnalysearchCoreEngine
            mode: "quick", "standard", "deep", "mirror"
            query_length: length of query (longer = may need more)
            force_level: Override escalation level
            
        Returns:
            EscalationLevel enum value
        """
        self._stats["total_decisions"] += 1

        if force_level:
            return force_level

        # Mode-based overrides
        if mode == "mirror":
            # Mirror mode always benefits from 2-model adversarial exchange
            if self._api_key:
                return EscalationLevel.TIER_4
            return EscalationLevel.LITE

        if mode == "deep":
            # Deep mode escalates if confidence not already high
            if confidence < self.THRESHOLD_NATIVE and self._api_key:
                return EscalationLevel.TIER_8

        # Confidence-based routing
        if confidence >= self.THRESHOLD_NATIVE:
            self._stats["stayed_native"] += 1
            return EscalationLevel.NONE

        if confidence >= self.THRESHOLD_LITE:
            # Have API key? Lightweight enrichment worth it
            if self._api_key and mode in ("deep", "mirror"):
                self._stats["escalated_tier8"] += 1
                return EscalationLevel.TIER_8
            return EscalationLevel.LITE

        if confidence >= self.THRESHOLD_TIER8:
            if self._api_key:
                self._stats["escalated_tier8"] += 1
                return EscalationLevel.TIER_8
            return EscalationLevel.LITE

        # Low confidence
        if self._api_key:
            self._stats["escalated_tier4"] += 1
            return EscalationLevel.TIER_4

        return EscalationLevel.LITE

    def escalate(
        self,
        level: EscalationLevel,
        query: str,
        native_result: Dict[str, Any],
    ) -> EscalationResult:
        """
        Execute escalation call to external LLM.
        
        Returns EscalationResult. Never raises — errors are captured.
        If level is NONE or LITE, returns immediately without API call.
        """
        import time
        start = time.perf_counter()

        if level in (EscalationLevel.NONE, EscalationLevel.LITE):
            reason = (
                "Native confidence sufficient — no LLM escalation needed"
                if level == EscalationLevel.NONE
                else "Moderate confidence — native result returned with advisory"
            )
            return EscalationResult(
                level=level,
                triggered=False,
                reason=reason,
            )

        if not self._api_key:
            return EscalationResult(
                level=level,
                triggered=False,
                reason="No API key configured — staying native",
                error="OPENROUTER_API_KEY / RCT_CORE_BRAIN_KEY not set",
            )

        # Build prompt
        analysis = native_result.get("analysis", {})
        synthesis = native_result.get("synthesis", {})
        keywords = native_result.get("keywords", [])

        prompt = ESCALATION_PROMPT_TEMPLATE.format(
            confidence=native_result.get("confidence", 0.5),
            query=query[:300],
            keywords=", ".join(
                k.get("keyword", k) if isinstance(k, dict) else str(k)
                for k in keywords[:5]
            ),
            query_type=analysis.get("query_type", "exploration"),
            disciplines=synthesis.get("disciplines_detected", 0),
            complexity=analysis.get("complexity", "medium"),
            innovation=synthesis.get("innovation_potential", 0.0),
        )

        # Select model
        tier_config = ESCALATION_MODELS.get(level, ESCALATION_MODELS[EscalationLevel.TIER_8])
        model = tier_config["models"][0]

        # Try API call
        try:
            result = self._call_openrouter(
                model=model,
                prompt=prompt,
                max_tokens=tier_config["max_tokens"],
                temperature=tier_config["temperature"],
            )

            latency = (time.perf_counter() - start) * 1000
            self._stats["total_tokens_used"] += result.get("tokens", 0)

            return EscalationResult(
                level=level,
                triggered=True,
                model_used=model,
                enhanced_hypothesis=result.get("enhanced_hypothesis"),
                missing_considerations=result.get("missing_considerations", []),
                recommended_architecture=result.get("recommended_architecture"),
                confidence_boost=min(float(result.get("confidence_boost", 0.0)), 0.3),
                cost_tokens=result.get("tokens", 0),
                latency_ms=round(latency, 1),
                reason=f"Escalated to {model} ({tier_config['description']})",
            )

        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            logger.warning(f"Escalation failed (non-critical): {e}")
            return EscalationResult(
                level=level,
                triggered=False,
                latency_ms=round(latency, 1),
                error=str(e),
                reason=f"Escalation attempted but failed: {type(e).__name__}",
            )

    def _call_openrouter(self, model: str, prompt: str, max_tokens: int, temperature: float) -> Dict:
        """Make OpenRouter API call and parse JSON response"""
        import urllib.request
        import urllib.error

        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }).encode("utf-8")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://huggingface.co/spaces/Delentia/delentia-analyserch-intent",
            "X-Title": "Delentia Analyserch Intent",
        }

        req = urllib.request.Request(
            f"{self._base_url}/chat/completions",
            data=payload,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        text = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)

        parsed = json.loads(text)
        parsed["tokens"] = tokens
        return parsed

    def get_stats(self) -> Dict[str, Any]:
        return {**self._stats, "api_configured": bool(self._api_key)}
