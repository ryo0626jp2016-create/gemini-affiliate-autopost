def render_article(title, lede, headings, sections, offers, wp_base_url2):
    html = [f"<h1>{title}</h1>", f"<p>{lede}</p>"]
    for h, s in zip(headings, sections):
        html.append(f"<h2>{h}</h2>")
        html.append(f"<p>{s}</p>")

    # A8オファー紹介を追加
    from .gemini_client import generate_offer_sections
    html.append("<h2>おすすめサービス・商品</h2>")
    html.append(generate_offer_sections(offers))

    return "\n".join(html)
