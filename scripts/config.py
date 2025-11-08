# scripts/config.py
import os
from dataclasses import dataclass

@dataclass
class Settings:
    """
    GitHub Actions から渡された環境変数をまとめて持つクラス
    /2024blog に投稿するのがデフォルト
    """
    # WordPress (末尾の / は消しておく)
    wp_base_url: str = (os.getenv("WP_BASE_URL2") or "https://www.2025blog.com/2024blog").rstrip("/")
    wp_user: str = os.getenv("WP_USER") or ""
    wp_app_password: str = os.getenv("WP_APP_PASSWORD") or ""

    # Gemini
    gemini_api_key: str = os.getenv("GEMINI_API_KEY") or ""

    # モデル名の正規化
    _raw_model = (os.getenv("GEMINI_MODEL") or "").strip()
    if _raw_model.startswith("models/"):
        _raw_model = _raw_model.split("/", 1)[1]
    # workflow で拾ってきた名前がなければとりあえずこれ
    gemini_model: str = _raw_model or "gemini-1.5-pro"

    # ASP（任意）
    a8_app_id: str = os.getenv("A8_APP_ID") or ""
    moshimo_affiliate_id: str = os.getenv("MOSHIMO_AFFILIATE_ID") or ""
    valuecommerce_sid: str = os.getenv("VALUECOMMERCE_SID") or ""
    valuecommerce_pid: str = os.getenv("VALUECOMMERCE_PID") or ""

    # 実投稿を止めたいとき用（Actionsで DRY_RUN=1 にする）
    dry_run: bool = (os.getenv("DRY_RUN", "0") == "1")

    # どのブログ向けの記事か（今回は internet 固定でいい）
    blog_kind: str = os.getenv("BLOG_KIND", "internet")

    def validate(self, strict: bool = False):
        """
        必須の環境変数が無いときにエラーにする
        dry-run のときはゆるくする
        """
        missing = []
        if not self.wp_base_url:
            missing.append("WP_BASE_URL2")
        if not self.wp_user:
            missing.append("WP_USER")
        if not self.wp_app_password:
            missing.append("WP_APP_PASSWORD")
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")

        if strict and missing:
            raise RuntimeError("Missing env: " + ", ".join(missing))
