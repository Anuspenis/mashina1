"""Yearly co-occurrence counts by concept tags, resumable across nights.

Store: data/counts.json = {"single": {id: {year: n}}, "pair": {"A|B": {year: n}},
"zero_batches": [...]} with A < B. A pair absent from "pair" but covered by a
zero batch has no co-tagged works 1950-2018.

Saving credits: before asking for yearly counts, one request checks a whole
batch of partners (concepts.id:A + B1|...|B50). If the batch has zero works,
50 pairs are settled for 1 credit.
"""
import json
import os

from .oa import BudgetExhausted

STORE = "data/counts.json"
BATCH = 50


def load(path=STORE):
    if os.path.exists(path):
        return json.load(open(path))
    return {"single": {}, "pair": {}, "zero": []}


def save(st, path=STORE):
    tmp = path + ".tmp"
    json.dump(st, open(tmp, "w"), separators=(",", ":"))
    os.replace(tmp, path)


def pair_key(a, b):
    return a + "|" + b if a < b else b + "|" + a


def settled(st):
    done = set(st["pair"])
    for z in st["zero"]:
        done.update(z)
    return done


def run(oa, area_ids, path=STORE, log=print):
    st = load(path)
    try:
        for a in area_ids:
            if a not in st["single"]:
                st["single"][a] = oa.year_counts(f"concepts.id:{a}")
        save(st, path)
        done = settled(st)
        ids = sorted(area_ids)
        for i, a in enumerate(ids):
            partners = [b for b in ids[i + 1:] if pair_key(a, b) not in done]
            for s in range(0, len(partners), BATCH):
                chunk = partners[s:s + BATCH]
                n = oa.count(f"concepts.id:{a},concepts.id:" + "|".join(chunk))
                if n == 0:
                    keys = [pair_key(a, b) for b in chunk]
                    st["zero"].append(keys)
                    done.update(keys)
                    continue
                for b in chunk:
                    st["pair"][pair_key(a, b)] = oa.year_counts(f"concepts.id:{a},concepts.id:{b}")
                    done.add(pair_key(a, b))
            if i % 10 == 0:
                save(st, path)
                log(f"area {i + 1}/{len(ids)}  credits left {oa.remaining}")
    except BudgetExhausted as e:
        log(f"budget stop: {e}")
    save(st, path)
    total = len(area_ids) * (len(area_ids) - 1) // 2
    return len(settled(st)), total
