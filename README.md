# Git Secret Scanner

An LLM-powered tool to scan Git repositories for hardcoded secrets (API keys, passwords, tokens, private keys, etc.) by analyzing commit diffs and messages. It uses a combination of **heuristic patterns** and **LLM verification**.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ana-rosu/git-scanner-for-exposed-secrets.git
cd git-scanner-for-exposed-secrets
```

2. Create a virtual environment and install dependencies:

```
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

3. Set your OpenAI API key in .env:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

```
Options:
--repo: Path to local git repository or URL for remote repository (required)
--n: Number of recent commits to scan. (default: 10)
--verbose: Print detailed logs.
--ignore-files: List of files to skip (comma-separated).
--ignore-llms: Skip LLM verification and use only heuristics.
```

Example usage:

```
python cli.py --repo /path/to/repo --n 10 --v
```

The scan produces a JSON report including:

- scan_metadata (repository info, commits scanned, scan date)
- list of findings

A finding includes:

- commit_hash
- file_path
- snippet
- finding_type
- confidence
- rationale
