# Core Logic of Recursive Language Models (RLM)

## First Principles

The core idea of an RLM is to augment an LLM with a REPL (Read-Eval-Print Loop) environment that allows it to:
1.  **Reason**: Generate thought processes and code.
2.  **Act**: Execute the generated code in the environment.
3.  **Recurse**: The environment provides a mechanism for the code to call the LLM itself (or another LLM) to solve sub-problems.
4.  **Observe**: See the results of the code execution and the recursive calls.

This creates a loop: `Prompt -> LLM -> Code -> Execution (with Recursion) -> Observation -> Prompt`.

## Key Components

### 1. The Controller (RLM Class)
The controller manages the lifecycle of a request.
-   **Input**: User prompt, configuration (max depth, max iterations).
-   **State**: Message history, iteration count.
-   **Loop**:
    1.  Construct prompt (System prompt + User prompt + History).
    2.  Call LLM.
    3.  Parse response for code blocks.
    4.  Execute code blocks in the Environment.
    5.  Check for "Final Answer".
    6.  Update history with LLM response and Execution result.
-   **Termination**: Returns final answer or runs out of iterations.

### 2. The Environment (REPL)
The environment is where code execution happens.
-   **Isolation**: Can be local (same process/machine) or isolated (Docker, Cloud Sandbox).
-   **Context**: Can hold variables, imported modules, and data.
-   **Capabilities**:
    -   `execute_code(code)`: Runs the code and captures stdout, stderr, and return values.
    -   **Critical**: Must provide a `llm_query(prompt)` function available in the scope of the executed code. This enables recursion.

### 3. The LLM Handler (Recursion Enabler)
The mechanism that allows the isolated environment to call back to the LLM.
-   **Problem**: The code runs in a sandbox (possibly on another machine), but needs access to the LLM credentials/client which are on the host.
-   **Solution**:
    -   Host starts a Server (e.g., TCP Socket or HTTP).
    -   Environment's `llm_query` sends a request to this Server.
    -   Host receives request, calls LLM, and sends back the response.
-   **Protocol**: Needs a serialization format (JSON) to exchange prompts and responses.

### 4. The LLM Client
Wraps the actual LLM provider (OpenAI, Anthropic, etc.).
-   Standardizes the interface (`completion(prompt) -> response`).
-   Handles API keys and rate limits.

## Simplified Data Flow

1.  **User** sends prompt "Solve X".
2.  **Controller** starts **Server** and **Environment**.
3.  **Controller** prompts **LLM**: "User wants X. You have python tools."
4.  **LLM** responds: "I will write code to solve sub-problem Y. ```python result = llm_query('Solve Y') ```"
5.  **Controller** parses code.
6.  **Controller** calls **Environment.execute_code()**.
7.  **Environment** runs code. Finds `llm_query`.
8.  `llm_query` connects to **Server** and sends "Solve Y".
9.  **Server** calls **LLM** with "Solve Y". **LLM** returns "Answer Y".
10. **Server** sends "Answer Y" back to **Environment**.
11. `result` becomes "Answer Y".
12. **Environment** returns execution result (stdout/locals) to **Controller**.
13. **Controller** updates history and loops.
