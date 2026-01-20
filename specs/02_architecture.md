# Simplified Architecture

## Overview
The simplified implementation runs entirely within a single Python process for ease of understanding and debugging. It removes the TCP socket servers and isolated networked environments found in the upstream `rlm` repo, while preserving the functional "recursion".

## Components

### 1. `ToolLoopAgent` (`simplified/agent.py`)
- **Inputs**: `system_prompt`, `user_query`, `tools` (list), `llm` (client).
- **State**: `messages` (list of dicts).
- **Loop**:
  1. `llm.generate(messages)` -> `response`.
  2. Parse `response` -> `text` + `tool_calls` (Code Blocks).
  3. If `tool_calls`:
     - Execute each tool.
     - Append result to `messages`.
     - Continue Loop.
  4. If `final_answer` detected or max steps reached:
     - Return result.

### 2. `PythonREPL` Tool (`simplified/tools.py`)
- Wraps Python's `exec()`.
- **Scope**: Maintains a `globals` dictionary.
- **Injected Functions**:
  - `llm_query(prompt)`: A function injected into `globals` that allows the code to call the LLM. In the simplified version, this wraps a synchronous call to a fresh `ToolLoopAgent` (or the LLM directly) with `depth + 1`.

### 3. `MinimalLLM` (`simplified/llm.py`)
- A simple wrapper around an LLM provider (e.g., OpenAI or a Mock).
- Standardizes input (messages) and output (text).

## Data Flow (Recursive)

1. **User** calls `agent.run("Solve X")`.
2. **Agent** generates code: `sub_result = llm_query("Sub-problem of X")`.
3. **REPL** executes code:
   - Calls `llm_query("Sub-problem of X")`.
   - **New Agent** (Depth 1) is instantiated.
   - **New Agent** solves sub-problem and returns string.
4. **REPL** assigns result to `sub_result`.
5. **Agent** (Depth 0) uses `sub_result` to compute final answer.
