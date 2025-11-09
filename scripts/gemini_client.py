# scripts/gemini_client.py
from __future__ import annotations

import json
from typing import List, Dict
import google.generativeai as genai

from .config import Settings

SYSTEM_PROMPT = """あなたは日本語のブログ記事を書くアシスタントです。
- 出力は日本語です。
- 余計な前置きや「承知しました」などは書かないでください。
- 見出しごとに200〜400字くらいの本文を書いてください。
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

    # 予備: list_modelsから1個拾う
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

出力は必ず次のJSONだけにしてください。説明文は入れないでください。

{{
  "sections": [
    {{"body": "<p>本文...</p>"}}
  ]
}}

条件:
- sections の要素数は見出しの数と同じにする
- body はHTMLとして成立させる
- 不要な挨拶や前置きは書かない
"""

    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    # 1) JSONとして読めた場合
    bodies: List[str] = []
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
        # ちゃんと戻せたらここで終了
        return bodies
    except Exception:
        # JSONじゃなかったときは次の保険へ
        pass

    # 2) 段落分割でがんばる
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    for idx, h in enumerate(headings):
        if idx < len(parts):
            body = parts[idx]
        else:
            body = f"{h}についてのポイントをわかりやすくまとめます。"
        if "<p" not in body:
            body = f"<p>{body}</p>"
        bodies.append(body)

    # 3) まだスカスカならテンプレで埋める
    if len("".join(bodies)) < 80:
        bodies = []
        for h in headings:
            body = (
                f"<p>{h}の概要・メリット・注意点を初心者向けに説明してください。"
                f"箇条書きが必要なら<ul><li>...</li></ul>を使ってください。</p>"
            )
            bodies.append(body)

    return bodies
