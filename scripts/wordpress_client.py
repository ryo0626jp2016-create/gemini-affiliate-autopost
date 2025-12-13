# scripts/wordpress_client.py
from __future__ import annotations

import io
import requests
import urllib.parse
from .config import Settings


def _create_session(cfg: Settings) -> requests.Session:
    s = requests.Session()
    s.auth = (cfg.wp_user, cfg.wp_app_password)
    return s


def _upload_ai_image(sess: requests.Session, base_url: str, title: str) -> int | None:
    """
    タイトルからAI画像を生成・ダウンロードしてWPメディアにアップロードしIDを返す
    """
    # AI画像生成のURLを作成 (Pollinations AI)
    safe_title = urllib.parse.quote(title)
    prompt = f"illustration of {safe_title}, bright style, high quality, digital art"
    # ※nologo=trueでロゴなし、width/heightでサイズ指定
    ai_img_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1200&height=630&nologo=true"

    try:
        # 画像データをダウンロード
        img_resp = requests.get(ai_img_url, timeout=30)
        img_resp.raise_for_status()
        img_data = img_resp.content
    except Exception:
        # 失敗したらダミー画像にフォールバック
        try:
            fallback_url = "https://placehold.jp/1200x630.png?text=No+Image"
            img_data = requests.get(fallback_url, timeout=10).content
        except:
            return None

    # WordPressにアップロードするためのファイル名
    filename = f"ai_thumb_{safe_title[:10]}.jpg"

    files = {
        "file": (filename, img_data, "image/jpeg"),
    }
    data = {
        "title": title,
        "alt_text": title, 
    }
    media_url = f"{base_url}/wp-json/wp/v2/media"
    
    try:
        r = sess.post(media_url, files=files, data=data, timeout=30)
        r.raise_for_status()
        mid = r.json().get("id")
        return mid
    except Exception as e:
        print(f"Image upload failed: {e}")
        return None


def create_post(title: str, content: str, status: str = "draft"):
    cfg = Settings()
    cfg.validate(strict=True)
    sess = _create_session(cfg)

    base = cfg.wp_base_url2.rstrip("/")

    post_url = f"{base}/wp-json/wp/v2/posts"
    
    # AI画像を生成してアップロードし、IDを取得
    featured_id = _upload_ai_image(sess, base, title)

    payload = {
        "title": title,
        "content": content,
        "status": status,
    }
    if featured_id:
        payload["featured_media"] = featured_id

    r = sess.post(post_url, json=payload, timeout=30)
    
    # 404エラー時のフォールバック（旧パーマリンク設定対策）
    if r.status_code == 404:
        post_url = f"{base}/index.php?rest_route=/wp/v2/posts"
        r = sess.post(post_url, json=payload, timeout=30)

    r.raise_for_status()
    return r.json()
