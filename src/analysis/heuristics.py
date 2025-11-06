from src.config import SECRET_REGEXES, ENTROPY_THRESHOLD
from src.utils import calculate_shannon_entropy
import re

def check_line_with_heuristics(line):
    for finding_type, info in SECRET_REGEXES.items():
        if re.search(info["regex"], line):
            is_strong = info["strength"] == "strong"
            return {
                "finding_type": f"Heuristic: {finding_type}",
                "rationale": f"Matched regex for {finding_type}",
                "confidence": "High" if is_strong else "Medium",
                "requires_llm_check": not is_strong  # only weak patterns go to LLM
            }

    if calculate_shannon_entropy(line) > ENTROPY_THRESHOLD:
        return {
            "finding_type": "High Entropy String",
            "rationale": "High Shannon entropy suggests a potential secret.",
            "confidence": "Low",
            "requires_llm_check": True
        }
    return None
