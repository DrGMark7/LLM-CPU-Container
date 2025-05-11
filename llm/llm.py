import time
import random

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class LLM:
    def __init__(self, model_path):
        self.model_path = model_path
        self.mode = None
        self.tokenizer = None

    def load_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)

    def generate_text(self, prompt: str) -> str:
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model and tokenizer have not been loaded. Call load_model() first.")

        inputs = self.tokenizer(prompt, return_tensors="pt")
        generate_ids = self.model.generate(
            inputs.input_ids,
        )

        return self.tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
