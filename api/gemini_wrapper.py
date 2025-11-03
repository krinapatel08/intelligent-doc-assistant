import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def generate_answer(prompt: str, model: str = "models/text-bison-001", max_output_tokens: int = 512):
    if not API_KEY:
        return "GEMINI_API_KEY not set."
    try:
        # Some versions use genai.generate_text; adapt if needed
        resp = genai.generate_text(model=model, input=prompt, max_output_tokens=max_output_tokens)
        # Many wrappers have resp.text
        if hasattr(resp, "text"):
            return resp.text
        # fallback for dict-like
        if isinstance(resp, dict):
            return resp.get("candidates", [{}])[0].get("content") or resp.get("text","")
        return str(resp)
    except Exception as e:
        return f"Error from gemini: {e}"
