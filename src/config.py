NUMBER_OF_CONTEXT_LINES = 2

ENTROPY_THRESHOLD = 4.5

SECRET_REGEXES = {
    # Strong patterns (can be flagged directly)
    "private_key": {
        "regex": r"-----BEGIN ((RSA|OPENSSH|EC|PGP) )?PRIVATE KEY-----",
        "strength": "strong"
    },
    "github_token": {
        "regex": r"ghp_[a-zA-Z0-9]{36}",
        "strength": "strong"
    },
    "stripe_live_secret": {
        "regex": r"sk_live_[0-9a-zA-Z]{24,}",
        "strength": "strong"
    },
    "aws_access_key": {
        "regex": r"AKIA[0-9A-Z]{16}",
        "strength": "strong"
    },

    # Weak patterns (require LLM verification)
    "api_key": {
        "regex": r"(?i)(api_key|api-key|apikey|secret_key|secret-key|secretkey)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
        "strength": "weak"
    },
    "aws_secret_key": {
        "regex": r"(?i)aws(.{0,20})?(secret|access)[\s:=]+['\"]?([A-Za-z0-9/+=]{40})['\"]?",
        "strength": "weak"
    },
    "slack_token": {
        "regex": r"xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}",
        "strength": "weak"
    },
    "bearer_token": {
        "regex": r"(?i)bearer\s+[A-Za-z0-9\-\._~\+\/]+=*",
        "strength": "weak"
    },
    "jwt": {
        "regex": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
        "strength": "weak"
    },
    "google_api_key": {
        "regex": r"AIza[0-9A-Za-z\-_]{35}",
        "strength": "weak"
    },
    "stripe_test_secret": {
        "regex": r"sk_test_[0-9a-zA-Z]{24,}",
        "strength": "weak"
    }
}

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