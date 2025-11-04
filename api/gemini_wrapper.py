import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("⚠️ GEMINI_API_KEY not set")


def generate_answer(prompt: str):
    """Generate text using Gemini 2.5 family."""
    if not API_KEY:
        return "⚠️ GEMINI_API_KEY not set in environment."

    for model_name in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"]:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if hasattr(response, "text") and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"⚠️ Model {model_name} failed: {e}")
            continue

    return "❌ Gemini failed to generate a response."
