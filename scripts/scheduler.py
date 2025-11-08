# scripts/scheduler.py
from .config import Settings
from . import content_plan, gemini_client, render_post, wordpress_client
from .fetch_offers import build_offers

def run(dry_run: bool | None = None):
    # 設定を読み込む
    cfg = Settings()

    # 引数でdry_runが指定されてなければ、環境変数のほうを使う
    if dry_run is None:
        dry_run = cfg.dry_run

    # 本番のときだけ必須チェックを厳しくする
    cfg.validate(strict=not dry_run)

    # 1) キーワード・見出しなどのプランを決める
    #    元のコードが plan = content_plan.pick_topic() だったのでそのまま踏襲
    plan = content_plan.pick_topic()

    # 例: 「光回線の選び方と比較」みたいなタイトルを作る
    title = f"{plan['keyword']}の選び方と比較"

    # 2) Geminiで本文パートを生成
    #    gemini_client 側で cfg.gemini_api_key / cfg.gemini_model を読む想定
    sections = gemini_client.generate_article(plan, plan["headings"])

    # 3) 紹介する案件をCSVなどから組み立てる
    offers = build_offers(plan["keyword"])

    # 4) HTMLとして組み立て（ここで WP のURL を渡してる元コードに合わせてる）
    html = render_post.render_article(
        title,
        plan["lede"],
        plan["headings"],
        sections,
        offers,
        cfg.wp_base_url,
    )

    # 5) 実投稿 or ドライラン表示
    if dry_run:
        print("[DRY_RUN] title:", title)
        print("[DRY_RUN] post to:", cfg.wp_base_url)
        print("[DRY_RUN] offers:", offers)
        print("[DRY_RUN] html preview:\n", html[:500])
        return

    # 実際にWordPressにPOSTする
    res = wordpress_client.create_post(title, html, status="publish")
    print("Published:", res.get("link", ""))


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("scheduler", nargs="?", help="for compatibility")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
