# predict.py for Replicate deployment
import os
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from cog import BasePredictor, Input, Path

class Predictor(BasePredictor):
    def setup(self):
        """Load the model and tokenizer into memory."""
        self.model_name = "unsloth/Meta-Llama-3.1-8B-bnb-4bit"
        self.adapter_path = "./models/adapters/jitna_v0.2_toon"
        
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            load_in_4bit=True
        )
        # Load PEFT adapter if available
        if os.path.exists(self.adapter_path):
            print(f"Loading adapter weights from: {self.adapter_path}")
            self.model = PeftModel.from_pretrained(self.model, self.adapter_path)
            
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def predict(
        self,
        intent: str = Input(description="User intent query (e.g. Thai or English prompt)"),
    ) -> str:
        """Run a single prediction on the model."""
        # Standard JITNA v3 TOON system prompt
        system_prompt = (
            "<|system|>\n"
            "You are Delentia OS v0.2 — a constitutional AI operating under RCT v5 governance. "
            "You process intents through the JITNA v3 protocol. "
            "You respond in TOON format (Token-Oriented Object Notation) for token efficiency. "
            "Your responses must be factual, safe, and PDPA-compliant. "
            "You must respond using the 6 JITNA fields: I=Intent, D=Data, Δ=Delta, A=Approach, R=Reflection, M=Memory.\n"
            f"<|user|>\n{intent}\n"
            "<|assistant|>\n"
        )
        
        inputs = self.tokenizer(system_prompt, return_tensors="pt").to("cuda")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Strip the prompt from response
        if response.startswith(system_prompt):
            response = response[len(system_prompt):]
        return response.strip()
