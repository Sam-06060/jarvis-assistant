import google.generativeai as genai
import os

api_key = "AIzaSyDtVMZPN7msn1wakk7ayklfq9fgqZPvU7A"
genai.configure(api_key=api_key)

print("Listing Available Models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
