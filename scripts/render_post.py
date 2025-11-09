# scripts/render_post.py

from __future__ import annotations
from typing import List, Dict
import html


def _render_offers(offers: List[Dict[str, str]]) -> str:
    """A8の手動CSVから渡ってきたオファーをいい感じのカードにする"""
    if not offers:
        return ""

    blocks: List[str] = []
    blocks.append('<h2>おすすめサービス・商品</h2>')

    for offer in offers:
        name = offer.get("name") or "おすすめ案件"
        url = offer.get("url") or "#"
        note = offer.get("note") or ""

        # XSS/文字化け防止でnameとnoteだけはescapeしておく
        name_esc = html.escape(name)
        note_esc = html.escape(note)

        blocks.append(
            f"""
<div class="offer-box" style="border:1px solid #ddd;padding:1rem;margin:1rem 0;border-radius:0.5rem;">
  <h3 style="margin-top:0;">{name_esc}</h3>
  {"<p style='color:#666;margin:.4rem 0 .8rem 0;'>" + note_esc + "</p>" if note_esc else ""}
  <p style="margin:0;">
    <a href="{url}" rel="nofollow noopener" target="_blank" style="display:inline-block;background:#0073aa;color:#fff;padding:.5rem 1rem;border-radius:9999px;text-decoration:none;">
      ▶ 詳しくみる
    </a>
  </p>
</div>
""".strip()
        )

    return "\n".join(blocks)


def render_article(
    title: str,
    lede: str,
    headings: List[str],
    sections: List[str],
    offers: List[Dict[str, str]],
    site_url: str = "",
) -> str:
    """本文＋見出し＋A8のおすすめの順でHTMLを組み立てる"""

    html_parts: List[str] = []

    # タイトル・リード
    html_parts.append(f"<h1>{html.escape(title)}</h1>")
    if lede:
        html_parts.append(f"<p>{html.escape(lede)}</p>")

    # 本文セクション
    for h, body in zip(headings, sections):
        html_parts.append(f"<h2>{html.escape(h)}</h2>")
        # body は Gemini が返したHTMLをそのまま載せる想定なのでエスケープしない
        html_parts.append(body)

    # A8おすすめ
    html_parts.append(_render_offers(offers))

    return "\n".join(html_parts)
