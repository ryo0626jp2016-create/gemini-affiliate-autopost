import google.generativeai as genai
from .config import Settings

cfg = Settings()
genai.configure(api_key=cfg.gemini_api_key)
model = genai.GenerativeModel(cfg.gemini_model)

SYSTEM = """あなたはアフィリエイト記事を自動生成する日本語ライターAIです。
SEOを意識し、自然な見出し・紹介文・本文を作成してください。"""

def generate_article(plan, headings):
    """Geminiで本文生成"""
    prompt = f"""
    テーマ: {plan['keyword']}
    導入文: {plan['lede']}
    見出し構成: {headings}
    上記の情報をもとに、SEOを意識した2000〜3000字の記事本文を自然な日本語で生成してください。
    """
    resp = model.generate_content([SYSTEM, prompt])
    return resp.text

def generate_offer_sections(offers: list[dict]) -> str:
    """A8オファー紹介を自然に整形"""
    results = []
    for offer in offers:
        prompt = f"""
        以下のサービスをブログ記事内で自然に紹介する短い見出しと紹介文を作成してください。
        - サービス名: {offer['name']}
        - カテゴリ: {offer['note']}
        出力形式:
        ## {offer['name']}
        （50〜80文字の紹介文。読者がクリックしたくなる自然な文体で）
        最後に「▶ 詳しくみる」リンクを添えてください。
        """
        try:
            res = model.generate_content(prompt)
            text = res.text.strip()
        except Exception:
            text = f"## {offer['name']}\nおすすめの{offer['note']}関連サービスです。\n▶ [詳しくみる]({offer['url']})"
        # URLを挿入
        text = text.replace("▶ 詳しくみる", f"▶ [詳しくみる]({offer['url']})")
        results.append(text)
    return "\n\n".join(results)
