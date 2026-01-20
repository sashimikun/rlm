# Simplified Recursive Language Model (RLM)

This is a minimal implementation of the RLM concept using the **ToolLoopAgent** pattern. It strips away the complex networking and isolation of the original repo to focus on the core "recursive loop" where an LLM can generate code that calls the LLM again.

## Concepts

1.  **ToolLoopAgent**: The main loop that queries the LLM, executes returned tools (code), and feeds results back.
2.  **Recursion**: The `PythonREPL` tool has a special function `llm_query(prompt)` injected into its global scope. This allows the generated code to spin up a sub-agent (increasing depth) to solve sub-problems.

## Mapping to Specs

- **Concepts**: Implements `specs/01_core_concepts.md`.
- **Architecture**: Implements `specs/02_architecture.md` (Single process, `exec` based).
- **Loop**: Implements `specs/03_tool_loop.md` (Iterative generate -> execute -> feed loop).

## Usage

### Prerequisites
- Python 3.10+
- (Optional) `OPENAI_API_KEY` env var. If not provided, it runs with a Mock LLM.

### Running the Example

```bash
python simplified/main.py
```

### Example Flow (Mock)

1.  **User**: "Compute complex value"
2.  **Agent (Depth 0)**: Decides it needs a sub-value. Generates code:
    ```python
    val = llm_query('What is the magic number?')
    print(val)
    ```
3.  **REPL**: Executes code. Calls `llm_query`.
4.  **Agent (Depth 1)**: Receives "What is the magic number?". Returns "The magic number is 42."
5.  **REPL**: Returns "42" to Agent 0.
6.  **Agent (Depth 0)**: Receives result. Returns "Final Answer: 42".

## Differences from Upstream (`rlm/`)

- **No Networking**: Everything runs in one process. Upstream uses TCP sockets.
- **No Isolation**: Code runs with `exec()`. Upstream supports Docker/Modal.
- **Simplified Loop**: Uses a basic `while` loop instead of the complex event-driven structures.
- **Minimal Types**: No complex dataclasses for messages/history.
