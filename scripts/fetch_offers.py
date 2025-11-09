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


def _pick_by_similarity(keyword: str, offers: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    キーワードにそれっぽいものを上から返す
    """
    kw = keyword.lower()
    kw_words = [w for w in kw.replace("　", " ").split() if w]

    scored: List[tuple[int, Dict[str, str]]] = []
    for off in offers:
        text = (off.get("name", "") + " " + off.get("note", "")).lower()
        score = 0
        for w in kw_words:
            if w and w in text:
                score += 2
        # よくありそうなパターンを少しだけ手当て
        if "vpn" in kw and "vpn" in text:
            score += 3
        if ("光" in keyword or "インターネット" in keyword) and (
            "光" in off.get("name", "") or "インターネット" in off.get("note", "")
        ):
            score += 2
        if ("ドメイン" in keyword or "サーバ" in keyword) and (
            "ドメイン" in off.get("name", "") or "サーバ" in off.get("note", "")
        ):
            score += 2
        if ("脱毛" in keyword or "美容" in keyword or "スキンケア" in keyword) and (
            "脱毛" in text or "美容" in text or "スキンケア" in text
        ):
            score += 2

        scored.append((score, off))

    # スコア0のものしかない時は空を返す → フォールバックに任せる
    scored.sort(key=lambda x: x[0], reverse=True)
    filtered = [off for s, off in scored if s > 0]
    return filtered[:3]


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

    # まず関連性で取ってみる
    picked = _pick_by_similarity(keyword, offers)
    if picked:
        return picked

    # 全然関連が見つからなかったときだけ従来どおりハッシュで回す
    h = int(hashlib.sha256(keyword.encode("utf-8")).hexdigest(), 16)
    k = h % len(offers)
    return (offers[k:] + offers[:k])[:3]
