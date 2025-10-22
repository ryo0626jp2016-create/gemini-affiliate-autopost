from .config import Settings
from . import content_plan, gemini_client, render_post, wordpress_client
from .fetch_offers import build_offers

def run(dry_run=False):
    cfg=Settings(); cfg.validate(strict=not dry_run)
    plan=content_plan.pick_topic()
    title=f"{plan['keyword']}の選び方と比較"
    sections=gemini_client.generate_article(plan, plan['headings'])
    offers=build_offers(plan['keyword'])
    html=render_post.render_article(title, plan['lede'], plan['headings'], sections, offers, cfg.wp_base_url2)
    if dry_run:
        print(title); print(offers); print(html[:500]); return
    res=wordpress_client.create_post(title, html, status='publish')
    print('Published:', res.get('link',''))

def main():
    import argparse; ap=argparse.ArgumentParser(); ap.add_argument('scheduler', nargs='?'); ap.add_argument('--dry-run', action='store_true'); a=ap.parse_args(); run(dry_run=a.dry_run)
