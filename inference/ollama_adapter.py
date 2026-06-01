"""
ollama_adapter.py

Python client adapter for Delentia SLM served through Ollama.
Implements the OLLAMA_ADAPTER HexaCore role interface.

Usage:
  from inference.ollama_adapter import OllamaAdapter

  adapter = OllamaAdapter(model_name="delentia-jitna-v0.1")
  response = adapter.execute_intent("Summarize PDPA Article 19 in Thai")
  print(response.output)
"""

import json
import urllib.request
from dataclasses import dataclass

OLLAMA_DEFAULT_URL = "http://localhost:11434"
DEFAULT_MODEL      = "delentia-jitna-v0.1"

SYSTEM_PROMPT = (
    "You are Delentia OS — a constitutional AI operating under RCT v5 governance. "
    "Process intents through JITNA v3 protocol. "
    "Responses must be factual, safe, and PDPA-compliant."
)


@dataclass
class OllamaResponse:
    output: str
    model: str
    done: bool
    prompt_eval_count: int
    eval_count: int


class OllamaAdapter:
    """Thin adapter over Ollama REST API for Delentia SLM inference."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        base_url: str = OLLAMA_DEFAULT_URL,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 1024,
    ) -> None:
        self.model_name  = model_name
        self.base_url    = base_url.rstrip("/")
        self.temperature = temperature
        self.top_p       = top_p
        self.max_tokens  = max_tokens

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:  # nosec (localhost only)
            return json.loads(resp.read().decode())

    def health_check(self) -> bool:
        """Return True if Ollama is running and the model is available."""
        try:
            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:  # nosec
                tags = json.loads(resp.read())
                models = [m["name"] for m in tags.get("models", [])]
                return self.model_name in models
        except Exception:
            return False

    def execute_intent(self, intent: str, context: str = "") -> OllamaResponse:
        """
        Send an intent to the local SLM via Ollama.
        Returns an OllamaResponse with .output as the generated text.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        if context:
            messages.append({"role": "user", "content": f"Context: {context}"})
        messages.append({"role": "user", "content": intent})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": self.max_tokens,
            },
        }

        response = self._post("/api/chat", payload)

        return OllamaResponse(
            output=response.get("message", {}).get("content", ""),
            model=response.get("model", self.model_name),
            done=response.get("done", True),
            prompt_eval_count=response.get("prompt_eval_count", 0),
            eval_count=response.get("eval_count", 0),
        )

    def list_models(self) -> list[str]:
        """List all models available in local Ollama."""
        url = f"{self.base_url}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:  # nosec
            tags = json.loads(resp.read())
        return [m["name"] for m in tags.get("models", [])]
