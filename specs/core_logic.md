# Core Logic: Recursive Language Models (RLM)

## First Principles
The fundamental limitation of standard LLMs is the finite context window. Even with large context windows, reasoning over massive data is inefficient and prone to "lost in the middle" phenomena.

**RLM shifts the paradigm from "Retrieval-Augmented Generation" (RAG) to "Recursive-Augmented Generation" (or Programmable Context).**

Instead of retrieving chunks and stuffing them into the prompt, RLM gives the model:
1.  **A Handle to the Data**: The data is loaded into a persistent execution environment (REPL) as a variable (e.g., `context`). The model cannot see the content of this variable directly unless it prints it, but it can manipulate it using code.
2.  **A Tool to Query Itself**: The model is given a function (e.g., `llm_query(prompt, context_chunk)`) that allows it to spawn a sub-instance of itself to process a specific piece of data.

## The RLM Loop
The RLM operates in a loop similar to ReAct (Reasoning + Acting), but specialized for code-based data processing.

1.  **Initialize**:
    *   Load the user's data (context) into the Environment.
    *   Construct a System Prompt that explains the available tools (`context`, `llm_query`) and the objective.

2.  **Iterate**:
    *   **Prompt**: Send the current conversation history to the LLM.
    *   **Generate**: The LLM generates a response, potentially containing code blocks (e.g., inside ` ```repl ... ``` `).
    *   **Execute**:
        *   Extract code blocks.
        *   Execute them in the persistent Environment.
        *   The code may access `context`.
        *   The code may call `llm_query()` to perform sub-tasks (e.g., "Summarize this chunk of text").
    *   **Feedback**: Capture `stdout`, `stderr`, and updated `locals()`. Append this execution result to the conversation history.
    *   **Check Termination**: If the LLM produces a final answer marker (e.g., `FINAL(answer)` or `FINAL_VAR(var_name)`), terminate and return the result.

3.  **Recursive Decomposition**:
    *   The power of RLM comes from the model writing code to *decompose* the problem.
    *   Example: "For each chapter in `context`, call `llm_query('Summarize', chapter)`. Then call `llm_query('Combine summaries', all_summaries)`."
    *   This effectively extends the context window infinitely by processing data in chunks and aggregating results, driven entirely by the model's own logic.

## Simplified Abstraction
To build a simplified version, we need:
1.  **Agent**: A loop that prompts an LLM and parses its output.
2.  **Environment**: A Python `exec()` scope that persists variables between steps.
3.  **Interface**: A set of functions injected into the Environment (`llm_query`) that bridge the gap back to the Agent.
