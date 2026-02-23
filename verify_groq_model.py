import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/chat/completions"
model = "qwen/qwen3-32b" # The suspect model

print(f"Testing model: {model}")

# Simulation of Architect Payload
system_prompt = """
You are an ELITE Software Architect (Level: Staff Engineer).
Your goal is to generate **PRODUCTION-READY**, **MODERN**, and **BEAUTIFUL** code.
Think like Claude 3.5 Sonnet: Precise, elegant, and highly logical.

### CORE OPERATING RULES:
1. **NO PLACEHOLDERS**: Never say "Add code here". Write the FULL code.
"""

user_prompt = """
PREVIOUS PROJECT CONTEXT:
<file name="index.html">...</file>
<file name="style.css">...</file>

USER REQUEST: Create a flappy bird game website, it should have very good graphics.
"""

print(f"Testing model: {model} with System Prompt & Context")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": model,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    "max_tokens": 8192,
    "temperature": 0.3
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error Body: {response.text}")
    else:
        print("Success! Response received.")
except Exception as e:
    print(f"Error: {e}")
