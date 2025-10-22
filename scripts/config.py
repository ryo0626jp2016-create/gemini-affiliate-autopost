# ================================================
# config.py
# Gemini × WordPress 自動投稿設定ファイル
# ================================================

import os
from dotenv import load_dotenv

# .env がある場合はロード
load_dotenv()

# --------------------------------
# WordPress API 接続情報
# --------------------------------
wp_base_url = os.getenv("WP_BASE_URL2")
wp_user = os.getenv("WP_USER")
wp_app_password = os.getenv("WP_APP_PASSWORD")

# --------------------------------
# Gemini 設定
# --------------------------------
# モデル名を安全に正規化（空文字や 'models/' を除去）
_raw = (os.getenv("GEMINI_MODEL") or "gemini-1.5-pro").strip()
if _raw.startswith("models/"):
    _raw = _raw.split("/", 1)[1]
gemini_model = _raw

# APIキー
gemini_api_key = os.getenv("GEMINI_API_KEY")

# --------------------------------
# ASP設定（A8・もしも・バリューコマース）
# --------------------------------
a8_app_id = os.getenv("A8_APP_ID")
moshimo_affiliate_id = os.getenv("MOSHIMO_AFFILIATE_ID")
valuecommerce_sid = os.getenv("VALUECOMMERCE_SID")
valuecommerce_pid = os.getenv("VALUECOMMERCE_PID")

# --------------------------------
# 環境確認用ログ（B対応）
# --------------------------------
print("========== CONFIG CHECK ==========")
print(f"WP_BASE_URL2: {wp_base_url}")
print(f"Gemini Model: {gemini_model}")
print(f"Gemini API Key: {'✔' if gemini_api_key else '❌'}")
print(f"A8_APP_ID: {'✔' if a8_app_id else '❌'}")
print("==================================")
