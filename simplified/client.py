import os
from abc import ABC, abstractmethod


class BaseClient(ABC):
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name

    @abstractmethod
    def completion(self, prompt: str) -> str:
        pass


class MockClient(BaseClient):
    def __init__(self, responses: dict[str, str] = None):
        super().__init__()
        self.responses = responses or {}
        self.default_response = "I don't know the answer to that."

    def completion(self, prompt: str) -> str:
        # Simple exact match mock
        if prompt in self.responses:
            return self.responses[prompt]

        # Heuristic for demo purposes if no match found
        print(f"[MockClient] Received prompt: {prompt[:50]}...")
        return self.default_response


class SimpleOpenAIClient(BaseClient):
    def __init__(self, model_name: str = "gpt-4o", api_key: str = None):
        super().__init__(model_name)
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError("Please install openai package: pip install openai") from e

        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))

    def completion(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )
        return response.choices[0].message.content
