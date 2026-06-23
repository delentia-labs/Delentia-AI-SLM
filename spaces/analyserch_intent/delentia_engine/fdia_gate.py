"""
FDIA Gate — Input Validation Layer
Ported from Delentia-OS/microservices/intent-loop/loop_engine.py

FDIA Formula: F = (D^I) × A
  F = Final Output Quality
  D = Data Quality
  I = Intent Clarity
  A = Architect Approval

This gate runs BEFORE any processing to ensure garbage inputs
don't consume resources. Zero external dependencies.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import re
import logging

logger = logging.getLogger(__name__)


class GIGOStatus(str, Enum):
    """GIGO validation status levels"""
    SAFE_CLEAR = "SAFE_CLEAR"
    GIGO_WARNING = "GIGO_WARNING"
    GIGO_VIOLATION = "GIGO_VIOLATION"
    SECURITY_BLOCK = "SECURITY_BLOCK"
    EMPTY = "EMPTY"


@dataclass
class GIGOResult:
    """Result of FDIA/GIGO gate validation"""
    status: GIGOStatus
    message: str
    entropy: float
    fdia_score: float          # 0.0 - 1.0: F=(D^I)×A
    data_quality: float        # D component
    intent_clarity: float      # I component
    badge_color: str
    badge_bg: str
    is_blocked: bool
    word_count: int
    unique_ratio: float
    details: Dict = field(default_factory=dict)


class FDIAGate:
    """
    FDIA Gatekeeper — Pillar 1 of Delentia OS Intent Loop

    Enforces constitutional rules before any computation.
    Uses Shannon Entropy + FDIA formula for mathematical scoring.
    
    Thresholds (optimized for maximum system performance):
      - FDIA Score < 0.25 → GIGO_VIOLATION (reject)
      - Entropy < 1.5 → GIGO_WARNING (pass with warning)
      - Entropy < 0.5 → GIGO_VIOLATION (reject)
      - Forbidden keywords → SECURITY_BLOCK (immediate reject)
      - Repetitive tokens (unique_ratio < 0.35 for len > 5 words) → GIGO_VIOLATION
    """

    # Constitutional rules
    MAX_INTENT_LENGTH = 2000
    MIN_INTENT_LENGTH = 5
    MIN_ENTROPY_HARD = 0.5      # Hard block below this
    MIN_ENTROPY_WARN = 1.5      # Warning zone
    MIN_WORD_COUNT = 3
    REPETITION_THRESHOLD = 0.35  # min unique word ratio
    FDIA_THRESHOLD = 0.25        # FDIA score minimum

    FORBIDDEN_KEYWORDS = [
        "hack", "exploit", "bypass", "jailbreak", "override",
        "sql injection", "xss", "ddos", "rootkit", "malware"
    ]

    # Thai character unicode range
    THAI_RANGE = re.compile(r'[\u0E00-\u0E7F]')

    def validate(self, text: str) -> GIGOResult:
        """
        Full FDIA validation pipeline.
        
        Returns GIGOResult with all scoring details.
        Never raises exceptions — always returns a result.
        """
        text = text or ""
        text_stripped = text.strip()

        # ── Early exits ──────────────────────────────────────────────────
        if not text_stripped:
            return GIGOResult(
                status=GIGOStatus.EMPTY,
                message="Input is empty.",
                entropy=0.0, fdia_score=0.0,
                data_quality=0.0, intent_clarity=0.0,
                badge_color="#6b7fa3", badge_bg="rgba(107,127,163,0.15)",
                is_blocked=True,
                word_count=0, unique_ratio=0.0
            )

        if len(text_stripped) < self.MIN_INTENT_LENGTH:
            return GIGOResult(
                status=GIGOStatus.GIGO_WARNING,
                message=f"Input too short (min {self.MIN_INTENT_LENGTH} chars).",
                entropy=0.0, fdia_score=0.1,
                data_quality=0.1, intent_clarity=0.1,
                badge_color="#ff8c00", badge_bg="rgba(255,140,0,0.15)",
                is_blocked=False,
                word_count=len(text_stripped.split()), unique_ratio=1.0
            )

        if len(text_stripped) > self.MAX_INTENT_LENGTH:
            text_stripped = text_stripped[:self.MAX_INTENT_LENGTH]

        # ── Forbidden keyword check ───────────────────────────────────────
        text_lower = text_stripped.lower()
        for kw in self.FORBIDDEN_KEYWORDS:
            if kw in text_lower:
                return GIGOResult(
                    status=GIGOStatus.SECURITY_BLOCK,
                    message=f"Security boundary violated: blocked token '{kw}' detected.",
                    entropy=0.0, fdia_score=0.0,
                    data_quality=0.0, intent_clarity=0.0,
                    badge_color="#ff3b3b", badge_bg="rgba(255,59,59,0.2)",
                    is_blocked=True,
                    word_count=0, unique_ratio=0.0,
                    details={"blocked_token": kw}
                )

        # ── Word/token analysis ───────────────────────────────────────────
        words = text_stripped.split()
        word_count = len(words)
        unique_words = set(w.lower() for w in words)
        unique_ratio = len(unique_words) / max(word_count, 1)

        # Repetition check (for longer inputs only)
        if word_count > 5 and unique_ratio < self.REPETITION_THRESHOLD:
            entropy = self._calculate_entropy(text_stripped)
            return GIGOResult(
                status=GIGOStatus.GIGO_VIOLATION,
                message=f"Low information density: {unique_ratio:.0%} unique tokens (min {self.REPETITION_THRESHOLD:.0%}).",
                entropy=entropy, fdia_score=0.0,
                data_quality=entropy / 5.0, intent_clarity=0.0,
                badge_color="#ff3b3b", badge_bg="rgba(255,59,59,0.15)",
                is_blocked=True,
                word_count=word_count, unique_ratio=unique_ratio
            )

        # ── Shannon Entropy ───────────────────────────────────────────────
        entropy = self._calculate_entropy(text_stripped)

        if entropy < self.MIN_ENTROPY_HARD:
            return GIGOResult(
                status=GIGOStatus.GIGO_VIOLATION,
                message=f"Entropy {entropy:.3f} below hard minimum {self.MIN_ENTROPY_HARD}.",
                entropy=entropy, fdia_score=0.0,
                data_quality=entropy / 5.0, intent_clarity=0.0,
                badge_color="#ff3b3b", badge_bg="rgba(255,59,59,0.15)",
                is_blocked=True,
                word_count=word_count, unique_ratio=unique_ratio
            )

        # ── FDIA Score: F = (D^I) × A ─────────────────────────────────────
        data_quality = self._score_data_quality(text_stripped, entropy, word_count, unique_ratio)
        intent_clarity = self._score_intent_clarity(text_stripped, word_count)
        architect_approval = 1.0  # Auto-approved (can be set to 0.0 for human gate)

        # FDIA formula
        fdia_score = (data_quality ** intent_clarity) * architect_approval
        fdia_score = round(min(max(fdia_score, 0.0), 1.0), 4)

        logger.debug(f"FDIA: D={data_quality:.3f} I={intent_clarity:.3f} F={fdia_score:.3f}")

        if fdia_score < self.FDIA_THRESHOLD:
            return GIGOResult(
                status=GIGOStatus.GIGO_VIOLATION,
                message=f"FDIA score {fdia_score:.3f} below threshold {self.FDIA_THRESHOLD}.",
                entropy=entropy, fdia_score=fdia_score,
                data_quality=data_quality, intent_clarity=intent_clarity,
                badge_color="#ff3b3b", badge_bg="rgba(255,59,59,0.15)",
                is_blocked=True,
                word_count=word_count, unique_ratio=unique_ratio
            )

        # ── Warning zone ──────────────────────────────────────────────────
        if entropy < self.MIN_ENTROPY_WARN or word_count < self.MIN_WORD_COUNT:
            return GIGOResult(
                status=GIGOStatus.GIGO_WARNING,
                message=f"Low complexity input (entropy={entropy:.2f}). Results may be limited.",
                entropy=entropy, fdia_score=fdia_score,
                data_quality=data_quality, intent_clarity=intent_clarity,
                badge_color="#ff8c00", badge_bg="rgba(255,140,0,0.15)",
                is_blocked=False,
                word_count=word_count, unique_ratio=unique_ratio
            )

        # ── SAFE ──────────────────────────────────────────────────────────
        lang_hint = self._detect_language_hint(text_stripped)
        return GIGOResult(
            status=GIGOStatus.SAFE_CLEAR,
            message=f"High information density. Safe constitutional query. ({lang_hint})",
            entropy=entropy, fdia_score=fdia_score,
            data_quality=data_quality, intent_clarity=intent_clarity,
            badge_color="#00e676", badge_bg="rgba(0,230,118,0.12)",
            is_blocked=False,
            word_count=word_count, unique_ratio=unique_ratio,
            details={"language_hint": lang_hint}
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _calculate_entropy(text: str) -> float:
        """Shannon entropy on word distribution"""
        words = text.lower().split()
        if not words:
            return 0.0
        total = len(words)
        freq: Dict[str, int] = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        entropy = 0.0
        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    @staticmethod
    def _score_data_quality(text: str, entropy: float, word_count: int, unique_ratio: float) -> float:
        """
        D (Data Quality) = composite score 0-1
        Factors: entropy, length, uniqueness
        """
        # Entropy factor (normalized to 0-1, max meaningful entropy ~5.0)
        entropy_score = min(entropy / 5.0, 1.0)
        
        # Length factor (sweet spot: 10-100 words)
        if word_count < 3:
            length_score = 0.2
        elif word_count <= 50:
            length_score = min(word_count / 50.0, 1.0)
        else:
            # Diminishing returns after 50 words
            length_score = max(1.0 - (word_count - 50) / 200.0, 0.7)
        
        # Uniqueness factor
        uniqueness_score = unique_ratio
        
        # Weighted composite
        d = (entropy_score * 0.5 + length_score * 0.3 + uniqueness_score * 0.2)
        return round(min(d, 1.0), 4)

    @staticmethod
    def _score_intent_clarity(text: str, word_count: int) -> float:
        """
        I (Intent Clarity) = 0-1 based on structural signals
        Higher = clearer intent structure
        """
        text_lower = text.lower()
        score = 0.5  # Base score

        # Action verbs boost
        action_verbs = [
            "build", "create", "implement", "deploy", "analyze", "design",
            "optimize", "refactor", "test", "debug", "integrate", "develop",
            "สร้าง", "พัฒนา", "วิเคราะห์", "ออกแบบ", "ปรับปรุง", "ทดสอบ"
        ]
        if any(v in text_lower for v in action_verbs):
            score += 0.15

        # Technical terms boost
        tech_terms = [
            "api", "database", "cache", "microservice", "blockchain", "ai",
            "model", "pipeline", "architecture", "system", "service", "endpoint",
            "ระบบ", "ฐานข้อมูล", "โมเดล", "สถาปัตยกรรม"
        ]
        if any(t in text_lower for t in tech_terms):
            score += 0.15

        # Question or goal structure
        goal_words = ["to", "for", "in order", "so that", "เพื่อ", "สำหรับ"]
        if any(g in text_lower for g in goal_words):
            score += 0.1

        # Constraint specification
        constraint_words = ["with", "without", "max", "min", "budget", "limit",
                            "ภายใน", "โดยไม่", "ต้องการ"]
        if any(c in text_lower for c in constraint_words):
            score += 0.1

        return round(min(score, 1.0), 4)

    def _detect_language_hint(self, text: str) -> str:
        """Quick language detection for display"""
        thai_chars = len(self.THAI_RANGE.findall(text))
        total_alpha = len(re.findall(r'[a-zA-Z\u0E00-\u0E7F]', text))
        if total_alpha == 0:
            return "lang:mixed"
        ratio = thai_chars / total_alpha
        if ratio >= 0.5:
            return "lang:th 🇹🇭"
        elif ratio >= 0.1:
            return "lang:th+en 🌏"
        return "lang:en 🇬🇧"
