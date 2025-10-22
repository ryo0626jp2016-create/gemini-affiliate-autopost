# scripts/config.py ーーー完全版
import os
from dataclasses import dataclass

@dataclass
class Settings:
    # WordPress
    wp_base_url2: str = (os.getenv("WP_BASE_URL2") or "").rstrip("/")
    wp_user: str = os.getenv("WP_USER") or ""
    wp_app_password: str = os.getenv("WP_APP_PASSWORD") or ""

    # Gemini
    gemini_api_key: str = os.getenv("GEMINI_API_KEY") or ""
    # モデル名の正規化（空/全角/先頭に 'models/' が付いてもOKに）
    _raw = (os.getenv("GEMINI_MODEL") or "gemini-1.5-pro").strip()
    if _raw.startswith("models/"):
        _raw = _raw.split("/", 1)[1]
    gemini_model: str = _raw

    # ASP（任意）
    a8_app_id: str = os.getenv("A8_APP_ID") or ""
    moshimo_affiliate_id: str = os.getenv("MOSHIMO_AFFILIATE_ID") or ""
    valuecommerce_sid: str = os.getenv("VALUECOMMERCE_SID") or ""
    valuecommerce_pid: str = os.getenv("VALUECOMMERCE_PID") or ""

    def validate(self, strict: bool = False):
        missing = []
        if not self.wp_base_url2:      missing.append("WP_BASE_URL2")
        if not self.wp_user:           missing.append("WP_USER")
        if not self.wp_app_password:   missing.append("WP_APP_PASSWORD")
        if not self.gemini_api_key:    missing.append("GEMINI_API_KEY")
        if strict and missing:
            raise RuntimeError("Missing env: " + ", ".join(missing))
