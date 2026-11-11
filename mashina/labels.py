"""Clean labels: a co-tagged work counts only if both entities are named in its
title or abstract. Works are downloaded (1 credit per 200) and checked locally;
server-side text search costs 10 credits per request and is not used.
"""
import json
import os

from .oa import BudgetExhausted

STORE = "data/labels.json"


def invert(ii):
    if not ii:
        return ""
    w = []
    for tok, pos in ii.items():
        for p in pos:
            if p >= len(w):
                w.extend([""] * (p - len(w) + 1))
            w[p] = tok
    return " ".join(w)


def scan(oa, a, b, ra, rb, y1, y2, need=None):
    """Return matches, scanned, total and works without abstract in [y1, y2].
    Stops early once `need` matching works are found."""
    page, scanned, match, noabs, total = 1, 0, 0, 0, 0
    while True:
        j = oa.get("/works", {
            "filter": f"concepts.id:{a},concepts.id:{b},publication_year:{y1}-{y2}",
            "select": "id,publication_year,title,abstract_inverted_index",
            "per-page": 200, "page": page})
        total = j["meta"]["count"]
        for w in j["results"]:
            scanned += 1
            ab = w.get("abstract_inverted_index")
            if not ab:
                noabs += 1
            text = ((w.get("title") or "") + " " + invert(ab)).lower()
            if ra.search(text) and rb.search(text):
                match += 1
        if (need and match >= need) or scanned >= total or len(j["results"]) < 200:
            break
        page += 1
    return {"match": match, "scanned": scanned, "total": total, "noabs": noabs,
            "complete": scanned >= total}


def run(oa, jobs, rx, path=STORE, need=10, log=print):
    """jobs: list of (cutoff, A, B, window) with window 'te' (t+1..t+6) or 'tr' (..t)."""
    st = json.load(open(path)) if os.path.exists(path) else {}
    try:
        for n, (c, a, b, win) in enumerate(jobs):
            key = f"{c}|{a}|{b}|{win}"
            if key in st:
                continue
            y1, y2 = (c + 1, c + 6) if win == "te" else (1950, c)
            st[key] = scan(oa, a, b, rx[a], rx[b], y1, y2, need if win == "te" else None)
            if n % 25 == 0:
                json.dump(st, open(path, "w"))
    except BudgetExhausted as e:
        log(f"budget stop: {e}")
    json.dump(st, open(path, "w"))
    return st
