import re

def parse_code_blocks(text: str) -> list[str]:
    """
    Extracts Python code blocks from the text.
    Looks for ```python ... ``` or just ``` ... ```.
    """
    pattern = r"```(?:python)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches
