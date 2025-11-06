from dotenv import load_dotenv
import json
import os
import re
from openai import OpenAI
from src.config import SECRET_DETECTION_PROMPT, MODEL

load_dotenv() 

def get_llm_analysis(snippet: str, commit_message: str, file_path: str) -> dict | None:
    client = get_openai_client()
    if not client:
        return None

    prompt = SECRET_DETECTION_PROMPT.format(
        file_path=file_path,
        commit_message=commit_message,
        snippet=snippet
    )
    raw_response = call_llm(client, prompt)
    if not raw_response:
        return None

    analysis = parse_llm_json(raw_response)
    if analysis and analysis.get("is_secret"):
        return analysis

    return None
    
def get_openai_client() -> OpenAI | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set. Skipping LLM analysis.")
        return None
    return OpenAI(api_key=api_key)

def call_llm(client: OpenAI, prompt: str) -> str | None:
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a security assistant that provides analysis in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )
        if not response or not response.choices:
            return None
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI call failed: {e}")
        return None

def parse_llm_json(raw: str) -> dict | None:
    cleaned = clean_llm_json_response(raw)
    try:
        return json.loads(cleaned)
    except Exception:
        print(f"Failed to parse JSON from model:\n---\n{cleaned}\n---")
        return None

def clean_llm_json_response(raw_string: str) -> str:
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

