# scripts/render_post.py
from __future__ import annotations

from typing import List, Dict
import html
import urllib.parse

def render_article(
    title: str,
    lede: str,
    headings: List[str],
    sections: List[str],
    offers: List[Dict[str, str]],
    wp_base_url2: str = "",
) -> str:
    parts: List[str] = []

    # ★改善点: 画像を「文字画像」から「AI生成イラスト」に変更
    # Pollinations AI を使用 (登録不要・無料)
    # プロンプトを英語風に変換してURLに埋め込む
    safe_title = urllib.parse.quote(title)
    # 日本語プロンプトでも動きますが、念のため 'illustration', 'blog header' などの指示を追加
    image_prompt = f"illustration of {safe_title}, bright style, high quality"
    hero_src = f"https://image.pollinations.ai/prompt/{image_prompt}?width=1200&height=630&nologo=true"

    parts.append(f'<figure class="post-hero"><img src="{hero_src}" alt="{html.escape(title)}"></figure>')

    parts.append(f"<h1>{html.escape(title)}</h1>")

    if lede:
        parts.append(f"<p>{html.escape(lede)}</p>")

    for h, body in zip(headings, sections):
        parts.append(f"<h2>{html.escape(h)}</h2>")
        # body は Gemini が返したHTML(表やリスト含む)をそのまま入れる
        parts.append(body)

    if offers:
        parts.append("<h2>おすすめサービス・商品</h2>")
        for off in offers:
            name = off.get("name") or "おすすめサービス"
            url = off.get("url") or "#"
            note = off.get("note") or ""

            # クエリが消えないようにHTMLエスケープ
            safe_url = html.escape(url, quote=True)

            parts.append('<div class="offer-box">')
            parts.append(f"<h3>{html.escape(name)}</h3>")
            if note:
                parts.append(f"<p>{html.escape(note)}</p>")
            
            # ボタンのデザイン用クラスはCSSで装飾推奨
            parts.append(
                f'<p><a class="offer-btn" href="{safe_url}" target="_blank" rel="nofollow noopener">▶ 公式サイトで詳しく見る</a></p>'
            )
            parts.append("</div>")

    return "\n".join(parts)
