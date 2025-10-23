import random, csv, pathlib
DATA = pathlib.Path(__file__).resolve().parents[1]/'data'/'keywords_internet.csv'

def pick_topic(seed=None):
    if seed is not None:
        random.seed(seed)
    rows = list(csv.DictReader(open(DATA,encoding='utf-8')))
    t = random.choice(rows)
    headings = [
        f"{t['keyword']}とは？",
        f"{t['keyword']}の選び方",
        "比較とおすすめ",
        "申込みの流れ",
        "Q&A",
    ]
    return {
        'keyword': t['keyword'],
        'category': t['category'],
        'notes': t['notes'],
        'headings': headings,
        'lede': f"{t['keyword']}の要点まとめ",
    }
