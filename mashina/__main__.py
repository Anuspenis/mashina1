"""Nightly pipeline. Usage:
    python -m mashina nightly [--areas 500] [--max-credits 9500]
    python -m mashina status
    python -m mashina evaluate
Each night continues where the previous one stopped; all state lives in data/.
"""
import argparse
import datetime as dt
import json
import os

from . import areas as areas_mod
from . import collect, labels, model, synonyms
from .oa import OpenAlex

AREAS = "data/areas.json"
KNOWN_NESTED = [("Perovskite solar cell", "Photovoltaic system"),
                ("Climate change", "Carbon capture and storage (timeline)")]


def load_areas():
    return json.load(open(AREAS))["areas"]


def index(ar, counts):
    ids = [a["id"] for a in ar]
    pos = {a: i for i, a in enumerate(ids)}
    pair = {}
    for k, v in counts["pair"].items():
        a, b = k.split("|")
        if a in pos and b in pos:          # a subset of areas keeps only its own pairs
            i, j = sorted((pos[a], pos[b]))
            pair[(i, j)] = v
    return ids, counts["single"], pair


def complete_prefix(ids_sorted, counts):
    """How many leading areas (in sorted-id order, the order of collection) already
    have counts for all their pairs. Those areas form a complete sub-network."""
    done = collect.settled(counts)
    m = 0
    for i, a in enumerate(ids_sorted):
        if all(collect.pair_key(a, b) in done for b in ids_sorted[i + 1:]):
            m += 1
        else:
            break
    return m


def nested_pairs(ar, single, pair):
    """Part-of pairs: one area is an ancestor of the other, more than half of the
    smaller area's works carry the bigger tag, or listed after the 96-work audit."""
    ids = [a["id"] for a in ar]
    name = {a["name"]: i for i, a in enumerate(ar)}
    out = set()
    for x, y in KNOWN_NESTED:
        if x in name and y in name:
            out.add(tuple(sorted((name[x], name[y]))))
    for i, a in enumerate(ar):
        for j, b in enumerate(ar):
            if i < j and (b["id"] in (a.get("ancestors") or []) or a["id"] in (b.get("ancestors") or [])):
                out.add((i, j))
    for (i, j), o in pair.items():
        p = model.ysum(o, 1950, 2018)
        m = min(model.ysum(single.get(ids[i]), 1950, 2018), model.ysum(single.get(ids[j]), 1950, 2018))
        if m and p / m > 0.5:
            out.add((i, j))
    return out


def label_jobs(ids, single, pair, exclude, windows=("te", "tr")):
    jobs = []
    for c in model.CUTS:
        for r in model.build(ids, single, pair, c, exclude=exclude):
            if r["y"]:
                jobs.append((c, ids[r["i"]], ids[r["j"]], "te"))
                if r["tr"] > 0 and "tr" in windows:
                    jobs.append((c, ids[r["i"]], ids[r["j"]], "tr"))
    return jobs


def status_text(ar, counts, lab, jobs, spent, remaining):
    total = len(ar) * (len(ar) - 1) // 2
    done = len(collect.settled(counts))
    lines = [f"# Статус машины — {dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC", "",
             f"- Областей: {len(ar)}",
             f"- Пар со счётчиками: {done} из {total} ({100 * done / max(total, 1):.1f}%)",
             f"- Проверено текстом окон «новых связей»: {len(lab)} из {len(jobs) if jobs else '— (ждёт счётчиков)'}",
             f"- Потрачено кредитов за прогон: {spent}; осталось на сегодня: {remaining}"]
    return "\n".join(lines) + "\n"


