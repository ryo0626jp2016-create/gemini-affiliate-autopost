# scripts/render_post.py
from __future__ import annotations
from typing import List, Dict


def render_article(
    title: str,
    lede: str,
    headings: List[str],
    sections: List[str],
    offers: List[Dict[str, str]],
    base_url: str = "",
) -> str:
    """記事＋オファーをHTML文字列にする"""

    parts: List[str] = []
    parts.append(f"<h1>{title}</h1>")
    if lede:
        parts.append(f"<p>{lede}</p>")

    # 本文セクション
    for h, body in zip(headings, sections):
        parts.append(f"<h2>{h}</h2>")
        parts.append(f"<p>{body}</p>")

    # A8オファー
    if offers:
        parts.append("<h2>おすすめサービス・商品</h2>")
        for o in offers:
            parts.append(
                f"""
<div class="offer-box" style="border:1px solid #ddd;padding:12px;margin:10px 0;">
  <strong>{o.get('name','おすすめリンク')}</strong><br>
  <p>{o.get('note','')}</p>
  <a href="{o['url']}" target="_blank" rel="nofollow noopener">▶ 詳しくみる</a>
</div>
""".strip()
            )

    # 免責
    parts.append('<p style="font-size:0.9em;color:#666;">※本記事にはアフィリエイトリンクが含まれます。</p>')

    return "\n".join(parts)
