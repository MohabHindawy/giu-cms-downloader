import requests
from requests_ntlm import HttpNtlmAuth

def get_session(username: str, password: str) -> requests.Session:
    s = requests.Session()
    s.auth = HttpNtlmAuth(username, password)
    return s