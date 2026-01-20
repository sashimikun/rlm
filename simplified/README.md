# Simplified RLM Implementation

This directory contains a minimal, standalone implementation of the Recursive Language Model (RLM) logic.

## Overview

The simplified RLM reduces the complexity of the full repository into four core components:

1.  **RLM (`rlm.py`)**: The main controller. It manages the conversation history, calls the LLM, and orchestrates the Read-Eval-Print Loop (REPL).
2.  **Environment (`env.py`)**: A lightweight wrapper around Python's `exec()`. It captures `stdout` and `stderr` and maintains variable state between executions.
3.  **Client (`client.py`)**: An abstract base class for LLM backends and a `MockClient` for testing without an API key.
4.  **Parsing Utils (`utils.py`)**: Helper functions to extract code blocks (` ```repl ... ``` `) and final answers (`FINAL(...)`) from the LLM's response.

## Mapping to Core Logic

| Core Concept | Simplified Implementation | Design Decision |
| :--- | :--- | :--- |
| **Recursion** | `env.py` injects `llm_query` | We use a simple callback function that triggers the LLM client directly. This simulates recursion depth=1 (or strictly sequential calls) without the complexity of a multi-process socket server. |
| **Isolation** | `LocalEnv` uses `exec()` | Instead of Docker or Modal containers, we execute code in the local process. **Warning**: This is not secure for untrusted code but simplifies deployment for study. |
| **Networking** | Direct function calls | The complex TCP socket/HTTP broker architecture is replaced by direct function calls, as everything runs in a single process. |
| **History** | In-memory list | Conversation history is managed as a simple list of message dictionaries passed to the client. |

## Usage

### Running the Demo

A demonstration script is provided to verify the logic using a Mock Client (no API key required).

```bash
python3 simplified/demo.py
```

### Using with a Real LLM

To use this with a real LLM (e.g., OpenAI), implement a client wrapper:

```python
from simplified.rlm import RLM
from simplified.client import BaseClient
import openai

class OpenAIClient(BaseClient):
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def completion(self, messages):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content

rlm = RLM(client=OpenAIClient("your-key"))
answer = rlm.completion("What is the 10th Fibonacci number?")
print(answer)
```