def evaluate(ar, counts, name="results", note=""):
    ids, single, pair = index(ar, counts)
    ex = nested_pairs(ar, single, pair)
    lab = json.load(open(labels.STORE)) if os.path.exists(labels.STORE) else {}
    pos = {a: i for i, a in enumerate(ids)}
    clean = {}
    for k, v in lab.items():
        c, a, b, win = k.split("|")
        if win == "te" and a in pos and b in pos:
            i, j = sorted((pos[a], pos[b]))
            clean[(int(c), i, j)] = int(v["match"] >= 10)
    res = {"tags": model.evaluate(ids, single, pair, exclude=ex),
           "clean": model.evaluate(ids, single, pair, labels=clean, exclude=ex),
           "nested_excluded": len(ex), "areas": len(ar)}
    json.dump(res, open(f"reports/{name}.json", "w"), indent=1)
    rows = ["| Срез | Связей: теги → чистые | AUC сходства: теги → чистые | AUC модели: теги → чистые | P@20 модели: теги → чистые |",
            "| --- | --- | --- | --- | --- |"]
    for c in (2008, 2012):
        t, k = res["tags"][c], res["clean"][c]
        base = k["pos"] / max(k["n"], 1)
        lift = k["p20_lr"] / base if base else 0
        rows.append(f"| {c} | {t['pos']} → {k['pos']} | {t['auc_cos']} → {k['auc_cos']} | "
                    f"{t['auc_lr']} → {k['auc_lr']} | {t['p20_lr']:.2f} → {k['p20_lr']:.2f} ({lift:.0f}× случайного) |")
    open(f"reports/{name}.md", "w").write(
        f"# Результаты на {len(ar)} областях\n\n{note}Вложенных пар исключено: {len(ex)}.\n\n" + "\n".join(rows) + "\n")
    return res


INTERIM = "data/interim_subset.json"


def interim(oa, ar, counts, at):
    """One early answer on the first complete sub-network of areas. The label scans
    it needs are a subset of the final ones, so the main run loses nothing."""
    if os.path.exists("reports/interim.json"):
        return
    if os.path.exists(INTERIM):
        sub_ids = json.load(open(INTERIM))
    else:
        ids_sorted = sorted(a["id"] for a in ar)
        m = complete_prefix(ids_sorted, counts)
        if m < at or m >= len(ar):
            return
        sub_ids = ids_sorted[:m]
        json.dump(sub_ids, open(INTERIM, "w"))
    keep = set(sub_ids)
    sub = [a for a in ar if a["id"] in keep]
    ids, single, pair = index(sub, counts)
    ex = nested_pairs(sub, single, pair)
    jobs = label_jobs(ids, single, pair, ex, windows=("te",))
    rx = synonyms.compiled(json.load(open(synonyms.STORE)))
    lab = labels.run(oa, jobs, rx)
    if all(f"{c}|{a}|{b}|{w}" in lab for c, a, b, w in jobs):
        evaluate(sub, counts, name="interim",
                 note="Промежуточный результат: первые области, для которых собраны все пары. "
                      "Критерий записан заранее (README). Финал — на всех 500.\n\n")


def nightly(args):
    oa = OpenAlex(max_credits=args.max_credits)
    if not os.path.exists(AREAS):
        areas_mod.build(oa, AREAS, n=args.areas)
    areas_mod.fill_ancestors(oa, AREAS)
    ar = load_areas()
    synonyms.build(ar)
    interim(oa, ar, collect.load(), args.interim_at)
    n_done, n_total = collect.run(oa, [a["id"] for a in ar])
    counts = collect.load()
    jobs, lab = [], {}
    if n_done >= n_total:
        ids, single, pair = index(ar, counts)
        ex = nested_pairs(ar, single, pair)
        jobs = label_jobs(ids, single, pair, ex)
        rx = synonyms.compiled(json.load(open(synonyms.STORE)))
        lab = labels.run(oa, jobs, rx)
        if all(f"{c}|{a}|{b}|{w}" in lab for c, a, b, w in jobs):
            evaluate(ar, counts)
    open("reports/status.md", "w").write(status_text(ar, counts, lab, jobs, oa.spent, oa.remaining))
    print(open("reports/status.md").read())


def main():
    p = argparse.ArgumentParser(prog="mashina")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("nightly")
    n.add_argument("--areas", type=int, default=500)
    n.add_argument("--max-credits", type=int, default=9500)
    n.add_argument("--interim-at", type=int, default=120)
    sub.add_parser("status")
    sub.add_parser("evaluate")
    a = p.parse_args()
    os.makedirs("reports", exist_ok=True)
    if a.cmd == "nightly":
        nightly(a)
    elif a.cmd == "status":
        ar = load_areas()
        print(status_text(ar, collect.load(), {}, [], 0, None))
    else:
        print(json.dumps(evaluate(load_areas(), collect.load()), indent=1))


if __name__ == "__main__":
    main()
