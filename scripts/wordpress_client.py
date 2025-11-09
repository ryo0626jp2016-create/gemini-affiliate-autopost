# scripts/wordpress_client.py
from __future__ import annotations

import io
import requests
from .config import Settings


def _create_session(cfg: Settings) -> requests.Session:
    s = requests.Session()
    s.auth = (cfg.wp_user, cfg.wp_app_password)
    return s


def _upload_placeholder(sess: requests.Session, base_url: str, title: str) -> int | None:
    """
    ダミーのPNGを作って /media に投げてIDを返す
    """
    # 1200x630 のプレースホルダーをその場でダウンロードして投げる
    ph_url = "https://placehold.jp/1200x630.png"
    try:
        img_resp = requests.get(ph_url, timeout=10)
        img_resp.raise_for_status()
    except Exception:
        return None

    files = {
        "file": ("thumb.png", img_resp.content, "image/png"),
    }
    data = {
        "title": title,
    }
    media_url = f"{base_url}/wp-json/wp/v2/media"
    try:
        r = sess.post(media_url, files=files, data=data, timeout=15)
        r.raise_for_status()
        mid = r.json().get("id")
        return mid
    except Exception:
        return None


def create_post(title: str, content: str, status: str = "draft"):
    cfg = Settings()
    cfg.validate(strict=True)
    sess = _create_session(cfg)

    base = cfg.wp_base_url2.rstrip("/")

    # まず通常のエンドポイントで試す
    post_url = f"{base}/wp-json/wp/v2/posts"
    # あとで featured_media を入れるので、先にメディアを用意しておく
    featured_id = _upload_placeholder(sess, base, title)

    payload = {
        "title": title,
        "content": content,
        "status": status,
    }
    if featured_id:
        payload["featured_media"] = featured_id

    r = sess.post(post_url, json=payload, timeout=15)
    if r.status_code == 404:
        # 旧RESTの形式にフォールバック
        post_url = f"{base}/index.php?rest_route=/wp/v2/posts"
        r = sess.post(post_url, json=payload, timeout=15)

    r.raise_for_status()
    return r.json()
