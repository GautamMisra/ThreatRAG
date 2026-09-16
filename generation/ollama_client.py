import json
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi4-mini"


class OllamaClient:

    def __init__(self, model=MODEL):
        self.model = model

    def generate(self, prompt, temperature=0.2):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]

    def generate_json(self, prompt, temperature=0.2):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature
            }
        }

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return json.loads(data["response"])


if __name__ == "__main__":

    client = OllamaClient()

    response = client.generate(
        "Say hello in one sentence.",
        temperature=0.2
    )

    print("\n========== OLLAMA TEST ==========")
    print(response)
    print("=================================")