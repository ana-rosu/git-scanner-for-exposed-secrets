# Params
MODEL = "gpt-3.5-turbo"
NUMBER_OF_CONTEXT_LINES = 2
ENTROPY_THRESHOLD = 4.5

# Strong Secret Regex Patterns (automatic findings)
STRONG_PATTERNS = {
    "private_key": r"-----BEGIN ((RSA|OPENSSH|EC|PGP) )?PRIVATE KEY-----",
    "github_token": r"ghp_[a-zA-Z0-9]{36}",
    "stripe_live_secret": r"sk_live_[0-9a-zA-Z]{24,}",
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
}

# Weak Patterns (require LLM confirmation)
WEAK_PATTERNS = {
    "api_key": r"(?i)(api_key|api-key|apikey|secret_key|secret-key|secretkey)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
    "aws_secret_key": r"(?i)aws(.{0,20})?(secret|access)[\s:=]+['\"]?([A-Za-z0-9/+=]{40})['\"]?",
    "slack_token": r"xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}",
    "bearer_token": r"(?i)bearer\s+[A-Za-z0-9\-\._~\+\/]+=*",
    "jwt": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
    "google_api_key": r"AIza[0-9A-Za-z\-_]{35}",
    "stripe_test_secret": r"sk_test_[0-9a-zA-Z]{24,}",
}

# Combined lookup table
SECRET_REGEXES = {
    **{k: {"regex": v, "strength": "strong"} for k, v in STRONG_PATTERNS.items()},
    **{k: {"regex": v, "strength": "weak"} for k, v in WEAK_PATTERNS.items()},
}

# LLM Prompt
SECRET_DETECTION_PROMPT="""
    You are a security expert specialized in detecting **hardcoded secrets** in code.
    Analyze the following code snippet and commit message to determine if a **real, hardcoded secret** is present, not just a variable name suggesting one. 

    **Rules:**
    1. Flag only **real, hardcoded secrets** assigned in code:
        - API keys, passwords, tokens, private keys, etc.
        - Example: `"sk_live_ABC123..."`, `"AKIA..."`, `"-----BEGIN PRIVATE KEY-----"`.
    2. Do NOT flag:
        - Regex patterns that *match* secrets (e.g., r"sk_live_[0-9a-zA-Z]{{24,}}")
        - Placeholder/example values (e.g., "YOUR_API_KEY_HERE", "example", "test")
        - References to environment variables (e.g., process.env.*, os.environ.*, getenv)
        - Comments, docs, or config schemas
    3. If it is unclear whether the value is real or example, choose confidence "Low".

    **Output JSON format:**
    {{
        "is_secret": boolean,
        "finding_type": string,   # e.g., "API Key", "Password", "Private Key"
        "rationale": string,      # brief explanation
        "confidence": "High" | "Medium" | "Low"
    }}

    **File Path:** {file_path}
    **Commit Message:** "{commit_message}"
    **Code Snippet:**
    ```
    {snippet}
    ```

    **Respond ONLY with the JSON object.**
"""