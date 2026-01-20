# ToolLoopAgent Logic

This specification aligns with the Vercel AI SDK 6 `ToolLoopAgent` pattern.

## The Loop

The `run` method executes the following loop:

1.  **Initialize**:
    *   Append `user_prompt` to `messages`.
    *   Initialize `step_count = 0`.

2.  **Iterate**:
    *   **Check Step Limit**: If `step_count >= max_steps`, return "Max steps reached".
    *   **Generate**: Call LLM with current `messages`.
    *   **Parse**: Extract text content and any "tool calls" (in RLM, these are fenced code blocks like \`\`\`python ... \`\`\`).
    *   **Action**:
        *   If **Final Answer** found (e.g., text contains specific marker or no tools):
            *   Return Final Answer.
        *   If **Tool Calls** found:
            *   For each code block:
                *   Execute via `PythonREPL`.
                *   Capture `stdout`, `stderr`, and `locals` (optional).
            *   **Append History**: Add a message of type `tool_result` (or equivalent "user" message with execution output) to `messages`.
            *   Increment `step_count`.
            *   **Continue** to next iteration.

## Stop Conditions

1.  **Final Answer**: The model produces a response that does not contain tool calls, OR explicitly formats a final answer (e.g., `Final Answer: ...`).
    *   *Simplification*: We will treat any response *without* code blocks as a potential final answer, or look for a specific variable `final_answer` in the REPL state if the model is instructed to assign it.
    *   *Refinement*: RLM upstream looks for `find_final_answer`. We will simplify: if no code blocks, it's a final answer. Or if the code defines a `final_answer` variable, that's the result.

2.  **Max Steps**: `max_steps` (default ~10-30) prevents infinite loops.

3.  **Max Depth**: Handled at the `llm_query` level. If `depth > max_depth`, `llm_query` should fail or return a fallback.

## Tool Interface

A simplified tool interface:

```python
class Tool(Protocol):
    name: str
    description: str
    def run(self, input_data: str) -> str: ...
```

The `PythonREPL` implements this.
