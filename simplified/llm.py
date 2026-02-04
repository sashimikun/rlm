from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    def completion(self, prompt: str) -> str:
        """
        Generates a completion for the given prompt.
        """
        pass

class MockLLMClient(LLMClient):
    """
    A mock LLM client for testing purposes.
    It returns predefined responses based on the prompt content.
    """
    def __init__(self, responses: dict[str, str] = None):
        self.responses = responses or {}
        self.default_response = "I don't know how to respond to that."

    def completion(self, prompt: str) -> str:
        # Simple keyword matching for mock responses
        for key, value in self.responses.items():
            if key in prompt:
                return value
        return self.default_response
