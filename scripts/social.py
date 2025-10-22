def build_x_post(title,url,offers):
    tail=' / '.join(o['name'] for o in offers[:2])
    return f"{title} | {tail} #アフィリエイト {url}"[:270]
