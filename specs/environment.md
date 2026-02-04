# Environment Specification

## Purpose
The Environment allows the LLM to "act" by running Python code. It must persist state so that variables defined in one step are available in the next.

## Core Requirements

1.  **Persistence**:
    *   Variables defined in one `exec()` block must be available in subsequent blocks.
    *   Ideally implemented by maintaining a `globals` dictionary that is passed to every `exec()` call.

2.  **Input/Output Capture**:
    *   Must capture `stdout` (print statements) to feed back to the LLM.
    *   Must capture `stderr` (errors) to allow the LLM to self-correct.

3.  **Injected Globals**:
    *   `context`: The data payload. Can be a string, list, or whatever the user provided.
    *   `llm_query(prompt, model=None)`: Function to perform a recursive LLM call.
    *   `llm_query_batched(prompts, model=None)`: Function for concurrent calls.
    *   `FINAL(answer)` / `FINAL_VAR(var_name)`: Markers or functions to signal termination. (Or the RLM parsing logic can detect these patterns in the code, but having them as functions that maybe print a special token is also a valid design).

4.  **Safety (Optional for Simplified)**:
    *   In a real system, dangerous builtins (`os.system`, etc.) should be blocked.
    *   For the simplified version, we can use standard `exec` without restrictions, or minimal blocking.

## Implementation Details (Simplified)

```python
class LocalEnv:
    def __init__(self, client):
        self.globals = {}
        self.locals = {}
        self.client = client # Access to LLM for recursive calls
        self.setup_globals()

    def setup_globals(self):
        self.globals['llm_query'] = self._llm_query
        # ... other builtins

    def _llm_query(self, prompt):
        # Callback to client
        return self.client.completion(prompt)

    def execute(self, code):
        # Capture stdout/stderr
        # exec(code, self.globals, self.locals)
        # Return result
```

## Context Loading
*   The `context` variable is special. It should be loaded before the first user prompt.
*   If the context is huge (files), the Environment might handle lazy loading, but for simplicity, we assume it fits in memory (RAM), just not in the LLM context window.
