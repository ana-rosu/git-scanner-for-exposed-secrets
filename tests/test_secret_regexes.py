import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import re
from config import SECRET_REGEXES

def test_api_key_regex():
    line = "api_key = 'ABCDEFGHIJKLMNOPQRSTUVWX'"
    assert re.search(SECRET_REGEXES["api_key"]["regex"], line)

def test_aws_access_key_regex():
    line = "AKIAABCDEFGHIJKLMNOP"
    assert re.search(SECRET_REGEXES["aws_access_key"]["regex"], line)

def test_aws_secret_key_regex():
    line = "aws_secret = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'"
    assert re.search(SECRET_REGEXES["aws_secret_key"]["regex"], line)

def test_private_key_regex():
    line = "-----BEGIN PRIVATE KEY-----"
    assert re.search(SECRET_REGEXES["private_key"]["regex"], line)

def test_github_token_regex():
    line = "ghp_abcdefghijklmnopqrstuvwxyz0123456789AB"
    assert re.search(SECRET_REGEXES["github_token"]["regex"], line)

def test_slack_token_regex():
    line = "xoxb-123456789012-123456789012-123456789012-abcdefghijklmnopqrstuvwxyz012345"
    assert re.search(SECRET_REGEXES["slack_token"]["regex"], line)

def test_google_api_key_regex():
    line = "AIzaSyA-abcdefghijklmnopqrstuvwxzy012345"
    assert re.search(SECRET_REGEXES["google_api_key"]["regex"], line)

def test_jwt_regex():
    line = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    assert re.search(SECRET_REGEXES["jwt"]["regex"], line)

def test_stripe_live_secret_regex():
    line = "sk_live_abcdefghijklmnopqrstuvwxyz0123"
    assert re.search(SECRET_REGEXES["stripe_live_secret"]["regex"], line)

def test_stripe_test_secret_regex():
    line = "sk_test_abcdefghijklmnopqrstuvwxyz0123"
    assert re.search(SECRET_REGEXES["stripe_test_secret"]["regex"], line)