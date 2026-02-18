"""
List all available Gemini models to find the correct embedding model
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY not found")
    exit(1)

genai.configure(api_key=api_key)

print("\n" + "="*60)
print("📋 Available Gemini Models")
print("="*60 + "\n")

print("EMBEDDING MODELS:")
print("-" * 60)
for model in genai.list_models():
    if 'embedding' in model.name.lower():
        print(f"✓ {model.name}")
        print(f"  Supported methods: {model.supported_generation_methods}")
        print()

print("\nGENERATIVE MODELS (for LLM):")
print("-" * 60)
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        if 'gemini' in model.name.lower() and 'embedding' not in model.name.lower():
            print(f"✓ {model.name}")