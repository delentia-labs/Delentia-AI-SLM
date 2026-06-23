"""
Analysearch Core Engine
Ported from Delentia-OS/microservices/analysearch-intent/app/core/analysearch_engine.py

This is the PRIMARY intelligence engine for Analyserch Intent.
No external LLMs required — runs entirely on Delentia OS algorithms.

Algorithms:
  - ALGO-41: KeywordCrystallizer (golden keyword extraction)
  - ALGO-26: Intent Conservation check
  - ALGO-05: Cross-Disciplinary Synthesis
  - Mirror Mode: PROPOSE → COUNTER → REFINE loop
  - Language detection (Thai/ASEAN routing hint)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
import math
import re
import secrets
import logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

class AnalysearchMode(str, Enum):
    QUICK = "quick"          # Fast, keyword-only
    STANDARD = "standard"   # Keywords + synthesis
    DEEP = "deep"            # Full pipeline + Mirror Mode
    MIRROR = "mirror"        # Explicit Mirror Mode


class MirrorPhase(str, Enum):
    PROPOSE = "propose"
    COUNTER = "counter"
    REFINE = "refine"
    CONVERGED = "converged"


# ─────────────────────────────────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MirrorState:
    session_id: str
    query: str
    phase: MirrorPhase = MirrorPhase.PROPOSE
    iterations: int = 0
    max_iterations: int = 5
    proposals: List[Dict] = field(default_factory=list)
    counters: List[Dict] = field(default_factory=list)
    refinements: List[Dict] = field(default_factory=list)
    convergence_score: float = 0.0
    converged: bool = False


@dataclass
class DisciplineInsight:
    discipline: str
    relevance_score: float
    key_concepts: List[str]
    connections: List[str]
    evidence_strength: float


@dataclass
class KeywordResult:
    keyword: str
    score: float
    entropy: float
    frequency: int
    domain: Optional[str]
    category: str
    definition: str
    implications: List[str]


@dataclass
class AnalysearchResult:
    """Full result from Analysearch Native Engine"""
    query: str
    mode: str
    keywords: List[KeywordResult]
    analysis: Dict[str, Any]
    synthesis: Dict[str, Any]
    mirror_state: Optional[MirrorState]
    research_sources: List[Dict]
    intent_preserved: bool
    confidence: float           # 0.0 - 1.0 (drives escalation decision)
    processing_time_ms: float
    routing_hint: Dict[str, Any]
    engine: str = "delentia-native-v1"


# ─────────────────────────────────────────────────────────────────────────────
# ALGO-41: Keyword Crystallizer
# ─────────────────────────────────────────────────────────────────────────────

# Rich concept knowledge base (extended from original)
CONCEPT_KNOWLEDGE_BASE = {
    "sovereignty": {
        "definition": "อำนาจการควบคุมและครอบครองข้อมูลและโครงสร้างพื้นฐานอย่างสมบูรณ์แบบโดยไม่ต้องพึ่งพาระบบคลาวด์ภายนอก",
        "category": "Conceptual",
        "domain": "security",
        "implications": [
            "Self-hosted database cluster (PostgreSQL, Redis บนเซิร์ฟเวอร์ส่วนตัว)",
            "Local SLM inference (no external API calls)",
            "PDPA/GDPR Level-5 data protection",
        ],
    },
    "realtime": {
        "definition": "ระบบการสื่อสารแบบสองทิศทางแบบทันทีทันใด (Instant bidirectional communication)",
        "category": "Technical",
        "domain": "engineering",
        "implications": [
            "WebSocket / Server-Sent Events (SSE) protocol",
            "Redis Pub/Sub for packet distribution",
            "Edge node processing for minimal latency",
        ],
    },
    "blockchain": {
        "definition": "สถาปัตยกรรมการจัดเก็บข้อมูลแบบกระจายศูนย์ที่ป้องกันการย้อนกลับ",
        "category": "Domain",
        "domain": "engineering",
        "implications": [
            "Web3 SDK / Smart Contract connectors",
            "Multi-signature transaction signing",
            "Decentralized finance integration",
        ],
    },
    "payment": {
        "definition": "กลไกหรือกระบวนการโอนย้ายมูลค่าทางการเงินแบบอิเล็กทรอนิกส์",
        "category": "Business",
        "domain": "economics",
        "implications": [
            "PCI-DSS compliance requirement",
            "Cryptographic digital signatures",
            "Real-time budget simulation",
        ],
    },
    "cache": {
        "definition": "การจัดเก็บข้อมูลชั่วคราวบนหน่วยความจำความเร็วสูง เพื่อหลีกเลี่ยงการประมวลผลซ้ำ",
        "category": "Technical",
        "domain": "engineering",
        "implications": [
            "In-memory key store (Redis, local dict)",
            "Warm Recall < 50ms target",
            "TOON token compression for LLM context",
        ],
    },
    "ai": {
        "definition": "ระบบปัญญาประดิษฐ์ที่สามารถเรียนรู้และปรับตัวได้จากข้อมูล",
        "category": "Technical",
        "domain": "computer_science",
        "implications": [
            "ML model training and inference pipeline",
            "Constitutional AI safety constraints",
            "Federated learning for data sovereignty",
        ],
    },
    "api": {
        "definition": "Application Programming Interface — ชั้นการสื่อสารระหว่างระบบซอฟต์แวร์",
        "category": "Technical",
        "domain": "computer_science",
        "implications": [
            "RESTful or gRPC endpoint design",
            "API gateway with rate limiting",
            "OpenAPI/Swagger documentation",
        ],
    },
    "microservice": {
        "definition": "สถาปัตยกรรมซอฟต์แวร์ที่แบ่งระบบออกเป็นบริการเล็กๆ ที่ทำงานอิสระ",
        "category": "Technical",
        "domain": "engineering",
        "implications": [
            "Docker containerization per service",
            "Service mesh (Istio/Linkerd) for traffic",
            "Event-driven communication (Kafka/RabbitMQ)",
        ],
    },
    "security": {
        "definition": "ชุดมาตรการปกป้องระบบและข้อมูลจากการเข้าถึงที่ไม่ได้รับอนุญาต",
        "category": "Conceptual",
        "domain": "security",
        "implications": [
            "Zero-Trust network architecture",
            "Cryptographic key management (HSM)",
            "Real-time threat detection (SIEM)",
        ],
    },
    "database": {
        "definition": "ระบบจัดเก็บข้อมูลที่มีโครงสร้างสำหรับการเข้าถึงที่รวดเร็วและเชื่อถือได้",
        "category": "Technical",
        "domain": "computer_science",
        "implications": [
            "ACID transaction guarantees",
            "Vector database for semantic search",
            "Replication and failover strategy",
        ],
    },
    "model": {
        "definition": "โมเดล ML/AI ที่ผ่านการฝึกสอนเพื่อทำงานเฉพาะทาง",
        "category": "Technical",
        "domain": "computer_science",
        "implications": [
            "LoRA fine-tuning for domain adaptation",
            "GGUF quantization for local inference",
            "Model versioning and A/B testing",
        ],
    },
    "sovereignty": {  # Duplicate key, will use last one (already handled)
        "definition": "อำนาจสูงสุดในการควบคุมระบบและข้อมูลทั้งหมดโดยไม่พึ่งพาภายนอก",
        "category": "Conceptual",
        "domain": "security",
        "implications": [
            "Air-gapped deployment option",
            "Local LLM (Ollama/llama.cpp) inference",
            "PDPA/GDPR Level-5 compliance",
        ],
    },
    "pipeline": {
        "definition": "ลำดับขั้นตอนการประมวลผลข้อมูลที่เชื่อมต่อกันเป็นห่วงโซ่",
        "category": "Technical",
        "domain": "engineering",
        "implications": [
            "Apache Airflow / Prefect orchestration",
            "Stream processing (Apache Kafka)",
            "CI/CD automation with GitHub Actions",
        ],
    },
}

# Domain taxonomy for cross-disciplinary synthesis
DISCIPLINE_KEYWORDS: Dict[str, List[str]] = {
    "computer_science": ["algorithm", "data", "code", "software", "network", "compute", "ai", "api", "cache", "database", "model", "pipeline", "microservice"],
    "engineering": ["design", "system", "build", "structure", "optimize", "infrastructure", "realtime", "blockchain", "cache"],
    "security": ["protect", "secure", "defend", "guard", "prevent", "sovereignty", "zero-trust", "encryption", "authentication"],
    "economics": ["market", "cost", "price", "demand", "supply", "investment", "roi", "budget", "payment", "revenue"],
    "mathematics": ["equation", "formula", "proof", "theorem", "statistics", "probability", "entropy", "algorithm"],
    "psychology": ["behavior", "cognitive", "perception", "emotion", "motivation", "user", "ux", "intent"],
    "biology": ["bio", "cell", "organism", "evolution", "gene", "ecology"],
    "physics": ["force", "energy", "quantum", "wave", "particle", "thermal"],
}

DISCIPLINE_CONNECTIONS: Dict[str, List[str]] = {
    "computer_science": ["mathematics", "engineering", "psychology"],
    "engineering": ["physics", "computer_science", "mathematics"],
    "security": ["computer_science", "mathematics", "psychology"],
    "economics": ["mathematics", "psychology", "computer_science"],
    "mathematics": ["physics", "computer_science", "economics"],
    "psychology": ["computer_science", "biology", "economics"],
    "biology": ["chemistry", "physics"],
    "physics": ["engineering", "mathematics"],
}


class KeywordCrystallizer:
    """
    ALGO-41: Golden Keyword Extraction
    
    Extracts high-value keywords using entropy + TF scoring.
    Enriches with knowledge base definitions when available.
    """

    def __init__(self, min_entropy: float = 0.5):
        self.min_entropy = min_entropy

    def extract(self, text: str, top_k: int = 10) -> List[KeywordResult]:
        """Extract and score golden keywords from text"""
        if not text:
            return []

        # Tokenize (handle Thai + Latin)
        words = re.findall(r'[a-zA-Z]{3,}|[\u0E00-\u0E7F]+', text)
        if not words:
            return []

        total = len(words)
        freq: Dict[str, int] = {}
        for w in words:
            key = w.lower()
            freq[key] = freq.get(key, 0) + 1

        results: List[KeywordResult] = []
        seen = set()

        for word, count in freq.items():
            if word in seen:
                continue
            seen.add(word)

            if len(word) < 3:
                continue

            entropy = self._char_entropy(word)
            if entropy < self.min_entropy:
                continue

            # TF score
            tf = count / total

            # Knowledge base lookup
            kb = self._lookup_kb(word)
            domain = kb.get("domain") if kb else None
            category = kb.get("category", "General") if kb else "General"
            definition = kb.get("definition", f"Term '{word}' identified in query context.") if kb else f"Technical concept '{word}' detected in intent analysis."
            implications = kb.get("implications", [
                f"Analyze '{word}' requirements in system context",
                f"Evaluate '{word}' integration complexity",
                f"Define '{word}' success metrics",
            ]) if kb else [
                f"Analyze '{word}' requirements in system context",
                f"Evaluate '{word}' integration complexity",
            ]

            # Score calculation
            boost = 1.5 if domain else 1.0
            length_bonus = min(len(word) / 12, 1.0)
            kb_boost = 1.3 if kb else 1.0
            score = (tf * 0.25 + entropy / 5.0 * 0.45 + length_bonus * 0.30) * boost * kb_boost

            results.append(KeywordResult(
                keyword=word,
                score=round(score, 4),
                entropy=round(entropy, 3),
                frequency=count,
                domain=domain,
                category=category,
                definition=definition,
                implications=implications,
            ))

        # Sort by score
        results.sort(key=lambda k: k.score, reverse=True)
        return results[:top_k]

    def _lookup_kb(self, word: str) -> Optional[Dict]:
        """Look up word in concept knowledge base"""
        return CONCEPT_KNOWLEDGE_BASE.get(word.lower())

    @staticmethod
    def _char_entropy(word: str) -> float:
        """Character-level Shannon entropy"""
        if not word:
            return 0.0
        freq: Dict[str, int] = {}
        for c in word.lower():
            freq[c] = freq.get(c, 0) + 1
        n = len(word)
        entropy = 0.0
        for count in freq.values():
            p = count / n
            if p > 0:
                entropy -= p * math.log2(p)
        return round(entropy, 4)


# ─────────────────────────────────────────────────────────────────────────────
# Cross-Disciplinary Synthesizer
# ─────────────────────────────────────────────────────────────────────────────

class CrossDisciplinarySynthesizer:
    """
    Finds unexpected connections between domains.
    Higher intersection count → higher innovation potential.
    """

    def synthesize(self, keywords: List[KeywordResult], context: str = "") -> Dict[str, Any]:
        all_text = " ".join(k.keyword for k in keywords) + " " + context.lower()

        disciplines = self._detect_disciplines(keywords, all_text)
        intersections = self._find_intersections(disciplines)
        insights = self._generate_insights(disciplines, intersections)
        innovation = self._calc_innovation(disciplines, intersections)

        return {
            "disciplines_detected": len(disciplines),
            "disciplines": [
                {
                    "name": d.discipline,
                    "relevance": d.relevance_score,
                    "key_concepts": d.key_concepts,
                    "connections": d.connections,
                    "evidence_strength": d.evidence_strength,
                }
                for d in disciplines
            ],
            "intersections": intersections,
            "insights": insights,
            "innovation_potential": innovation,
        }

    def _detect_disciplines(self, keywords: List[KeywordResult], all_text: str) -> List[DisciplineInsight]:
        scores: Dict[str, float] = {}
        concepts: Dict[str, List[str]] = {}

        for disc, terms in DISCIPLINE_KEYWORDS.items():
            score = 0.0
            found = []
            for term in terms:
                if term.lower() in all_text:
                    score += 1.0
                    found.append(term)
            if score > 0:
                scores[disc] = score / len(terms)
                concepts[disc] = found

        insights = []
        for disc, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]:
            conn = DISCIPLINE_CONNECTIONS.get(disc, [])
            rel_conn = [c for c in conn if c in scores]
            insights.append(DisciplineInsight(
                discipline=disc,
                relevance_score=round(score, 3),
                key_concepts=concepts.get(disc, []),
                connections=rel_conn,
                evidence_strength=min(score * 2, 1.0),
            ))
        return insights

    def _find_intersections(self, disciplines: List[DisciplineInsight]) -> List[Dict]:
        intersections = []
        for i, d1 in enumerate(disciplines):
            for j, d2 in enumerate(disciplines):
                if i >= j:
                    continue
                common = set(d1.connections) & set(d2.connections)
                direct = d2.discipline in d1.connections or d1.discipline in d2.connections
                if direct or common:
                    intersections.append({
                        "disciplines": [d1.discipline, d2.discipline],
                        "connection_type": "direct" if direct else "indirect",
                        "shared_domains": list(common),
                        "potential_score": round((d1.relevance_score + d2.relevance_score) / 2, 3),
                    })
        return intersections

    def _generate_insights(self, disciplines: List[DisciplineInsight], intersections: List[Dict]) -> List[str]:
        insights = []
        for ix in intersections:
            d1, d2 = ix["disciplines"]
            insights.append(
                f"{d1} × {d2} intersection yields novel approach "
                f"({ix['connection_type']} link, potential={ix['potential_score']:.0%})"
            )
        if len(disciplines) >= 3:
            names = [d.discipline for d in disciplines[:3]]
            insights.append(f"Multi-disciplinary synthesis: {' + '.join(names)}")
        return insights

    def _calc_innovation(self, disciplines: List[DisciplineInsight], intersections: List[Dict]) -> float:
        if not disciplines:
            return 0.0
        d_factor = min(len(disciplines) / 3, 1.0) * 0.4
        i_factor = min(len(intersections) / 3, 1.0) * 0.3
        avg_ev = sum(d.evidence_strength for d in disciplines) / len(disciplines)
        return round(d_factor + i_factor + avg_ev * 0.3, 3)


# ─────────────────────────────────────────────────────────────────────────────
# Mirror Mode Engine
# ─────────────────────────────────────────────────────────────────────────────

class MirrorModeEngine:
    """
    PROPOSE → COUNTER → REFINE adversarial loop.
    Convergence threshold: 0.82 (optimized for speed vs depth tradeoff)
    """

    def __init__(self, max_iterations: int = 5, convergence_threshold: float = 0.82):
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold

    def run(self, query: str, analysis: Dict, keywords: List[KeywordResult],
            synthesis: Dict, max_iter: int = 3) -> MirrorState:
        """Run full Mirror Mode loop"""
        self.max_iterations = max_iter
        state = MirrorState(
            session_id=secrets.token_hex(6),
            query=query,
            max_iterations=max_iter,
        )

        while not state.converged and state.iterations < state.max_iterations:
            proposal = self._propose(state, analysis, keywords)
            counter = self._counter(state, proposal, synthesis)
            self._refine(state, proposal, counter)

        return state

    def _propose(self, state: MirrorState, analysis: Dict, keywords: List[KeywordResult]) -> Dict:
        top_kw = [k.keyword for k in keywords[:5]]
        query_type = analysis.get("query_type", "exploration")
        complexity = analysis.get("complexity", "medium")

        proposal = {
            "phase": "propose",
            "iteration": state.iterations,
            "hypothesis": (
                f"For query targeting [{', '.join(top_kw)}]: "
                f"Propose a {complexity}-complexity {query_type} strategy "
                f"using distributed microservice architecture."
            ),
            "evidence": [{"keyword": k.keyword, "score": k.score, "domain": k.domain} for k in keywords[:5]],
            "confidence": min(0.45 + len(keywords) * 0.04, 0.78),
            "assumptions": [f"'{k.keyword}' is primary driver (entropy={k.entropy})" for k in keywords[:3]],
            "timestamp": datetime.now().isoformat(),
        }
        state.proposals.append(proposal)
        state.phase = MirrorPhase.COUNTER
        return proposal

    def _counter(self, state: MirrorState, proposal: Dict, synthesis: Dict) -> Dict:
        weaknesses = []
        alternatives = []

        disciplines = synthesis.get("disciplines", [])
        if len(disciplines) < 2:
            weaknesses.append("Single-discipline view: cross-domain insights missing")

        evidence = proposal.get("evidence", [])
        weak = [e for e in evidence if e.get("score", 0) < 0.08]
        if weak:
            weaknesses.append(f"{len(weak)} keyword(s) have weak evidence scores")

        conf = proposal.get("confidence", 0)
        if conf < 0.60:
            weaknesses.append(f"Confidence {conf:.0%} below target threshold")

        for ix in synthesis.get("intersections", []):
            alternatives.append(
                f"Consider {ix['disciplines'][0]}↔{ix['disciplines'][1]} "
                f"cross-domain approach (potential={ix['potential_score']:.0%})"
            )

        counter = {
            "phase": "counter",
            "iteration": state.iterations,
            "weaknesses_found": len(weaknesses),
            "weaknesses": weaknesses,
            "alternative_perspectives": alternatives,
            "challenge_strength": min(len(weaknesses) * 0.2 + len(alternatives) * 0.15, 1.0),
            "timestamp": datetime.now().isoformat(),
        }
        state.counters.append(counter)
        state.phase = MirrorPhase.REFINE
        return counter

    def _refine(self, state: MirrorState, proposal: Dict, counter: Dict) -> Dict:
        base_conf = proposal.get("confidence", 0.5)
        refined_conf = min(base_conf + (1 - base_conf) * 0.32, 0.96)

        refined = {
            "phase": "refine",
            "iteration": state.iterations,
            "original_confidence": base_conf,
            "refined_confidence": refined_conf,
            "improvements": [f"✓ Addressed: {w}" for w in counter.get("weaknesses", [])],
            "alternatives_incorporated": counter.get("alternative_perspectives", []),
            "remaining_gaps": (
                [f"Confidence {refined_conf:.0%} < target {self.convergence_threshold:.0%}"]
                if refined_conf < self.convergence_threshold else []
            ),
            "timestamp": datetime.now().isoformat(),
        }

        state.refinements.append(refined)
        state.iterations += 1
        state.convergence_score = refined_conf

        if refined_conf >= self.convergence_threshold or state.iterations >= state.max_iterations:
            state.phase = MirrorPhase.CONVERGED
            state.converged = True
        else:
            state.phase = MirrorPhase.PROPOSE

        return refined


# ─────────────────────────────────────────────────────────────────────────────
# Language Detector (lightweight, no dependencies)
# ─────────────────────────────────────────────────────────────────────────────

class LanguageDetector:
    """
    Lightweight language detector for Thai/ASEAN routing.
    Pure Python, no external dependencies.
    """

    THAI_RANGE = re.compile(r'[\u0E00-\u0E7F]')
    ASEAN_RANGES = {
        "vi": re.compile(r'[\u1E00-\u1EFF\u00C0-\u024F]'),  # Vietnamese diacritics
        "ja": re.compile(r'[\u3040-\u30FF\u4E00-\u9FFF]'),  # Japanese
        "zh": re.compile(r'[\u4E00-\u9FFF]'),               # Chinese
        "ko": re.compile(r'[\uAC00-\uD7AF]'),               # Korean
    }

    def detect(self, text: str) -> Dict[str, Any]:
        """Returns {code, name, confidence, script, routing_model}"""
        if not text:
            return {"code": "en", "name": "English", "confidence": 0.5, "script": "Latin", "routing_model": None}

        total_alpha = len(re.findall(r'[a-zA-Z\u0E00-\u0E7F\u3040-\uD7AF\u4E00-\u9FFF]', text))
        if total_alpha == 0:
            return {"code": "en", "name": "English", "confidence": 0.5, "script": "Latin", "routing_model": None}

        thai_chars = len(self.THAI_RANGE.findall(text))
        thai_ratio = thai_chars / total_alpha

        if thai_ratio >= 0.3:
            return {
                "code": "th", "name": "Thai", "confidence": round(thai_ratio, 3),
                "script": "Thai", "routing_model": "typhoon-v2",
            }

        for lang, pattern in self.ASEAN_RANGES.items():
            found = len(pattern.findall(text))
            if found > 0 and found / total_alpha >= 0.3:
                models = {"vi": "seallm-v3", "ja": "qwen2-72b", "zh": "qwen2-72b", "ko": "qwen2-72b"}
                names = {"vi": "Vietnamese", "ja": "Japanese", "zh": "Chinese", "ko": "Korean"}
                return {
                    "code": lang, "name": names[lang],
                    "confidence": round(found / total_alpha, 3),
                    "script": lang.upper(), "routing_model": models[lang],
                }

        if thai_ratio >= 0.1:
            return {
                "code": "th+en", "name": "Thai+English", "confidence": round(thai_ratio, 3),
                "script": "Mixed", "routing_model": "typhoon-v2",
            }

        return {"code": "en", "name": "English", "confidence": round(1.0 - thai_ratio, 3), "script": "Latin", "routing_model": None}


# ─────────────────────────────────────────────────────────────────────────────
# Main Analysearch Engine
# ─────────────────────────────────────────────────────────────────────────────

class AnalysearchCoreEngine:
    """
    Primary Delentia OS Native Engine for Analyserch Intent.
    
    No external LLMs required.
    Confidence score drives escalation decision in EscalationRouter.
    """

    def __init__(self):
        self.crystallizer = KeywordCrystallizer()
        self.synthesizer = CrossDisciplinarySynthesizer()
        self.mirror = MirrorModeEngine()
        self.lang_detector = LanguageDetector()
        self._query_count = 0

    def analyze(
        self,
        query: str,
        mode: AnalysearchMode = AnalysearchMode.STANDARD,
        context: str = "",
        max_mirror_iterations: int = 3,
    ) -> AnalysearchResult:
        """
        Main analysis entry point.
        
        Returns AnalysearchResult.confidence which drives escalation:
          >= 0.70 → use native result only
          0.50-0.69 → native result + escalation note
          < 0.50 → trigger EscalationRouter
        """
        start = datetime.now()
        self._query_count += 1

        # Step 1: Extract keywords (ALGO-41)
        full_text = f"{query} {context}"
        keywords = self.crystallizer.extract(full_text, top_k=10)

        # Step 2: Cross-disciplinary synthesis (ALGO-05)
        synthesis = self.synthesizer.synthesize(keywords, full_text)

        # Step 3: Build structured analysis
        analysis = self._build_analysis(query, keywords, synthesis)

        # Step 4: Mirror Mode (deep/mirror modes only)
        mirror_state = None
        if mode in (AnalysearchMode.DEEP, AnalysearchMode.MIRROR):
            mirror_state = self.mirror.run(query, analysis, keywords, synthesis, max_mirror_iterations)

        # Step 5: Intent conservation check (ALGO-26)
        intent_preserved = self._check_intent_conservation(query, analysis, keywords)

        # Step 6: Confidence score (drives escalation)
        confidence = self._calculate_confidence(keywords, synthesis, mirror_state, mode)

        # Step 7: Language detection + routing hint
        lang = self.lang_detector.detect(query)
        routing_hint = self._build_routing_hint(lang, analysis)

        elapsed = (datetime.now() - start).total_seconds() * 1000

        return AnalysearchResult(
            query=query,
            mode=mode.value,
            keywords=keywords,
            analysis=analysis,
            synthesis=synthesis,
            mirror_state=mirror_state,
            research_sources=self._find_sources(keywords),
            intent_preserved=intent_preserved,
            confidence=confidence,
            processing_time_ms=round(elapsed, 2),
            routing_hint=routing_hint,
        )

    # ── Private methods ─────────────────────────────────────────────────────

    def _build_analysis(self, query: str, keywords: List[KeywordResult], synthesis: Dict) -> Dict:
        query_type = self._classify_query(query)
        complexity = self._estimate_complexity(keywords, synthesis)

        return {
            "query_type": query_type,
            "complexity": complexity,
            "keyword_summary": {
                "total": len(keywords),
                "top_domain": keywords[0].domain or "general" if keywords else "unknown",
                "avg_score": round(sum(k.score for k in keywords) / max(len(keywords), 1), 4),
            },
            "disciplines_involved": synthesis.get("disciplines_detected", 0),
            "innovation_potential": synthesis.get("innovation_potential", 0.0),
            "recommended_depth": "deep" if synthesis.get("disciplines_detected", 0) >= 2 else "standard",
        }

    def _classify_query(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["how", "วิธี", "ทำอย่างไร", "อย่างไร"]):
            return "how_to"
        if any(w in q for w in ["why", "ทำไม", "เพราะอะไร"]):
            return "explanation"
        if any(w in q for w in ["compare", "เปรียบเทียบ", "vs", "versus"]):
            return "comparison"
        if any(w in q for w in ["create", "build", "สร้าง", "พัฒนา", "implement", "design"]):
            return "creation"
        if any(w in q for w in ["analyze", "วิเคราะห์", "evaluate", "assess"]):
            return "analysis"
        return "exploration"

    def _estimate_complexity(self, keywords: List[KeywordResult], synthesis: Dict) -> str:
        disciplines = synthesis.get("disciplines_detected", 0)
        kw_count = len(keywords)
        if disciplines >= 3 or kw_count >= 8:
            return "high"
        elif disciplines >= 2 or kw_count >= 4:
            return "medium"
        return "low"

    def _check_intent_conservation(self, query: str, analysis: Dict, keywords: List[KeywordResult]) -> bool:
        """ALGO-26: Verify original intent is preserved"""
        query_words = {w.lower() for w in re.findall(r'[a-zA-Z\u0E00-\u0E7F]+', query) if len(w) > 2}
        if not query_words:
            return True
        kw_words = {k.keyword.lower() for k in keywords}
        analysis_str = str(analysis).lower()
        combined = kw_words | {w for w in analysis_str.split() if len(w) > 2}
        preserved = sum(1 for w in query_words if w in combined)
        return (preserved / len(query_words)) >= 0.25

    def _calculate_confidence(
        self,
        keywords: List[KeywordResult],
        synthesis: Dict,
        mirror_state: Optional[MirrorState],
        mode: AnalysearchMode,
    ) -> float:
        """
        Confidence score (0.0 - 1.0)
        
        Drives escalation decision:
          >= 0.70 → Native only (no LLM needed)
          0.50-0.69 → Native + escalation flag
          < 0.50 → Escalate to external LLM
        """
        # Keyword quality (0-0.35)
        kw_score = min(len(keywords) / 8, 1.0) * 0.35
        if keywords:
            avg_kw_score = sum(k.score for k in keywords) / len(keywords)
            kw_score *= (0.5 + avg_kw_score * 5)  # Boost if high quality
            kw_score = min(kw_score, 0.35)

        # Synthesis quality (0-0.25)
        innovation = synthesis.get("innovation_potential", 0.0)
        disciplines = synthesis.get("disciplines_detected", 0)
        synth_score = (innovation * 0.6 + min(disciplines / 3, 1.0) * 0.4) * 0.25

        # Mirror convergence (0-0.30)
        if mirror_state and mirror_state.converged:
            mirror_score = mirror_state.convergence_score * 0.30
        elif mirror_state:
            mirror_score = mirror_state.convergence_score * 0.15
        elif mode in (AnalysearchMode.QUICK, AnalysearchMode.STANDARD):
            mirror_score = 0.18  # Standard default (no mirror needed)
        else:
            mirror_score = 0.10

        # Knowledge base coverage (0-0.10)
        kb_hits = sum(1 for k in keywords if k.definition and "detected" not in k.definition)
        kb_score = min(kb_hits / max(len(keywords), 1), 1.0) * 0.10

        total = kw_score + synth_score + mirror_score + kb_score
        return round(min(total, 1.0), 4)

    def _build_routing_hint(self, lang: Dict, analysis: Dict) -> Dict:
        hint = {
            "lang_code": lang["code"],
            "lang_name": lang["name"],
            "lang_confidence": lang["confidence"],
            "script": lang["script"],
            "preferred_model": lang.get("routing_model"),
            "query_type": analysis.get("query_type", "exploration"),
            "complexity": analysis.get("complexity", "medium"),
            "prefer_regional": lang["code"] in ("th", "th+en", "ja", "ko", "zh", "vi"),
        }
        if lang.get("routing_model"):
            hint["reason"] = f"{lang['name']} detected → route to {lang['routing_model']}"
        return hint

    def _find_sources(self, keywords: List[KeywordResult]) -> List[Dict]:
        """Stub: return knowledge base references for keywords"""
        sources = []
        for kw in keywords[:5]:
            if kw.keyword in CONCEPT_KNOWLEDGE_BASE:
                sources.append({
                    "keyword": kw.keyword,
                    "source_type": "delentia_knowledge_base",
                    "relevance": kw.score,
                    "status": "available",
                    "category": kw.category,
                })
            else:
                sources.append({
                    "keyword": kw.keyword,
                    "source_type": "computed_analysis",
                    "relevance": kw.score,
                    "status": "inferred",
                    "category": kw.category,
                })
        return sources

    def get_stats(self) -> Dict:
        return {
            "engine": "delentia-native-v1",
            "total_queries": self._query_count,
            "knowledge_base_size": len(CONCEPT_KNOWLEDGE_BASE),
            "disciplines_tracked": len(DISCIPLINE_KEYWORDS),
        }
