# Simplified RLM Library Design

## Objective
Implement a minimal, working version of the Recursive Language Model (RLM) framework that demonstrates the core principles: Reason, Act, Recurse, Observe.

## Architecture

### 1. `SimpleRLM` (Controller)
-   **Main entry point**: `SimpleRLM(client, max_iterations=10)`
-   **Method**: `completion(prompt)`
-   **Responsibility**:
    -   Manages the loop.
    -   Handles prompting strategy (system prompt + history).
    -   Parses LLM output for code.
    -   Delegates execution to `SimpleEnv`.
    -   Detects final answer.

### 2. `SimpleEnv` (Environment)
-   **Responsibility**: Execute Python code.
-   **Implementation**: Uses Python's `exec` with a persistent dictionary for locals.
-   **Recursion**: Injects a `llm_query` function into the `exec` scope.
    -   This `llm_query` will directly call the `SimpleRLM`'s client (or a new `SimpleRLM` instance if we want true recursion depth handling, but for simplicity, we can just call the client directly or recurse via the same class).
    -   Let's make `llm_query` call the `client.completion` directly for this simplified version, as that's effectively what a sub-call is at depth 1.

### 3. `SimpleClient` (LLM Abstraction)
-   **Responsibility**: Abstract away the LLM provider.
-   **Implementation**: A dummy client for testing and an OpenAI-compatible client.

## Directory Structure
```
simplified/
├── __init__.py
├── rlm.py          # Contains SimpleRLM class
├── env.py          # Contains SimpleEnv class
├── client.py       # Contains SimpleClient and MockClient
└── prompts.py      # Basic prompts
```

## Key simplifications
1.  **No Socket Server**: The `llm_query` function in the environment will directly call the `Client`. This works because we are using `exec` in the same process. This removes the need for `LMHandler` and TCP/HTTP servers.
2.  **No Isolation**: We run code in `exec` in the same process.
3.  **Single Backend**: Only support one LLM backend.
4.  **Simplified Prompts**: Basic system prompts without complex history management or metadata.

## Flow
1.  User calls `rlm.completion("Calculate 5th Fibonacci")`.
2.  `SimpleRLM` creates `SimpleEnv`.
3.  `SimpleEnv` has `llm_query` which points to `client.completion`.
4.  Loop:
    -   LLM generates: "I will write a function. ```python def fib(n): ... print(fib(5))```"
    -   `SimpleEnv` executes code.
    -   Output "5" is captured.
    -   History updated.
    -   LLM sees output and says "The answer is 5."
    -   Loop ends.

## Handling Recursion
If the LLM writes:
```python
ans = llm_query("What is the capital of France?")
print(ans)
```
The `llm_query` function (injected into `exec` globals) will call `client.completion("What is the capital of France?")` and return the string. This simulates the recursion.
