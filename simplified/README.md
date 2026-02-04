# Simplified Recursive Language Model (RLM)

This is a minimal implementation of the Recursive Language Model architecture using **Vercel AI SDK 6**.

## Overview

RLM allows an LLM to write code that calls the LLM itself (recursion). This enables the model to break down complex problems into sub-problems, solve them using a REPL, and combine the results.

This implementation maps to the core concepts described in `specs/architecture.md`:

| RLM Concept | Simplified Implementation |
|-------------|---------------------------|
| **RLM Loop** | `generateText` with `maxSteps` (ToolLoopAgent pattern) |
| **Environment** | `PythonEnvironment` (Persistent `python-shell` process) |
| **Recursion** | `CallbackServer` (Node.js) + `llm_query` (Python) |

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set your OpenAI API key in `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

3. Ensure you have Python installed.

## Usage

Run the example:

```bash
npm start
```

Or run with a custom prompt:

```bash
npm start "Verify if 9999991 is prime. If not, ask the LLM for its factors using llm_query()."
```

## How It Works

1. **Host (Node.js)**: Starts an HTTP server (`CallbackServer`) to listen for sub-queries.
2. **Environment (Python)**: A Python process is spawned. A `llm_query()` function is injected into its global scope.
3. **Loop**: The LLM generates Python code.
   - If the code calls `llm_query("question")`, the Python process sends a request to the Host.
   - The Host pauses, calls `rlm("question")` (recursion), and returns the answer to Python.
4. **Result**: The Python code completes, and its output is fed back to the LLM.

## Differences from Upstream `rlm`

- **Language**: This is a TypeScript implementation using Vercel AI SDK, whereas the original is pure Python.
- **Isolation**: No Docker/Modal sandboxing. Code runs locally.
- **Persistence**: Minimal process-based persistence. No complex serialization/dill support.
- **Protocol**: Simple JSON-over-HTTP instead of custom TCP sockets.
