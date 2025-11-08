# scripts/wordpress_client.py
from __future__ import annotations
import os
import requests
from urllib.parse import urlsplit, urlunsplit


def _possible_post_urls(base: str):
    """
    与えられた base (例: https://www.2025blog.com/2024blog) から
    よくあるRESTのパスを何パターンか吐く
    """
    base = base.rstrip("/")

    # 1) まずはそのまま
    yield f"{base}/wp-json/wp/v2/posts"
    # 2) パーマリンクが効いてないとき用
    yield f"{base}/index.php?rest_route=/wp/v2/posts"

    # サブディレクトリだった場合は、ルートも試す
    parts = urlsplit(base)
    # parts.path が "/2024blog" みたいなとき
    if parts.path and parts.path not in ("/", ""):
        root = urlunsplit((parts.scheme, parts.netloc, "", "", ""))
        # ルートにWPがいるパターン
        yield f"{root}/wp-json/wp/v2/posts"
        yield f"{root}/index.php?rest_route=/wp/v2/posts"


def create_post(title: str, content: str, status: str = "publish") -> dict:
    base = (os.getenv("WP_BASE_URL2") or "").rstrip("/")
    user = os.getenv("WP_USER") or ""
    app_pass = os.getenv("WP_APP_PASSWORD") or ""

    if not base or not user or not app_pass:
        raise RuntimeError("WP_BASE_URL2 / WP_USER / WP_APP_PASSWORD が設定されていません")

    auth = (user, app_pass)

    data = {
        "title": title,
        "content": content,
        "status": status,
    }

    last_error = None
    for url in _possible_post_urls(base):
        try:
            print(f"[WP] TRY POST -> {url}")
            r = requests.post(url, auth=auth, json=data, timeout=20)
            if 200 <= r.status_code < 300:
                print("[WP] OK")
                return r.json()
            else:
                print(f"[WP] {r.status_code} {r.text[:200]}")
                last_error = (r.status_code, r.text)
        except Exception as e:
            print(f"[WP] exception on {url}: {e}")
            last_error = e

    # 全部ダメだったら最後のエラーを投げる
    raise RuntimeError(f"WordPress POST failed: {last_error}")
