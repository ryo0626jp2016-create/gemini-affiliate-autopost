# scripts/gemini_client.py
from __future__ import annotations

import json
from typing import List, Dict
import google.generativeai as genai

from .config import Settings

SYSTEM_PROMPT = """あなたは日本語のブログ記事を書くアシスタントです。
- 出力は日本語です。
- 余計な前置きや「承知しました」は不要です。
- 見出しごとに200〜400字くらいで書いてください。
- 本文はHTMLの<p>...</p>を基本にしてください。
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
        # ```json ... ``` みたいなのを剥がす
        lines = text.splitlines()
        # 先頭の ```xxx を外す
        if lines:
            lines = lines[1:]
        # 末尾の ``` を外す
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

次の見出しごとに本文を作成してください:

{heading_lines}

出力は必ず次のJSONフォーマットだけにしてください。説明文は入れないでください。

{{
  "sections": [
    {{"body": "<p>本文...</p>"}}
  ]
}}
"""

    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()
    text = _strip_code_fence(text)

    bodies: List[str] = []

    # 1) JSONとして読めたらそれを使う
    try:
        data = json.loads(text)
        sections = data.get("sections", [])
        for idx, h in enumerate(headings):
            if idx < len(sections):
                body = (sections[idx].get("body") or "").strip()
            else:
                body = ""
            if "<p" not in body:
                body = f"<p>{body or f'この記事では「{h}」について解説します。'}</p>"
            bodies.append(body)
        return bodies
    except Exception:
        # JSONじゃなかったらそのままテキストを分割
        pass

    # 2) 段落で分割して対応
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    for idx, h in enumerate(headings):
        if idx < len(parts):
            body = parts[idx]
        else:
            body = f"{h}についてのポイントをわかりやすくまとめます。"
        if "<p" not in body:
            body = f"<p>{body}</p>"
        bodies.append(body)

    return bodies
