# Simplified RLM Design

## Objective
Implement a minimal, single-process version of RLM to demonstrate the core "Recursive Language Model" concept without the complexity of networking, isolation, or multiple backends.

## Core Components

### 1. `SimpleRLM` Class
The main controller.

-   **State**:
    -   `client`: An LLM client (can be a mock or a wrapper around OpenAI).
    -   `max_iterations`: Limit to prevent infinite loops.
    -   `history`: List of messages (User, Assistant, System).

-   **Methods**:
    -   `__init__(client, max_iterations=10)`
    -   `completion(prompt)`: The main entry point.
    -   `_execute_code(code, context_locals)`: Runs python code using `exec`.
    -   `_llm_query(prompt)`: The function exposed to the python environment. It simply calls `client.completion(prompt)`.

### 2. Execution Environment
Instead of a separate process/server, we will use Python's `exec` within the same process.

-   **Namespace**: We will maintain a `locals` dictionary that persists across iterations of the *same* completion call.
-   **Injection**: We will inject `llm_query` into this namespace so the code can call it.
-   **Output Capture**: We will redirect `sys.stdout` to capture the output of `print` statements.

### 3. Data Flow

1.  User calls `rlm.completion("Calculate the 10th Fibonacci number")`.
2.  RLM creates a `context_locals` dict containing `{"llm_query": self._llm_query}`.
3.  RLM Loop:
    a.  Send `history` to LLM.
    b.  LLM returns text, e.g., "I will write a function. ```python def fib(n): ... print(fib(10))```".
    c.  RLM extracts the code block.
    d.  RLM runs `exec(code, {}, context_locals)`.
    e.  Code runs, defines `fib`, prints result.
    f.  RLM captures stdout: "55\n".
    g.  RLM appends "Output: 55\n" to history.
    h.  RLM checks for termination condition (e.g., LLM says "Final Answer: 55").

### 4. Recursion Example
If the LLM writes:
```python
result = llm_query("What is the capital of France?")
print(result)
```
1.  `exec` runs this.
2.  `llm_query` is called.
3.  `SimpleRLM._llm_query` is executed.
4.  It calls `client.completion("What is the capital of France?")`.
5.  It returns "Paris".
6.  `result` becomes "Paris".
7.  `print(result)` outputs "Paris".

## file structure

-   `simplified/simple_rlm.py`: Contains `SimpleRLM` and a basic `MockLLM`.
-   `simplified/demo.py`: A script to run the simple RLM.
