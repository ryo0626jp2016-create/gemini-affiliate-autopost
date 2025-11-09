from __future__ import annotations
from typing import Dict, List
from pathlib import Path
import csv, hashlib, urllib.parse, random

# === あなた専用A8トラッキングID ===
A8MAT = "45G7HH+AV5T82+3HZU+15ORS2"
A8_BASE = "https://px.a8.net/svt/ejp"

DATA = Path(__file__).resolve().parents[1] / "data" / "offers_manual.csv"

def _load_offers() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if DATA.exists():
        with open(DATA, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                if row.get("url"):
                    # URLをA8トラッキング付きに変換
                    target = row["url"].strip()
                    encoded = urllib.parse.quote(target, safe="")
                    a8_url = f"{A8_BASE}?a8mat={A8MAT}&a8ejpredirect={encoded}"
                    rows.append({
                        "name": row.get("name","おすすめ商品"),
                        "url": a8_url,
                        "note": row.get("note","その他")
                    })
    return rows

def build_offers(keyword: str) -> List[Dict[str, str]]:
    """記事のキーワードに関連しそうなA8オファーを3件抽出"""
    offers = _load_offers()
    if not offers:
        return [{"name": "サンプルA8リンク", "url": "https://example.com", "note": "サンプル"}]

    # キーワードに近いカテゴリを優先抽出
    related = [o for o in offers if o["note"] in keyword or keyword in o["note"]]
    pool = related if related else offers

    random.shuffle(pool)
    return pool[:3]

