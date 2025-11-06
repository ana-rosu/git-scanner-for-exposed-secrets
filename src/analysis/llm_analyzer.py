from dotenv import load_dotenv
import json
import os
import openai
from openai import OpenAI
from src.config import SECRET_DETECTION_PROMPT, MODEL
from src.utils import clean_llm_json_response

load_dotenv() 

def get_llm_analysis(snippet: str, commit_message: str, file_path: str) -> dict | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set. Skipping LLM analysis.")
        return None

    client = OpenAI(api_key=api_key)
    prompt = SECRET_DETECTION_PROMPT.format(file_path=file_path, commit_message=commit_message, snippet=snippet)
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
            print("Error calling OpenAI API: Received an empty response or no choices.")
            return None

        raw_response_content = response.choices[0].message.content
        cleaned_json_str = clean_llm_json_response(raw_response_content)
        if not raw_response_content or not cleaned_json_str:
            print("Error calling OpenAI API: Model returned an empty content string.")
            return None

        try:
            analysis = json.loads(cleaned_json_str)
            if analysis.get("is_secret"):
                return analysis
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from LLM response. The model returned:\n---\n{cleaned_json_str}\n---")
            return None

    except openai.APIError as e:
        print(f"An OpenAI API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during LLM analysis: {e}")

    return None
