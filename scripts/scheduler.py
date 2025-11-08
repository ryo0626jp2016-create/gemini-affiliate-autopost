# scripts/scheduler.py
from __future__ import annotations

from .config import Settings
from . import content_plan, gemini_client, render_post, wordpress_client
from .fetch_offers import build_offers


def run(dry_run: bool = False) -> None:
    cfg = Settings()
    # 本番なら環境変数チェック
    cfg.validate(strict=not dry_run)

    # 1. 記事の題材を決める（content_plan.py 側でCSVから選ぶ想定）
    plan = content_plan.pick_topic()
    # 例：plan = {"keyword": "光回線", "lede": "今回は～", "headings": [...]}

    title = f"{plan['keyword']}の選び方と比較"

    # 2. Geminiで本文を作る
    sections = gemini_client.generate_article(plan, plan["headings"])

    # 3. A8のオファーをキーワードから取得
    offers = build_offers(plan["keyword"])

    # 4. HTMLにまとめる
    html = render_post.render_article(
        title,
        plan["lede"],
        plan["headings"],
        sections,
        offers,
        cfg.wp_base_url2,
    )

    if dry_run:
        print(title)
        print("---- HTML preview ----")
        print(html[:800])
        return

    # 5. WPに投稿
    res = wordpress_client.create_post(title, html, status="publish")
    print("Published:", res.get("link", ""))


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("scheduler", nargs="?")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
