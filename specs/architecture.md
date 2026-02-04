# RLM Architecture Specifications

## Overview
Recursive Language Models (RLMs) enable an LLM to perform complex tasks by allowing it to programmatically decompose problems and recursively call itself. Unlike standard chains or agents that have a fixed flow, an RLM operates within a Read-Eval-Print Loop (REPL) where it can write code that invokes the LLM again (recursion).

## Core Concepts

### 1. The RLM Loop
The core control flow is an iterative loop that mirrors the "ToolLoopAgent" pattern (or ReAct loop), but with a specific focus on code execution and recursion.

**Lifecycle:**
1. **User Request**: The loop starts with a user prompt.
2. **Prompt Generation**: The system constructs a prompt that includes:
   - System instructions (defining available tools/globals).
   - Message history (previous turns).
   - Current context/state.
3. **Model Inference**: The LLM generates a response.
   - The response may contain natural language and/or **Code Blocks**.
4. **Code Execution**: The system extracts code blocks and executes them in a **Sandboxed Environment**.
5. **Result Feedback**: The output of the code execution (stdout/return value) is added to the history.
6. **Termination**: The loop repeats until:
   - The model generates a specific "Final Answer".
   - A maximum number of iterations is reached.

### 2. The Environment (REPL)
The Environment is a persistent runtime (e.g., Python shell) where the model's code executes.

**Key Features:**
- **Persistence**: Variables defined in one turn are available in subsequent turns.
- **Context Injection**: The initial problem or data is loaded into the environment as a variable (e.g., `context`).
- **Globals**: The environment is pre-populated with helper functions.

### 3. Recursion Mechanism (`llm_query`)
This is the defining feature of RLM. The code executing inside the environment can call the LLM.

**Interface:**
- `llm_query(prompt: str, model: str | None = None) -> str`: A synchronous function available in the REPL.
- `llm_query_batched(prompts: list[str], ...) -> list[str]`: A batched version.

**Data Flow:**
1. LLM generates code: `answer = llm_query("What is the capital of France?")`
2. Environment executes code.
3. `llm_query` function pauses execution and sends a request to the **Host System**.
4. **Host System** receives request, calls the LLM (or another RLM instance), and gets the result.
5. Result is sent back to the Environment.
6. `llm_query` returns the string result.
7. Code execution continues.

### 4. LM Handler (Host-side)
The Host System acts as a server (or broker) that manages LLM access.
- It listens for requests from the Environment.
- It routes requests to the appropriate Model Client.
- It handles concurrency (if batched) and rate limits.

---

## Simplified Implementation (`/simplified`)

The simplified implementation will mirror this architecture using **Vercel AI SDK 6** (Node.js/TypeScript).

### Mapping to AI SDK
- **RLM Loop** -> `generateText` (or `streamText`) with `tools` and `maxSteps`.
  - `maxSteps` provides the loop behavior.
  - The model continues generating tool calls until it decides to stop (or `maxSteps` is hit).
- **Environment** -> A custom Tool (`execute_python`).
  - This tool will spawn a Python process (or use a library) to execute code.
  - It will maintain state (simulated by passing context or keeping a persistent process).
- **Recursion** -> `llm_query` callback.
  - The `execute_python` tool will inject a prelude into the Python script.
  - The prelude defines `llm_query` which calls back to the Node.js host (via HTTP/IPC).
  - The Node.js host, upon receiving `llm_query`, will trigger another `generateText` call.

### Interfaces

#### `execute_python` Tool
```typescript
type ExecutePythonArgs = {
  code: string;
};

type ExecutePythonResult = {
  stdout: string;
  stderr: string;
  result: any;
};
```

#### Recursion Callback (Host)
```typescript
// Exposed via local HTTP server
POST /llm-query
Body: { prompt: string, model?: string }
Response: { text: string }
```

### Out of Scope for Simplified Build
- **Isolated Environments**: No Docker/Modal/Prime sandboxes. Code runs locally.
- **Batched Queries**: Only single `llm_query` support for simplicity.
- **Complex Persistence**: We might restart the python process per tool call for simplicity, or keep a simple persistent process if feasible. *Decision: Restart per call but pass state if needed, or keep persistent process for true REPL.* (RLM uses persistent REPL).
- **Visualizer/Logging**: Minimal console logging only.
- **Multiple Backends**: Only one primary backend (e.g., OpenAI).
