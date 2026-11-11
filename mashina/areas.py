"""Choose the areas (OpenAlex concepts) the machine works on.

Rule written down before any results: keep the 50 areas of the first experiment,
then add a random, field-stratified sample of level-2/3 concepts with at least
5 000 works, seed 42. No hand-picking, so the sample cannot be tuned to a result.
"""
import json
import random
from collections import defaultdict

BASE50 = "data/areas_50.json"


def fetch_candidates(oa, min_works=5000):
    out, cursor = [], "*"
    while cursor:
        j = oa.get("/concepts", {
            "filter": f"level:2|3,works_count:>{min_works}",
            "select": "id,display_name,level,works_count,ancestors,wikidata",
            "per-page": 200, "cursor": cursor})
        for c in j["results"]:
            roots = [a for a in (c.get("ancestors") or []) if a.get("level") == 0]
            out.append({
                "id": c["id"].rsplit("/", 1)[-1],
                "name": c["display_name"],
                "level": c["level"],
                "works": c["works_count"],
                "root": roots[0]["display_name"] if roots else "?",
                "ancestors": [a["id"].rsplit("/", 1)[-1] for a in (c.get("ancestors") or [])],
                "wikidata": (c.get("wikidata") or "").rsplit("/", 1)[-1],
            })
        cursor = j["meta"].get("next_cursor")
    return out


def select(candidates, base, n=500, seed=42):
    base_ids = {a["id"] for a in base}
    pool = [c for c in candidates if c["id"] not in base_ids]
    by_root = defaultdict(list)
    for c in pool:
        by_root[c["root"]].append(c)
    need = n - len(base)
    rng = random.Random(seed)
    total = len(pool)
    picked = []
    for root in sorted(by_root):
        group = sorted(by_root[root], key=lambda c: c["id"])
        k = round(need * len(group) / total)
        picked += rng.sample(group, min(k, len(group)))
    rest = sorted((c for c in pool if c not in picked), key=lambda c: c["id"])
    rng.shuffle(rest)
    picked += rest[: max(0, need - len(picked))]
    picked = picked[:need]
    chosen = list(base) + sorted(picked, key=lambda c: c["id"])
    return chosen


def build(oa, path="data/areas.json", n=500):
    base = json.load(open(BASE50))
    cand = fetch_candidates(oa)
    chosen = select(cand, base, n=n)
    json.dump({"rule": "50 base + stratified random level-2/3, works>5000, seed 42",
               "candidates": len(cand), "areas": chosen},
              open(path, "w"), ensure_ascii=False, indent=1)
    return chosen
