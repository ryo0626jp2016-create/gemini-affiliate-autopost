# scripts/fetch_offers.py
from __future__ import annotations
from typing import Dict, List
from pathlib import Path
import csv, hashlib

DATA = Path(__file__).resolve().parents[1] / "data" / "offers_manual.csv"


def _load_offers() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if DATA.exists():
        with open(DATA, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                url = (row.get("url") or "").strip()
                if not url:
                    continue
                rows.append(
                    {
                        "name": (row.get("name") or "").strip() or "おすすめサービス",
                        "url": url,
                        "note": (row.get("note") or "").strip(),
                    }
                )
    return rows


def build_offers(keyword: str) -> List[Dict[str, str]]:
    offers = _load_offers()
    if not offers:
        return [
            {
                "name": "おすすめサービス",
                "url": "https://example.com",
                "note": "",
            }
        ]
    # キーワードでシャッフルして3件出す
    h = int(hashlib.sha256(keyword.encode("utf-8")).hexdigest(), 16)
    k = h % len(offers)
    return (offers[k:] + offers[:k])[:3]

