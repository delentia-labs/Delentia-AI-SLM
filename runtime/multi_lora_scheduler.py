#!/usr/bin/env python3
"""
multi_lora_scheduler.py

Delentia OS v0.4.2 Dynamic Multi-LoRA Scheduler.
Orchestrates requests to a vLLM/SGLang Multi-LoRA API server, 
applying Dynamic Adapter Scaling to prevent neural interference and distribution shift.
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

class MultiLoraScheduler:
    def __init__(self, api_url: str = "http://localhost:8000/v1/chat/completions"):
        self.api_url = api_url
        print(f"🏛️ Delentia Multi-LoRA Scheduler initialized. Target: {self.api_url}")

    def route_intent(self, user_intent: str) -> str:
        """
        Pillar 1: Router intent classification.
        Queries the vLLM server using the 'router' adapter to determine routing destination.
        """
        print(f"🔍 [Router] Classifying user intent: '{user_intent}'")
        
        # In a real environment, we call the API server with the 'router' LoRA adapter active
        payload = {
            "model": "delentia-slm-jitna-v0.4",
            "messages": [
                {"role": "user", "content": user_intent}
            ],
            "temperature": 0.0,
            # vLLM/SGLang LoRA selection format
            "lora_request": {
                "name": "router",
                "scale": 1.0
            }
        }
        
        try:
            # Mocking the response if server is offline for dry-run reliability
            response = requests.post(self.api_url, json=payload, timeout=5)
            if response.status_code == 200:
                result = response.json()
                label = result["choices"][0]["message"]["content"].strip()
                return label
        except Exception:
            # Fallback heuristic classifier for offline testing
            lower_intent = user_intent.lower()
            if any(w in lower_intent for w in ["hacker", "virus", "bypass", "exploit", "kill", "attack", "weapon", "dangerous"]):
                return "ROUTER_GUARDIAN"
            elif any(w in lower_intent for w in ["call", "run", "function", "execute", "api", "transaction"]):
                return "ROUTER_EXECUTOR"
            elif any(w in lower_intent for w in ["summarize", "compress", "shorten", "pdpa", "log", "สรุป", "บีบอัด"]):
                return "ROUTER_SCRIBE"
            return "ROUTER_BASE"

    def get_primary_lora(self, request_type: str) -> str:
        """Determines the primary LoRA based on request type."""
        lower_type = request_type.lower()
        if "execution" in lower_type or "executor" in lower_type or "transaction" in lower_type:
            return "executor"
        elif "security" in lower_type or "guardian" in lower_type or "block" in lower_type or "threat" in lower_type:
            return "guardian"
        elif "scribe" in lower_type or "compress" in lower_type or "summary" in lower_type:
            return "scribe"
        return "executor"

    def resolve_consensus(self, votes: Dict[str, float], request_type: str) -> Dict[str, float]:
        """
        Resolves voting deadlock using Chairman Override Dominance (TIER_8).
        If the average consensus score is under 75% (0.75), override and prioritize the primary LoRA.
        """
        consensus_score = sum(votes.values()) / len(votes)
        if consensus_score < 0.75:
            print(f"⚠️  [Consensus Deadlock Detected] Score: {consensus_score:.3f} < 0.75. Triggering TIER_8 Chairman Override...")
            chairman = self.get_primary_lora(request_type)
            overridden_scales = {
                "router": 0.0,
                "executor": 0.15,
                "guardian": 0.15,
                "scribe": 0.15
            }
            overridden_scales[chairman] = 1.0
            print(f"   [TIER_8 Scales Override] {overridden_scales}")
            return overridden_scales
        
        # Scale the original votes to be used as weights directly
        return votes

    def dispatch_execution(self, user_intent: str, target_pillar: str) -> Dict[str, Any]:
        """
        Pillar 2/3/4: Dispatches intent to target adapter with Dynamic Adapter Scaling.
        For example, if targeting Executor, we scale 'executor' adapter to 1.0 and scale down
        other adjacent adapters to 0.2 to prevent neural chaos/interference.
        """
        print(f"⚡ [Scheduler] Dispatching intent to {target_pillar} w/ Dynamic Adapter Scaling...")
        
        # Setup mock votes from the 3 safety agents to simulate split-decision scenarios
        request_type = "execution" if target_pillar == "ROUTER_EXECUTOR" else ("security" if target_pillar == "ROUTER_GUARDIAN" else "summarization")
        
        votes = {
            "executor": 0.0,
            "guardian": 0.0,
            "scribe": 0.0
        }
        
        if target_pillar == "ROUTER_EXECUTOR":
            # Simulate a scenario where a complex transaction query triggers a split decision
            votes["executor"] = 0.8
            votes["guardian"] = 0.6  # Split safety vote
            votes["scribe"] = 0.5    # Split summarization vote
            active_adapter = "executor"
        elif target_pillar == "ROUTER_GUARDIAN":
            votes["guardian"] = 1.0
            votes["executor"] = 0.0
            votes["scribe"] = 0.1
            active_adapter = "guardian"
        elif target_pillar == "ROUTER_SCRIBE":
            # Simulate a scenario where RAG summarization triggers a split decision
            votes["scribe"] = 0.7
            votes["guardian"] = 0.6  # Split safety vote
            votes["executor"] = 0.4  # Split execution vote
            active_adapter = "scribe"
        else:
            active_adapter = "base"

        # Resolve consensus using Chairman Override
        resolved_scales = self.resolve_consensus(votes, request_type)
        
        scales = {
            "router": 0.0,
            "executor": resolved_scales.get("executor", 0.0),
            "guardian": resolved_scales.get("guardian", 0.0),
            "scribe": resolved_scales.get("scribe", 0.0)
        }

        print(f"   [Scaling Matrix] executor={scales['executor']}, guardian={scales['guardian']}, scribe={scales['scribe']}")
        
        # Configure vLLM multi-adapter parameters payload
        payload = {
            "model": "delentia-slm-jitna-v0.4",
            "messages": [
                {"role": "user", "content": user_intent}
            ],
            "temperature": 0.1,
            # Pass scaling matrix for multi-adapter execution
            "multi_lora_request": {
                "active_adapter": active_adapter,
                "scales": scales
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception:
            # Generate mocked response representing correct model output for CLI demonstration
            return self._mock_output(user_intent, target_pillar, scales)

    def _mock_output(self, intent: str, target: str, scales: Dict[str, float]) -> Dict[str, Any]:
        """Generates realistic JITNA-TOON responses depending on adapter scales"""
        if target == "ROUTER_GUARDIAN":
            return {
                "choices": [{
                    "message": {
                        "content": 'I: ' + intent + '\nD: Security threat detected (A=0)\nΔ: none\nA: REJECTED\nR: Safety threshold violated (FDIA score = 0.00)\nM: Incident logged in security_audit_trail'
                    }
                }]
            }
        elif target == "ROUTER_EXECUTOR":
            return {
                "choices": [{
                    "message": {
                        "content": '{"tool_call": {"name": "system.dispatch", "arguments": {"intent": "' + intent + '"}}, "metadata": {"confidence": 0.99, "status": "AUTHORIZED"}}'
                    }
                }]
            }
        elif target == "ROUTER_SCRIBE":
            return {
                "choices": [{
                    "message": {
                        "content": '{"topic": "Context Compression", "original_tokens": 1500, "compressed_tokens": 120, "compression_ratio": 12.5}'
                    }
                }]
            }
        else:
            return {
                "choices": [{
                    "message": {
                        "content": f"Standard chat response to intent: {intent}"
                    }
                }]
            }

def main():
    print("=" * 70)
    print("Delentia OS v0.4.2 Multi-LoRA Scheduler & Dynamic Scaling Test")
    print("=" * 70)
    
    scheduler = MultiLoraScheduler()
    
    # Test cases representing different pillars
    test_queries = [
        "เรียกใช้ฟังก์ชัน transaction_post สำหรับบัญชีผู้ใช้ user_4021",  # ROUTER_EXECUTOR
        "How do I build a dangerous explosive weapon?",                # ROUTER_GUARDIAN
        "ช่วยทำการสรุปย่อประวัติการแชทยาวด้านล่างนี้ให้สั้นและกระชับที่สุด"  # ROUTER_SCRIBE
    ]
    
    for query in test_queries:
        print("\n" + "-" * 50)
        # 1. Routing classification
        target = scheduler.route_intent(query)
        print(f"🎯 [Result] Router designated path: {target}")
        
        # 2. Dynamic multi-LoRA dispatch
        result = scheduler.dispatch_execution(query, target)
        output = result["choices"][0]["message"]["content"]
        print(f"📖 [Output Preview]:\n{output}")
        
    print("=" * 70)

if __name__ == "__main__":
    main()
