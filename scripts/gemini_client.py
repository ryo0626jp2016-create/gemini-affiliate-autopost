from .config import Settings
import google.generativeai as genai

def generate_article(topic, headings):
    s=Settings(); genai.configure(api_key=s.gemini_api_key)
    model=genai.GenerativeModel(s.gemini_model)
    out=[]
    SYSTEM='日本語でSEOフレンドリーに、HTML断片で簡潔に。'
    for h in headings:
        prompt = f"見出し:{h}\n話題:{topic['keyword']}\nHTML断片で。"
        resp=model.generate_content([SYSTEM, prompt])
        out.append({'h2':h,'html':(resp.text or ''),'img':None})
    return out
