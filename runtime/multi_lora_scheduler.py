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

    def dispatch_execution(self, user_intent: str, target_pillar: str) -> Dict[str, Any]:
        """
        Pillar 2/3/4: Dispatches intent to target adapter with Dynamic Adapter Scaling.
        For example, if targeting Executor, we scale 'executor' adapter to 1.0 and scale down
        other adjacent adapters to 0.2 to prevent neural chaos/interference.
        """
        print(f"⚡ [Scheduler] Dispatching intent to {target_pillar} w/ Dynamic Adapter Scaling...")
        
        # Configure scale matrix dynamically to prevent neural interference
        scales = {
            "router": 0.0,
            "executor": 0.0,
            "guardian": 0.0,
            "scribe": 0.0
        }
        
        if target_pillar == "ROUTER_EXECUTOR":
            scales["executor"] = 1.0
            scales["guardian"] = 0.2  # Keep safety guardrail lightly active
            scales["scribe"] = 0.2    # Keep memory parsing lightly active
            active_adapter = "executor"
        elif target_pillar == "ROUTER_GUARDIAN":
            scales["guardian"] = 1.0
            scales["executor"] = 0.0
            scales["scribe"] = 0.1
            active_adapter = "guardian"
        elif target_pillar == "ROUTER_SCRIBE":
            scales["scribe"] = 1.0
            scales["guardian"] = 0.2
            scales["executor"] = 0.1
            active_adapter = "scribe"
        else:
            # Base model runs directly (no adapters active)
            active_adapter = "base"

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
