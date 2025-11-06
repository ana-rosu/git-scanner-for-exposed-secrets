import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.analysis.llm_analyzer import get_llm_analysis

def assert_not_secret(snippet):
    result = get_llm_analysis(snippet, commit_message="", file_path="")
    assert result is None or result.get("is_secret") is False, f"False positive on:\n{snippet}"

def assert_secret(snippet):
    result = get_llm_analysis(snippet, commit_message="", file_path="")
    assert result is not None and result.get("is_secret") is True, f"Missed secret on:\n{snippet}"

def test_env_reference_is_not_secret():
    assert_not_secret('api_key = os.environ["OPENAI_API_KEY"]')
    assert_not_secret('password = process.env.DB_PASSWORD')
    assert_not_secret('token = getenv("SERVICE_TOKEN")')

def test_variable_name_only_is_not_secret():
    assert_not_secret('api_key = "my_api_key"')  
    assert_not_secret('password = "password"')  
    assert_not_secret('TOKEN = "example-token"') 

def test_regex_pattern_is_not_secret():
    assert_not_secret(r'regex = r"sk_live_[0-9a-zA-Z]{24,}"')
    assert_not_secret(r'regex = r"(?i)(api_key|secret_key)\s*[:=]\s*[a-zA-Z0-9]{20,}"')

def test_documentation_examples_are_not_secret():
    assert_not_secret('# Example: "sk_live_ABC123..."')
    assert_not_secret('""" API Key Example: AKIA... """')

def test_real_secrets_are_detected():
    assert_secret('API_KEY = "sk_live_51JYyYtS5q9aB0Q5aXbYkL9uHq"')
    assert_secret('aws_secret = "AKIAIOSFODNN7EXAMPLE"')
    assert_secret('private = "-----BEGIN PRIVATE KEY-----\\nMIIEv..."')
