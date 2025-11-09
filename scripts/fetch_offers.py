from __future__ import annotations
from typing import Dict, List
from pathlib import Path
import csv, hashlib, re

DATA = Path(__file__).resolve().parents[1] / "data" / "offers_manual.csv"

def _normalize_text(text: str) -> str:
    """全角・空白などを除去して検索用に整形"""
    return re.sub(r"\s+", "", text.lower())

def _load_offers() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if DATA.exists():
        with open(DATA, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("URL"):
                    continue
                rows.append({
                    "name": row.get("プログラム名") or row.get("広告主名") or "A8オファー",
                    "url": row.get("URL"),
                    "note": row.get("カテゴリ") or "A8プログラム"
                })
    return rows

def _pick_related_offers(keyword: str, offers: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """キーワードに関連するプログラムを優先的に選択"""
    kw = _normalize_text(keyword)
    scored = []
    for o in offers:
        score = 0
        text = _normalize_text(o["name"] + o["note"])
        if kw in text:
            score += 5
        if any(k in text for k in ["美容", "健康", "ビタミン"]) and "サプリ" in kw:
            score += 3
        if any(k in text for k in ["回線", "光", "Wi-Fi", "VPN"]) and "ネット" in kw:
            score += 3
        scored.append((score, o))
    scored.sort(key=lambda x: x[0], reverse=True)
    if scored and scored[0][0] > 0:
        return [x[1] for x in scored[:3]]
    # 関連が薄い場合はランダムシフト
    h = int(hashlib.sha256(keyword.encode("utf-8")).hexdigest(), 16)
    k = h % len(offers)
    return (offers[k:] + offers[:k])[:3]

def build_offers(keyword: str) -> List[Dict[str, str]]:
    offers = _load_offers()
    if not offers:
        return [{"name": "A8オファー", "url": "https://px.a8.net/", "note": "サンプル"}]
    selected = _pick_related_offers(keyword, offers)
    # 表示用タイトル生成
    for o in selected:
        o["title"] = f"【{o['note']}】{o['name'][:40]}"
    return selected
