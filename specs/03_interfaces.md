# Interfaces

## LLMClient

```python
class LLMClient:
    def completion(self, prompt: str) -> str:
        """
        Generates a completion for the given prompt.
        """
        pass
```

## Environment

```python
class Environment:
    def __init__(self, llm_client: LLMClient):
        pass

    def execute(self, code: str) -> str:
        """
        Executes the provided Python code string.
        Returns the captured stdout + any errors.
        """
        pass

    def get_variable(self, name: str) -> Any:
        """
        Retrieves a variable from the environment.
        """
        pass
```

## RLM

```python
class RLM:
    def __init__(self, llm_client: LLMClient, max_iterations: int = 10):
        pass

    def ask(self, question: str) -> str:
        """
        Main entry point. Takes a user question and returns the answer.
        """
        pass
```

## Prompts

**System Prompt:**
Should instruct the model to:
1.  Think about the problem.
2.  Write Python code to solve it or gather information.
3.  Use `llm_query(prompt)` to ask sub-questions.
4.  Use `final_answer = "..."` (or a specific variable) to return the result.
