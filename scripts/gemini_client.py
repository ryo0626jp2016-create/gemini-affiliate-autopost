# scripts/gemini_client.py
from __future__ import annotations

import json
from typing import List, Dict
import google.generativeai as genai

from .config import Settings

# ★改善点: プロンプトを強化して、読みやすい構成（表・箇条書き・強調）を指示
SYSTEM_PROMPT = """あなたはプロのWebライターです。
読者の悩みを解決する、わかりやすく魅力的な日本語のブログ記事を書いてください。

【執筆ルール】
- 出力は日本語です。
- 余計な前置き（「承知しました」など）は一切不要です。
- 専門用語には簡単な解説を添えてください。
- 重要なキーワードやメリットは **太字** で強調してください。
- 比較やスペック説明の際は、必ずHTMLの <table> (表) を使って見やすく整理してください。
- 手順やポイントは <ul> または <ol> のリスト形式を使ってください。
- 見出しごとに300〜500文字程度で、具体的かつ論理的に書いてください。
- 本文はHTML形式（<p>, <table>, <ul>, <li>, <strong> 等）で出力してください。
"""

def _init_model() -> genai.GenerativeModel:
    cfg = Settings()
    genai.configure(api_key=cfg.gemini_api_key)

    candidates: List[str] = []
    raw = (cfg.gemini_model or "").strip()
    if raw:
        if raw.startswith("models/"):
            candidates.append(raw)
        else:
            candidates.append(f"models/{raw}")

    # バックアップで1つ拾う
    try:
        for m in genai.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                candidates.append(m.name)
                break
    except Exception:
        pass

    last_exc = None
    for name in candidates:
        try:
            return genai.GenerativeModel(name)
        except Exception as e:
            last_exc = e
    if last_exc:
        raise last_exc
    raise RuntimeError("Gemini model could not be initialized")


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def generate_article(plan: Dict, headings: List[str]) -> List[str]:
    """
    return: 見出しと同じ長さの「本文HTML文字列」のリスト
    """
    model = _init_model()

    heading_lines = "\n".join(f"- {h}" for h in headings)

    prompt = f"""{SYSTEM_PROMPT}

記事のテーマ: {plan.get("keyword")}

以下の見出し構成で記事の本文を作成してください:

{heading_lines}

出力は必ず以下のJSONフォーマットのみにしてください。説明文は不要です。

{{
  "sections": [
    {{"body": "<p>ここに本文...</p><ul><li>リスト...</li></ul>"}}
  ]
}}
"""

    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()
    text = _strip_code_fence(text)

    bodies: List[str] = []

    # 1) JSONとしてパース
    try:
        data = json.loads(text)
        sections = data.get("sections", [])
        for idx, h in enumerate(headings):
            if idx < len(sections):
                body = (sections[idx].get("body") or "").strip()
            else:
                body = ""
            # 空の場合はフォールバック
            if not body:
                 body = f"<p>{h}について解説します。</p>"
            # 万が一 <p> 等が含まれていなければ囲む（簡易チェック）
            if "<p" not in body and "<table" not in body and "<ul" not in body:
                body = f"<p>{body}</p>"
            bodies.append(body)
        return bodies
    except Exception:
        pass

    # 2) JSON失敗時は改行分割で対応
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    for idx, h in enumerate(headings):
        if idx < len(parts):
            body = parts[idx]
        else:
            body = f"{h}についてのポイントをまとめます。"
        
        if "<p" not in body and "<table" not in body and "<ul" not in body:
            body = f"<p>{body}</p>"
        bodies.append(body)

    return bodies
