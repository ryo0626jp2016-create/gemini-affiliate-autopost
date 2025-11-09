# scripts/render_post.py
from __future__ import annotations

from typing import List, Dict
import html


def render_article(
    title: str,
    lede: str,
    headings: List[str],
    sections: List[str],
    offers: List[Dict[str, str]],
    wp_base_url2: str = "",
) -> str:
    parts: List[str] = []

    # サムネ用に1枚入れておく（テーマが最初の画像を拾う前提）
    hero_src = "https://placehold.jp/1200x630.png?text=" + html.escape(title)
    parts.append(f'<figure class="post-hero"><img src="{hero_src}" alt="{html.escape(title)}"></figure>')

    parts.append(f"<h1>{html.escape(title)}</h1>")

    if lede:
        parts.append(f"<p>{html.escape(lede)}</p>")

    for h, body in zip(headings, sections):
        parts.append(f"<h2>{html.escape(h)}</h2>")
        # body は Gemini が返したHTMLをそのまま入れる
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
            parts.append(
                f'<p><a class="offer-btn" href="{safe_url}" target="_blank" rel="nofollow noopener">▶ 詳しくみる</a></p>'
            )
            parts.append("</div>")

    return "\n".join(parts)
