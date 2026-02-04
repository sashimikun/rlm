import re

def find_code_blocks(text: str) -> list[str]:
    """
    Extracts python code blocks from the text.
    Looks for ```python ... ``` or just ``` ... ```
    """
    pattern = r"```(?:python)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [m.strip() for m in matches]
