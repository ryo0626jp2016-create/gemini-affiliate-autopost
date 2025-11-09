# scripts/gemini_client.py
from __future__ import annotations

import json
from typing import List, Dict
import google.generativeai as genai

from .config import Settings


SYSTEM_PROMPT = """あなたは日本語のブログ記事を書くアシスタントです。
- 出力は日本語です。
- 余計な前置きや「承知しました」「もちろんです」などは書かないでください。
- 見出しごとに200〜400字くらいの記事本文を書いてください。
- 本文は HTML の <p>...</p> を基本にしてください。リストにしたい場合は <ul><li>...</li></ul> を使っても構いません。
"""


def _init_model() -> genai.GenerativeModel:
    """環境変数で指定されたモデルを優先し、ダメなら list_models から1つ拾う。"""
    cfg = Settings()
    genai.configure(api_key=cfg.gemini_api_key)

    candidates: List[str] = []

    # .env / GitHub Secrets で指定してるやつを最優先
    name = (cfg.gemini_model or "").strip()
    if name:
        if name.startswith("models/"):
            candidates.append(name)
        else:
            candidates.append(f"models/{name}")

    # 念のため使えるモデルを1つ拾っておく
    try:
        for m in genai.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                candidates.append(m.name)
                break
    except Exception:
        # list_models が使えない環境でも落ちないように
        pass

    last_exc = None
    for c in candidates:
        try:
            return genai.GenerativeModel(c)
        except Exception as e:
            last_exc = e

    # ここまで全部ダメだったら最後の例外を投げる
    if last_exc:
        raise last_exc
    else:
        raise RuntimeError("Gemini model could not be initialized")


def generate_article(plan: Dict, headings: List[str]) -> List[Dict[str, str]]:
    """
    plan: content_plan.pick_topic() が返した dict を想定
    headings: その記事で使う見出しのリスト
    戻り値: [{ "heading": "...", "body": "<p>...</p>" }, ...]
    """
    model = _init_model()

    # 見出し一覧を文字列に
    heading_lines = "\n".join(f"- {h}" for h in headings)

    # JSONでしか返させないプロンプト
    prompt = f"""{SYSTEM_PROMPT}

記事のテーマ: {plan.get("keyword")}

次の見出しごとに本文を作成してください:

{heading_lines}

出力フォーマットは必ず次の JSON だけにしてください。説明文や前後の文章は書かないでください。

{{
  "sections": [
    {{"heading": "見出しタイトル", "body": "<p>この見出しの本文...</p>"}}
  ]
}}

制約:
- sections の配列は上に渡した見出しと同じ順番・同じ数にしてください
- body は200〜400字を目安にしてください
- body はHTMLとして成立するようにしてください
"""

    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    # -------- 1. JSONとして読めたらそのまま使う --------
    try:
        data = json.loads(text)
        sections = data["sections"]
        # 念のため p タグを保証
        fixed: List[Dict[str, str]] = []
        for i, h in enumerate(headings):
            if i < len(sections):
                body = sections[i].get("body", "").strip()
            else:
                body = ""
            if "<p" not in body:
                body = f"<p>{body or f'この記事では「{h}」について解説します。'}</p>"
            fixed.append({"heading": h, "body": body})
        return fixed
    except Exception:
        # JSONじゃなかったときの保険処理
        pass

    # -------- 2. JSONじゃなかったら素朴に分割して作る --------
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    result: List[Dict[str, str]] = []

    for i, h in enumerate(headings):
        if i < len(parts):
            body = parts[i]
        else:
            body = f"この記事では「{h}」のポイントをわかりやすくまとめます。"
        if "<p" not in body:
            body = f"<p>{body}</p>"
        result.append({"heading": h, "body": body})

    # もしモデルが「はい、承知しました。」だけ返した場合の最終保険
    if len("".join(p["body"] for p in result)) < 80:
        result = []
        for h in headings:
            body = (
                f"<p>{h}について、読者が最初に知りたい『メリット』『注意点』『おすすめの人』を簡潔に書いてください。"
                f"さらに箇条書きでポイントを3つ示してください。</p>"
            )
            result.append({"heading": h, "body": body})

    return result

