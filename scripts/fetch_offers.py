# scripts/fetch_offers.py
from __future__ import annotations
from typing import Dict, List
from pathlib import Path
import csv
import hashlib
import os

# data/offers_manual.csv を読む前提
DATA = Path(__file__).resolve().parents[1] / "data" / "offers_manual.csv"


def _load_offers(a8_app_id: str | None = None) -> List[Dict[str, str]]:
    """CSVを読み込んで、必要ならA8リンクに変換して返す"""
    rows: List[Dict[str, str]] = []

    if not DATA.exists():
        print(f"[warn] {DATA} が見つかりません")
        return rows

    with DATA.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_url = (row.get("url") or "").strip()
            if not raw_url:
                continue

            name = (row.get("name") or "A8オファー").strip()
            note = (row.get("note") or "").strip()

            # A8_APP_ID があれば px.a8.net の形式にする
            if a8_app_id:
                # a8ejpredirect= には元のLPをそのまま
                offer_url = (
                    f"https://px.a8.net/svt/ejp?a8mat={a8_app_id}"
                    f"&a8ejpredirect={raw_url}"
                )
            else:
                # 無ければそのまま直リンク
                print(f"[warn] A8_APP_ID 未設定 → {name} は直リンクで出力します")
                offer_url = raw_url

            rows.append(
                {
                    "name": name,
                    "url": offer_url,
                    "note": note,
                }
            )

    return rows


def build_offers(keyword: str) -> List[Dict[str, str]]:
    """
    記事ごとに3件くらい出したいので、
    キーワードのハッシュでずらして3つ返す
    """
    a8_app_id = os.getenv("A8_APP_ID")
    offers = _load_offers(a8_app_id)

    if not offers:
        return [
            {
                "name": "サンプルA8",
                "url": "https://example.com",
                "note": "サンプル",
            }
        ]

    h = int(hashlib.sha256(keyword.encode("utf-8")).hexdigest(), 16)
    start = h % len(offers)
    rotated = offers[start:] + offers[:start]
    return rotated[:3]
