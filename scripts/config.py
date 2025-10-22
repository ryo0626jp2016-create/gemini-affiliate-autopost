from dataclasses import dataclass
import os
from dotenv import load_dotenv
load_dotenv()
@dataclass
class Settings:
    wp_base_url2=os.getenv('WP_BASE_URL2','').rstrip('/')
    wp_user=os.getenv('WP_USER','')
    wp_app_password=os.getenv('WP_APP_PASSWORD','')
    gemini_api_key=os.getenv('GEMINI_API_KEY','')
    gemini_model: str = os.getenv("GEMINI_MODEL") or "gemini-1.5-pro"
    def validate(self,strict=False):
        missing=[]
        if not self.wp_base_url2: missing.append('WP_BASE_URL2')
        if not self.wp_user: missing.append('WP_USER')
        if not self.wp_app_password: missing.append('WP_APP_PASSWORD')
        if not self.gemini_api_key: missing.append('GEMINI_API_KEY')
        if strict and missing: raise RuntimeError(missing)
