import re

def find_code_blocks(text: str) -> list[str]:
    """
    Find REPL code blocks in text wrapped in triple backticks.
    Looks for ```repl ... ``` blocks.
    """
    # Relaxed pattern to allow various spacing
    pattern = r"```repl\s+(.+?)```"
    results = []
    for match in re.finditer(pattern, text, re.DOTALL):
        results.append(match.group(1).strip())
    return results

def find_final_answer(text: str, env=None) -> str | None:
    """
    Find FINAL(...) or FINAL_VAR(...) statement in response.
    """
    # Check for FINAL_VAR pattern
    final_var_pattern = r"FINAL_VAR\((.*?)\)"
    match = re.search(final_var_pattern, text, re.DOTALL)
    if match and env:
        var_name = match.group(1).strip().strip('"').strip("'")
        # Execute code to get the variable value
        # Pass variable name directly so it is evaluated
        result = env.execute(f"print(FINAL_VAR({var_name}))")
        return result['stdout'].strip() or result['stderr'].strip()

    # Check for FINAL pattern
    final_pattern = r"FINAL\((.*?)\)"
    match = re.search(final_pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return None

def format_execution_result(result: dict, max_length: int = 5000) -> str:
    """
    Format the execution result for the prompt history.
    """
    parts = []
    if result['stdout']:
        parts.append(f"STDOUT:\n{result['stdout']}")
    if result['stderr']:
        parts.append(f"STDERR:\n{result['stderr']}")

    # Add important locals if present? Maybe simpler to just skip for now to reduce noise
    # unless strictly necessary. The original code does filter and show them.

    full_output = "\n\n".join(parts) if parts else "No output"

    if len(full_output) > max_length:
        full_output = full_output[:max_length] + f"... [truncated, total {len(full_output)} chars]"

    return full_output
