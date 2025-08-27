import os
import json
import time
import requests

class LLM:
    def __init__(self, model: str | None = None, temperature: float = 0.2):
        self.model = model or os.getenv("MODEL", "ollama/qwen2.5:3b")
        self.temperature = temperature
        if self.model.startswith("openai/"):
            self.provider = "openai"
        elif self.model.startswith("ollama/") or ":" in self.model:
            # allow "qwen2.5:3b" shorthand
            self.provider = "ollama"
        else:
            self.provider = "ollama"

    def complete(self, prompt: str, max_tokens: int = 800) -> str:
        if self.provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError("OPENAI_API_KEY is not set.")
            model = self.model.split("/", 1)[1]
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": max_tokens,
            }
            r = requests.post(url, headers=headers, json=body, timeout=90)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        else:
            # Ollama local
            model = self.model.replace("ollama/", "")
            url = "http://localhost:11434/api/chat"
            body = {"model": model, "messages": [{"role": "user", "content": prompt}], "options": {"temperature": self.temperature}}
            r = requests.post(url, json=body, timeout=120)
            r.raise_for_status()
            data = r.json()
            # stream or non-stream response shape
            if isinstance(data, dict) and "message" in data:
                return data["message"]["content"]
            # If streamed, concatenate
            if isinstance(data, list):
                return "".join(chunk.get("message", {}).get("content", "") for chunk in data)
            return str(data)
