from abc import ABC, abstractmethod


class BaseClient(ABC):
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name

    @abstractmethod
    def completion(self, messages: list[dict[str, str]]) -> str:
        """
        Accepts a list of messages (role, content) and returns a string response.
        """
        pass

class MockClient(BaseClient):
    """
    A mock client that returns predefined responses based on the input prompt.
    Useful for testing without making real API calls.
    """
    def __init__(self, responses: dict[str, str] = None, default_response: str = "I don't know."):
        super().__init__("mock")
        self.responses = responses or {}
        self.default_response = default_response
        self.calls = []

    def completion(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(messages)
        # Get the last message content
        if not messages:
            return self.default_response

        last_msg = messages[-1]["content"]

        # Simple keyword matching
        for key, value in self.responses.items():
            if key in last_msg:
                return value

        return self.default_response

class OpenAIClient(BaseClient):
    """
    A simple wrapper around the OpenAI client.
    """
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        super().__init__(model_name)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Please install openai to use OpenAIClient: pip install openai"
            ) from None

    def completion(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        content = response.choices[0].message.content
        return content if content else ""
