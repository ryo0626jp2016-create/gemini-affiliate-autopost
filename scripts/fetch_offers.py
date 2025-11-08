from __future__ import annotations
from typing import Dict, List
from pathlib import Path
import csv, hashlib, os

# CSVファイルの場所
DATA = Path(__file__).resolve().parents[1] / "data" / "offers_manual.csv"

def _load_offers(a8_app_id: str | None = None) -> List[Dict[str, str]]:
    """CSVを読み込んでA8リンクを自動生成"""
    rows: List[Dict[str, str]] = []
    if not DATA.exists():
        print("[warn] offers_manual.csv が見つかりません")
        return rows

    with open(DATA, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("url", "").strip()
            if not url:
                continue

            name = row.get("name", "A8オファー")
            note = row.get("note", "A8")

            # 🔗 A8リンク変換
            if a8_app_id:
                a8_link = f"https://px.a8.net/svt/ejp?a8mat={a8_app_id}&a8ejpredirect={url}"
            else:
                # A8_APP_IDが未設定ならそのままURL使用（警告表示）
                print(f"[warn] A8_APP_ID未設定 → {name} のURLを直リンクで使用")
                a8_link = url

            rows.append({
                "name": name,
                "url": a8_link,
                "note": note,
            })
    return rows


def build_offers(keyword: str) -> List[Dict[str, str]]:
    """キーワードに基づいて3件までランダムに抽出"""
    a8_app_id = os.getenv("A8_APP_ID")
    offers = _load_offers(a8_app_id)

    if not offers:
        return [{"name": "サンプルA8", "url": "https://example.com", "note": "サンプル"}]

    # キーワードでハッシュを使った簡易ランダム選択
    h = int(hashlib.sha256(keyword.encode("utf-8")).hexdigest(), 16)
    k = h % len(offers)
    return (offers[k:] + offers[:k])[:3]
