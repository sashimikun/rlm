# Simplified Interfaces

## 1. LLM Client (`BaseClient`)

A simple abstraction for the underlying Large Language Model.

```python
class BaseClient:
    def completion(self, messages: list[dict[str, str]]) -> str:
        """
        Sends a list of messages to the LLM and returns the generated text.

        Args:
            messages: A list of dicts with 'role' (system/user/assistant) and 'content'.

        Returns:
            The string response from the model.
        """
        pass
```

## 2. Environment (`LocalEnv`)

Handles the execution of code blocks.

```python
class LocalEnv:
    def __init__(self, llm_callback: Callable[[str], str]):
        """
        Args:
            llm_callback: A function that takes a prompt string and returns a response string.
                          This is injected as `llm_query` into the environment.
        """
        pass

    def execute(self, code: str) -> dict:
        """
        Executes the provided Python code.

        Args:
            code: Python source code to run.

        Returns:
            A dictionary containing:
            - 'stdout': Captured standard output.
            - 'stderr': Captured standard error.
            - 'locals': Dictionary of local variables (converted to string/repr).
        """
        pass
```

## 3. Recursive Language Model (`RLM`)

The main orchestrator.

```python
class RLM:
    def __init__(self, client: BaseClient, max_iterations: int = 10):
        self.client = client
        self.max_iterations = max_iterations

    def completion(self, prompt: str) -> str:
        """
        Runs the RLM loop for a given user prompt.

        Args:
            prompt: The user's input query.

        Returns:
            The final answer text.
        """
        pass
```
