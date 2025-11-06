import os
import re
import stat
import math

def handle_rm_error(func, path, _):
    """
    Error handler for shutil.rmtree that handles read-only files.
    """
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def clean_llm_json_response(raw_string: str) -> str:
    """
    Cleans the raw string response from an LLM to extract the JSON object.
    It handles cases where the JSON is wrapped in Markdown code blocks.
    """
    if not isinstance(raw_string, str):
        return None

    # Use regex to find the JSON block between ``` and ``` or just { and }
    match = re.search(r'\{.*\}', raw_string, re.DOTALL)
    
    if match:
        return match.group(0)
    else:
        # Return the original string if no JSON object is found,
        # allowing the parser to fail and log the problematic string.
        return raw_string
    
def calculate_shannon_entropy(data):
    if not data:
        return 0
    
    entropy = 0
    for char in set(data):
        freq = float(data.count(char)) / len(data)
        entropy -= freq * math.log(freq, 2)
    return entropy