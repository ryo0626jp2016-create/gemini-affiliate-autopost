# scripts/gemini_client.py
from __future__ import annotations
from typing import List, Dict
import os
import google.generativeai as genai

# 記事生成のときに毎回書く前提のシステムっぽい指示
SYSTEM = (
    "あなたは日本語ブログの記事を作るアシスタントです。"
    "読みやすく、ですます調で、具体例を入れて書いてください。"
)


def _choose_model_name() -> str:
    """
    1. GEMINI_API_KEY があることを確認
    2. GEMINI_MODEL が指定されていたらそれを使う（なければ list_models から拾う）
    3. どの場合でも先頭に `models/` が付くように正規化する
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY が設定されていません。")

    genai.configure(api_key=api_key)

    # まずは環境変数優先
    env_model = os.getenv("GEMINI_MODEL")
    if env_model:
        m = env_model.strip()
        if not m.startswith("models/"):
            m = "models/" + m
        print("[Gemini] using env model:", m)
        return m

    # 無ければ API から取れるやつを1つ拾う
    models = list(genai.list_models())
    for m in models:
        if "generateContent" in getattr(m, "supported_generation_methods", []):
            print("[Gemini] using discovered model:", m.name)
            return m.name

    raise RuntimeError("generateContent が使える Gemini モデルが見つかりませんでした。")


# 一度決めたモデル名をキャッシュしておく
_MODEL_NAME: str | None = None


def _get_model():
    global _MODEL_NAME
    if _MODEL_NAME is None:
        _MODEL_NAME = _choose_model_name()
    # ここで必ず full name を使う
    return genai.GenerativeModel(_MODEL_NAME)


def generate_article(plan: Dict, headings: List[str]) -> List[str]:
    """
    content_plan.py が作った plan と、
    scheduler.py から渡ってきた見出しリストをもとに本文を作る。
    AIには「### 見出し」で区切ってもらい、あとでパースする。
    """
    model = _get_model()

    keyword = plan.get("keyword", "ブログ")
    lede = plan.get("lede", "")

    # AIに渡すプロンプトを作る
    headings_lines = "\n".join(f"- {h}" for h in headings)
    marker_lines = "\n".join(f"### {h}" for h in headings)

    prompt = f"""
{SYSTEM}

以下の条件で記事本文を出力してください。

# 記事のテーマ
{keyword}

# 導入文の要素
{lede}

# 見出し構成
{headings_lines}

# 出力フォーマット（厳守してください）
{marker_lines}

各見出しの下に、その見出しの説明・手順・ポイントなどを2〜4段落で書いてください。
無駄に長くせず、初心者向けに噛み砕いてください。
"""

    resp = model.generate_content(prompt)
    raw_text = getattr(resp, "text", "") or ""

    # 受け取ったテキストを "### 見出し" ごとに割る
    sections_map: Dict[str, str] = {}
    current_title: str | None = None
    buf: List[str] = []

    for line in raw_text.splitlines():
        if line.startswith("### "):
            # 直前の見出しを保存
            if current_title is not None:
                sections_map[current_title] = "\n".join(buf).strip()
            current_title = line.replace("### ", "").strip()
            buf = []
        else:
            buf.append(line)

    # 最後の見出し分
    if current_title is not None:
        sections_map[current_title] = "\n".join(buf).strip()

    # scheduler 側が渡してきた順で並べる
    sections: List[str] = []
    for h in headings:
        text = sections_map.get(h)
        if not text:
            # もしAIが見出し名を微妙に変えてしまった場合の保険
            text = f"{h}について解説します。"
        sections.append(text)

    return sections
