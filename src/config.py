ENTROPY_THRESHOLD = 4.5

# ! Common secret patterns, this is not an exhaustive list.
SECRET_REGEXES = {
    "api_key": r'(?i)(api_key|api-key|apikey|secret_key|secret-key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
    "aws_access_key": r'AKIA[0-9A-Z]{16}',
    "private_key": r'-----BEGIN ((RSA|OPENSSH|EC|PGP) )?PRIVATE KEY-----',
    "github_token": r'ghp_[a-zA-Z0-9]{36}',
    "slack_token": r'xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}',
}

SECRET_DETECTION_PROMPT="""
    You are a security expert specialized in detecting hardcoded secrets in code.
    Analyze the following code snippet and commit message to determine if a secret is present.

    **File Path:** {file_path}
    **Commit Message:** "{commit_message}"
    **Code Snippet:**
    ```
    {snippet}
    ```

    **Analysis Task:**
    1.  **Identify Potential Secrets:** Look for API keys, passwords, tokens, etc.
    2.  **Contextual Evaluation:** Determine if this is a real secret or just a placeholder, example, or test data.
    3.  **Provide a JSON response with the following structure:**
        - "is_secret": boolean (true if a secret is found, otherwise false)
        - "finding_type": string (e.g., "API Key", "Password", "Private Key")
        - "rationale": string (a brief explanation for your conclusion)
        - "confidence": string ("High", "Medium", or "Low")

    **Respond ONLY with the JSON object.**
    """