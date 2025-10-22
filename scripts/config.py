import os
from dataclasses import dataclass

@dataclass
class Config:
    # WordPress 投稿設定
    wp_base_url: str = os.getenv("WP_BASE_URL2")
    wp_user: str = os.getenv("WP_USER")
    wp_app_password: str = os.getenv("WP_APP_PASSWORD")

    # Gemini API設定
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    
    # モデル名の正規化処理（models/が付いていても安全に動作）
    _raw_model = (os.getenv("GEMINI_MODEL") or "gemini-1.5-pro").strip()
    if _raw_model.startswith("models/"):
        _raw_model = _raw_model.split("/", 1)[1]
    gemini_model: str = _raw_model

    # ASP系APIキー
    a8_app_id: str = os.getenv("A8_APP_ID")
    moshimo_affiliate_id: str = os.getenv("MOSHIMO_AFFILIATE_ID")
    valuecommerce_sid: str = os.getenv("VALUECOMMERCE_SID")
    valuecommerce_pid: str = os.getenv("VALUECOMMERCE_PID")

config = Config()
