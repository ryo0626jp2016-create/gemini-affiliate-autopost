# scripts/gemini_client.py
from .config import Settings
import google.generativeai as genai
from google.api_core import exceptions as gexc

SYSTEM = "日本語でSEOフレンドリーに、HTML断片で簡潔に。"

def _pick_model(s: Settings) -> str:
    # Secret/環境が空なら既定
    model = (s.gemini_model or "gemini-1.5-pro").strip()
    if model.startswith("models/"):
        model = model.split("/", 1)[1]
    return model

def generate_article(topic, headings):
    s = Settings()
    genai.configure(api_key=s.gemini_api_key)

    model_name = _pick_model(s)
    print(f"[Gemini] trying model: {model_name}")
    model = genai.GenerativeModel(model_name)

    out = []
    for h in headings:
        prompt = f"見出し:{h}\n話題:{topic['keyword']}\nHTML断片で。"
        try:
            resp = model.generate_content([SYSTEM, prompt])
        except gexc.NotFound:
            # proが閉じているプロジェクト対策でflashにフォールバック
            fallback = "gemini-1.5-flash"
            print(f"[Gemini] {model_name} not found -> fallback to {fallback}")
            model = genai.GenerativeModel(fallback)
            resp = model.generate_content([SYSTEM, prompt])
        out.append({"h2": h, "html": (getattr(resp, "text", "") or ""), "img": None})
    return out
