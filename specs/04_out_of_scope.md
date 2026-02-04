# Out of Scope

The simplified implementation (`/simplified`) intentionally omits the following features from the upstream `rlm` repo to focus on the core recursive loop:

1.  **Networked/Isolated Environments**:
    *   No TCP Socket Server (`LMHandler`).
    *   No Docker, Modal, or Prime sandboxes.
    *   All code execution happens in the main process (using `exec`). **Security Warning**: Do not run untrusted code with this simplified version.

2.  **Complex Logging/Visualization**:
    *   No `RLMLogger` or `.jsonl` trajectory artifacts.
    *   No web-based visualizer.
    *   Simple print statements will be used for tracing.

3.  **Multi-Backend Routing**:
    *   Upstream supports routing specific depths to different backends (OpenAI vs Local).
    *   Simplified version uses a single LLM backend configuration.

4.  **Async/Batched Execution**:
    *   Upstream supports `acompletion` and batched queries.
    *   Simplified version is synchronous.

5.  **Strict Persistence Protocol**:
    *   Upstream has complex context versioning (`context_0`, `history_1`).
    *   Simplified version will have a simpler state management for the REPL.
