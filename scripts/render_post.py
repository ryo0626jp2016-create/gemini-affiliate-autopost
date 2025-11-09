from __future__ import annotations
from typing import List, Dict
from jinja2 import Template
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "post_template.html"

def render_article(title: str, lede: str, headings: List[str], sections: List[str],
                   offers: List[Dict[str, str]], wp_base_url: str) -> str:
    if TEMPLATE.exists():
        tpl = Template(TEMPLATE.read_text(encoding="utf-8"))
        return tpl.render(title=title, lede=lede, headings=headings, sections=sections,
                          offers=offers, wp_base_url=wp_base_url)

    # fallback HTML
    html = [f"<h2>{title}</h2>", f"<p>{lede}</p>"]
    for h, s in zip(headings, sections):
        html.append(f"<h3>{h}</h3><p>{s}</p>")

    if offers:
        html.append("<h3>おすすめサービス・商品</h3><div>")
        for o in offers:
            html.append(f"""
            <div style='border:1px solid #ddd;padding:10px;margin:10px 0;border-radius:8px;'>
              <strong>{o.get('title') or o['name']}</strong><br>
              <span style='font-size:90%;color:#666;'>{o.get('note','')}</span><br>
              <a href='{o['url']}' rel='nofollow noopener' target='_blank'
                 style='display:inline-block;margin-top:6px;padding:6px 12px;
                 background:#ff7f50;color:white;border-radius:6px;text-decoration:none;'>
                 ▶ 詳しくみる
              </a>
            </div>
            """)
        html.append("</div>")

    return "\n".join(html)
