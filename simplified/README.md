# Simplified Recursive Language Model (RLM)

This is a minimal implementation of the Recursive Language Model architecture using **Vercel AI SDK 6**.
It demonstrates the core concept: an LLM loop that can execute code, which in turn can recursively call the LLM.

## Architecture

This simplified build maps to the `specs/architecture.md` as follows:

- **RLM Loop**: Implemented in `src/index.ts` using `generateText` with `maxSteps` (ToolLoopAgent pattern).
- **Environment**: A persistent Python process (`src/python-tool.ts` & `src/runner.py`) that maintains state between tool calls.
- **Recursion**: A local HTTP callback server (`src/server.js`) that the Python process calls via `llm_query()`.

## Files

- `src/index.ts`: The main entry point. Defines the agent loop and recursion handler.
- `src/server.ts`: A lightweight HTTP server for handling `llm_query` callbacks from Python.
- `src/python-tool.ts`: The Vercel AI SDK Tool definition that wraps the Python environment.
- `src/runner.py`: A Python script that runs in a loop, executing code and handling `llm_query` network requests.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set your OpenAI API key in `.env`:
   ```bash
   cp .env.example .env
   # Edit .env
   ```

3. Run the example:
   ```bash
   npm start
   ```

   Or with a custom prompt:
   ```bash
   npm start "Calculate the 20th prime number and ask llm_query() if it is a lucky number."
   ```

## Differences from Upstream RLM

- **Language**: TypeScript/Node.js (Host) vs Python (Host).
- **Environment**: Single simplified Python process vs Modular `Environments` (Docker, Modal, etc).
- **Communication**: Simple HTTP server vs ThreadingTCPServer with custom protocol.
- **Complexity**: Minimal error handling and configuration vs Production-ready.
