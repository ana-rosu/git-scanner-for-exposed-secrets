from src.config import SECRET_REGEXES, ENTROPY_THRESHOLD
from src.utils import calculate_shannon_entropy
import re

def check_line_with_heuristics(line):
    for finding_type, regex in SECRET_REGEXES.items():
        if re.search(regex, line):
            return {
                "finding_type": f"Heuristic: {finding_type}",
                "rationale": f"Matched regex for {finding_type}",
                "confidence": "Medium",
                "requires_llm_check": False
            }

    if calculate_shannon_entropy(line) > ENTROPY_THRESHOLD:
        return {
            "finding_type": "High Entropy String",
            "rationale": "High Shannon entropy suggests a potential secret.",
            "confidence": "Low",
            "requires_llm_check": True
        }
    return None
