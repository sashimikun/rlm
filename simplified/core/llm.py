import os
from dataclasses import dataclass
from typing import Any, List, Optional

@dataclass
class ChatMessage:
    role: str
    content: str

class MinimalLLM:
    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("Warning: 'openai' package not found. Running in Mock mode only.")

    def completion(self, messages: List[dict[str, Any]]) -> str:
        """
        Synchronous completion.
        Args:
            messages: List of dicts like {"role": "user", "content": "..."}
        """
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Error calling OpenAI: {e}"

        return self._mock_completion(messages)

    def _mock_completion(self, messages: List[dict[str, Any]]) -> str:
        """
        Simple mock logic for demonstration purposes if no API key is present.
        """
        last_msg = messages[-1]["content"]

        # Depth check: In the agent we append "Depth: N/M" to system prompt,
        # but here we only see messages.

        # Scenario: "Compute complex value"
        if "Compute complex value" in last_msg:
             return (
                 "I need to break this down. I'll ask for a sub-value first.\n"
                 "```python\n"
                 "print('Querying sub-agent...')\n"
                 "val = llm_query('What is the magic number?')\n"
                 "print(f'Received: {val}')\n"
                 "```"
             )

        # Scenario: Sub-agent answering "What is the magic number?"
        if "What is the magic number?" in last_msg:
            return "The magic number is 42."

        # Scenario: Handling the result of the tool execution
        # The user message will contain "Execution Result: ... Received: The magic number is 42."
        if "Received: The magic number is 42" in last_msg:
            return "The complex value is 42. Final Answer: 42."

        # Default
        return "I am a mock LLM. Ask me to 'Compute complex value' to see recursion."
