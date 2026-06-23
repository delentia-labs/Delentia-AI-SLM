"""
Memory Layer — Warm Recall Cache
Ported from Delentia-OS/microservices/intent-loop/loop_engine.py (MemoryLayer)

Philosophy:
  Cold Start: First time = full computation
  Warm Recall: Repeat query = < 50ms from cache
  Evolution: System gets smarter over time

Storage:
  Primary: In-memory dict (process lifetime)
  Secondary: Supabase (async, optional)

Key design: SHA-256 hash of normalized query = cache key
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib
import json
import math
import threading
import logging
import os

logger = logging.getLogger(__name__)


@dataclass
class MemoryHit:
    """Cached wisdom from previous computation"""
    intent_hash: str
    original_query: str
    result: Dict[str, Any]
    confidence: float           # 0.0 - 1.0
    created_at: datetime
    last_accessed: datetime
    access_count: int
    processing_time_ms: float   # Original compute time (for ROI tracking)
    engine_version: str = "native_v1"

    @property
    def age_seconds(self) -> float:
        return (datetime.now() - self.created_at).total_seconds()

    @property
    def is_fresh(self) -> bool:
        """Cache entry is 'fresh' if < 1 hour old"""
        return self.age_seconds < 3600

    @property
    def roi(self) -> float:
        """Return on investment: time saved by cache hit"""
        return self.processing_time_ms * self.access_count


class MemoryLayer:
    """
    In-memory intent cache with optional Supabase persistence.
    
    Warm Recall Strategy:
      1. Exact hash match (< 1ms)
      2. Normalized text match (< 5ms)
      3. Fuzzy word overlap match (< 20ms, threshold 0.80)
      
    Storage tiers:
      - L1: In-process dict (instant)
      - L2: Supabase (async background sync)
    """

    # Cache configuration (tuned for HF Space free tier)
    MAX_CACHE_SIZE = 500         # Max entries before LRU eviction
    MIN_CONFIDENCE_HIT = 0.70   # Min confidence for fuzzy cache hit (native threshold)
    FUZZY_MATCH_THRESHOLD = 0.80 # Jaccard similarity threshold

    def __init__(self):
        self._cache: Dict[str, MemoryHit] = {}
        self._lock = threading.Lock()
        self._stats = {
            "total_recall_attempts": 0,
            "exact_hits": 0,
            "fuzzy_hits": 0,
            "misses": 0,
            "stores": 0,
            "evictions": 0,
        }
        logger.info("MemoryLayer initialized (in-process + Supabase sync)")

    # ── Public API ───────────────────────────────────────────────────────────

    def recall(self, query: str) -> Optional[MemoryHit]:
        """
        Attempt to retrieve cached result for query.
        
        Returns MemoryHit if found with sufficient confidence, else None.
        Warm recall target: < 50ms
        """
        self._stats["total_recall_attempts"] += 1

        normalized = self._normalize(query)
        hash_key = self._hash(normalized)

        with self._lock:
            # L1: Exact hash match
            if hash_key in self._cache:
                hit = self._cache[hash_key]
                # Exact matches are always safe to recall if fresh (regardless of confidence)
                if hit.is_fresh:
                    hit.access_count += 1
                    hit.last_accessed = datetime.now()
                    self._stats["exact_hits"] += 1
                    logger.info(f"⚡ Cache HIT (exact): {query[:40]}... (×{hit.access_count})")
                    return hit

            # L2: Fuzzy word overlap match
            fuzzy_hit = self._fuzzy_match(normalized)
            if fuzzy_hit:
                fuzzy_hit.access_count += 1
                fuzzy_hit.last_accessed = datetime.now()
                self._stats["fuzzy_hits"] += 1
                logger.info(f"⚡ Cache HIT (fuzzy): {query[:40]}...")
                return fuzzy_hit

        self._stats["misses"] += 1
        logger.debug(f"Cache MISS: {query[:40]}...")
        return None

    def store(
        self,
        query: str,
        result: Dict[str, Any],
        confidence: float,
        processing_time_ms: float = 0.0
    ) -> str:
        """
        Store computation result in cache.
        
        Returns the hash key used.
        Triggers async Supabase sync if configured.
        """
        normalized = self._normalize(query)
        hash_key = self._hash(normalized)

        hit = MemoryHit(
            intent_hash=hash_key,
            original_query=query,
            result=result,
            confidence=confidence,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=0,
            processing_time_ms=processing_time_ms,
        )

        with self._lock:
            # Evict LRU if at capacity
            if len(self._cache) >= self.MAX_CACHE_SIZE:
                self._evict_lru()

            self._cache[hash_key] = hit

        self._stats["stores"] += 1
        logger.info(
            f"Memory stored: {hash_key[:12]}... "
            f"(conf={confidence:.2f}, t={processing_time_ms:.1f}ms)"
        )

        # Async sync to Supabase
        self._async_sync_to_supabase(hit)

        return hash_key

    def get_stats(self) -> Dict[str, Any]:
        """Return cache statistics"""
        total = self._stats["total_recall_attempts"]
        hits = self._stats["exact_hits"] + self._stats["fuzzy_hits"]
        hit_rate = hits / total if total > 0 else 0.0

        total_roi = sum(h.roi for h in self._cache.values())
        avg_confidence = (
            sum(h.confidence for h in self._cache.values()) / len(self._cache)
            if self._cache else 0.0
        )

        return {
            "cache_size": len(self._cache),
            "max_size": self.MAX_CACHE_SIZE,
            "hit_rate": f"{hit_rate:.1%}",
            "exact_hits": self._stats["exact_hits"],
            "fuzzy_hits": self._stats["fuzzy_hits"],
            "misses": self._stats["misses"],
            "stores": self._stats["stores"],
            "evictions": self._stats["evictions"],
            "total_roi_ms": round(total_roi, 1),
            "avg_confidence": round(avg_confidence, 3),
        }

    def clear(self) -> int:
        """Clear all cache entries. Returns count cleared."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
        logger.info(f"Cache cleared ({count} entries)")
        return count

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize query for consistent hashing"""
        return " ".join(text.lower().strip().split())

    @staticmethod
    def _hash(text: str) -> str:
        """SHA-256 hash of normalized text"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _fuzzy_match(self, normalized_query: str) -> Optional[MemoryHit]:
        """
        Jaccard similarity match against all cached queries.
        Returns best match above threshold, or None.
        """
        query_words = set(normalized_query.lower().split())
        if not query_words:
            return None

        best_hit: Optional[MemoryHit] = None
        best_score = 0.0

        for hit in self._cache.values():
            if not hit.is_fresh:
                continue
            cached_words = set(hit.original_query.lower().split())
            if not cached_words:
                continue

            # Jaccard similarity
            intersection = query_words & cached_words
            union = query_words | cached_words
            similarity = len(intersection) / len(union) if union else 0.0

            if (similarity >= self.FUZZY_MATCH_THRESHOLD
                    and similarity > best_score
                    and hit.confidence >= self.MIN_CONFIDENCE_HIT):
                best_score = similarity
                best_hit = hit

        return best_hit

    def _evict_lru(self) -> None:
        """Remove least recently used entry"""
        if not self._cache:
            return
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        del self._cache[lru_key]
        self._stats["evictions"] += 1
        logger.debug(f"LRU eviction: {lru_key[:12]}...")

    def _async_sync_to_supabase(self, hit: MemoryHit) -> None:
        """
        Async background sync to Supabase.
        Fire-and-forget — never blocks main pipeline.
        """
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("RCT_CORE_BRAIN_KEY") or os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            return  # Supabase not configured

        def _sync():
            try:
                import requests
                payload = {
                    "intent_hash": hit.intent_hash,
                    "original_query": hit.original_query[:500],
                    "confidence": hit.confidence,
                    "processing_time_ms": hit.processing_time_ms,
                    "engine_version": hit.engine_version,
                    "created_at": hit.created_at.isoformat(),
                    "result_summary": {
                        k: v for k, v in hit.result.items()
                        if k in ("confidence", "mode", "keywords_count",
                                 "mirror_converged", "escalation_level", "query_type")
                    }
                }
                headers = {
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                }
                endpoint = f"{supabase_url.rstrip('/')}/rest/v1/analyserch_memory"
                requests.post(endpoint, json=payload, headers=headers, timeout=5)
            except Exception as e:
                logger.debug(f"Supabase sync failed (non-critical): {e}")

        thread = threading.Thread(target=_sync, daemon=True)
        thread.start()
