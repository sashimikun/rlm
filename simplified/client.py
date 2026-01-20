from abc import ABC, abstractmethod
import random

class BaseClient(ABC):
    @abstractmethod
    def completion(self, messages: list[dict[str, str]]) -> str:
        pass

class MockClient(BaseClient):
    """
    A mock client that simulates RLM behavior for testing purposes.
    It follows a simple script based on the prompt content.
    """
    def __init__(self):
        self.call_count = 0

    def completion(self, messages: list[dict[str, str]]) -> str:
        self.call_count += 1
        last_message = messages[-1]['content']

        # Simple simulation for a math problem
        if "Calculate 5 * 5" in last_message:
            return "I will use Python to calculate this.\n```repl\nresult = 5 * 5\nprint(result)\n```"

        if "REPL output" in last_message and "25" in last_message:
            return "The calculation is done.\nFINAL(25)"

        # Simulation for recursion
        if "capital of France" in last_message and "Name" not in last_message:
             # First call: decide to use recursion
             return "I need to find out what the capital of France is. I will ask the LLM.\n```repl\ncapital = llm_query('Name the capital city of France')\nprint(capital)\n```"

        if "REPL output" in last_message and "Paris" in last_message:
             return "I have found the answer.\nFINAL(Paris)"

        if "Name the capital city of France" in last_message:
            # Inner call
            return "Paris"

        if "Calculate 10 + 10" in last_message:
            return "I will calculate this.\n```repl\nx = 10 + 10\n```\nFINAL_VAR(x)"

        return "FINAL(I don't know)"
