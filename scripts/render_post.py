from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

def render_article(title, lede, headings, sections, offers, base_url):
    env=Environment(loader=FileSystemLoader(str(Path(__file__).resolve().parents[1]/'templates')),autoescape=select_autoescape(['html']))
    tpl=env.get_template('post_template.html')
    return tpl.render(title=title, lede=lede, headings=headings, sections=sections, offers=offers)
