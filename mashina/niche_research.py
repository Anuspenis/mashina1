"""Data check of the niche scores in mashina/compare_all.py (one-off, 12-13.11.2026).

For each niche, two outside signals:
- OpenAlex: works per year matching a text query (growth 2023-2025 vs 2018-2020).
  One search request per niche = 10 credits, 20 niches = 200 credits.
- GitHub: how many public repositories already exist for the niche (all, created
  since 2025, pushed in the last 6 months) = how many people already build tools there.

Rule written down BEFORE the results (12.11.2026, 23:55 Copenhagen):
1. "Occupied" signal = rank of log(1 + active GitHub repos) + rank of log(1 + works 2023-2025).
   If my "незанято" score is right, Spearman rho between it and the occupied signal is negative.
   rho >= 0 means the data do not support my occupancy scores; rho <= -0.3 means they do;
   in between = weak support.
2. A niche I scored "незанято" = 3 that sits in the top quarter of the occupied signal is a
   flagged contradiction and is reported by name.
3. Counts depend on query wording, so levels are compared only as ranks, and growth only as a ratio.
Usage: python -m mashina.niche_research
"""
import json
import math
import os
import time
import urllib.parse
import urllib.request

import numpy as np

from .compare_all import NICHES
from .oa import OpenAlex

# name prefix -> (OpenAlex text query, GitHub repository query)
QUERIES = [
    ("Доказательство происхождения", '"carbon border adjustment" OR "supply chain due diligence" OR "provenance verification"', 'cbam OR "carbon border" OR "supply chain due diligence"'),
    ("Метан в импортном газе", '"methane emissions" AND (satellite OR TROPOMI)', 'methane satellite'),
    ("Проверка ИИ и данных", '"AI Act" OR "algorithmic auditing" OR "AI conformity assessment"', '"ai act" OR "ai audit"'),
    ("Медь Узбекистана", 'copper AND Uzbekistan', 'copper uzbekistan'),
    ("Энергия по физике погоды", '"electricity price forecasting" OR "wind power forecasting"', '"electricity price forecasting" OR "wind power forecasting"'),
    ("Трансформаторы", '"grain-oriented electrical steel" OR ("power transformer" AND "supply chain")', '"power transformer"'),
    ("Критические минералы", '"critical raw materials" OR ("rare earth" AND "supply chain")', '"critical raw materials" OR "critical minerals"'),
    ("Коммерческая наука", '"patent citations" OR "science-industry linkage"', '"patent citations"'),
    ("Сурьма", 'antimony AND ("supply chain" OR Tajikistan OR mining)', 'antimony'),
    ("Средний коридор", '"Middle Corridor" OR "Trans-Caspian"', '"middle corridor" OR "trans-caspian"'),
    ("Космос", '"space weather" OR "orbital data center"', '"space weather"'),
    ("Гелий", '"helium-3" OR "tritium supply" OR "REBCO"', 'helium-3 OR rebco OR tritium'),
    ("ИИ для науки", '"self-driving laboratory" OR "autonomous laboratory"', '"self-driving lab" OR "autonomous laboratory"'),
    ("Оборонная химия", '"energetic materials" AND (production OR manufacturing)', '"energetic materials"'),
    ("Газ Южного коридора", '"Southern Gas Corridor" OR (Azerbaijan AND "natural gas")', '"southern gas corridor"'),
    ("Обогащение урана", '"uranium enrichment" OR HALEU', 'haleu OR "uranium enrichment"'),
    ("Доставка генной терапии", '"lipid nanoparticle" AND extrahepatic', '"lipid nanoparticle"'),
    ("Память и чипы", '"high bandwidth memory"', '"high bandwidth memory"'),
    ("Рынки предсказаний", '"prediction market" OR stablecoin', '"prediction market" OR stablecoin'),
    ("Дженерики GLP-1", 'semaglutide AND (generic OR biosimilar OR compounded)', 'semaglutide'),
]


def full_name(prefix):
    return next(n for n in NICHES if n.startswith(prefix))


def github_count(q, token):
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode({"q": q, "per_page": 1})
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "Authorization": "Bearer " + token,
                                               "User-Agent": "mashina"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)["total_count"]
        except Exception:
            time.sleep(10 * (attempt + 1))
    return None


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    oa = OpenAlex(floor=40, max_credits=230)
    rows = []
    for prefix, oq, gq in QUERIES:
        name = full_name(prefix)
        row = {"niche": name, "oa_query": oq, "gh_query": gq}
        try:
            j = oa.get("/works", {"search": oq, "filter": "publication_year:2015-2025",
                                  "group_by": "publication_year"}, allow_search=True)
            yc = {int(g["key"]): g["count"] for g in j["group_by"]}
            row["works_by_year"] = yc
            row["works_2023_25"] = sum(yc.get(y, 0) for y in (2023, 2024, 2025))
            early = sum(yc.get(y, 0) for y in (2018, 2019, 2020))
            row["growth"] = round(row["works_2023_25"] / early, 2) if early else None
        except Exception as e:  # budget or network: keep going with GitHub
            row["oa_error"] = str(e)
        if token:
            row["gh_all"] = github_count(gq, token)
            time.sleep(2.5)
            row["gh_new_since_2025"] = github_count(gq + " created:>=2025-01-01", token)
            time.sleep(2.5)
            row["gh_active_6m"] = github_count(gq + " pushed:>=2026-05-13", token)
            time.sleep(2.5)
        rows.append(row)
        print(name, row.get("works_2023_25"), row.get("growth"), row.get("gh_all"), row.get("gh_active_6m"), flush=True)

    ok = [r for r in rows if r.get("works_2023_25") is not None and r.get("gh_active_6m") is not None]
    verdict = {}
    if len(ok) >= 10:
        occ_gh = [math.log1p(r["gh_active_6m"]) for r in ok]
        occ_oa = [math.log1p(r["works_2023_25"]) for r in ok]
        occ = np.argsort(np.argsort(occ_gh)) + np.argsort(np.argsort(occ_oa))
        mine = [NICHES[r["niche"]][1] for r in ok]
        rho = spearman(mine, occ)
        cut = np.quantile(occ, 0.75)
        flagged = [r["niche"] for r, o, m in zip(ok, occ, mine) if m == 3 and o >= cut]
        verdict = {"n": len(ok), "rho_open_vs_occupied": round(rho, 2),
                   "reading": "supports" if rho <= -0.3 else ("weak support" if rho < 0 else "does not support"),
                   "flagged_open_but_crowded": flagged}
    out = {"run": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "credits_spent": oa.spent,
           "rows": rows, "verdict": verdict}
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/niches_data.json", "w"), ensure_ascii=False, indent=1)
    lines = [f"# Ниши: проверка данными ({out['run']})", "",
             "| Ниша | Работ 2023–2025 | Рост к 2018–2020 | Репозиториев на GitHub | Новых с 2025 | Активных за 6 мес. |",
             "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['niche']} | {r.get('works_2023_25', '—')} | {r.get('growth', '—')} | "
                     f"{r.get('gh_all', '—')} | {r.get('gh_new_since_2025', '—')} | {r.get('gh_active_6m', '—')} |")
    lines += ["", f"Проверка правила: {verdict}", f"Потрачено кредитов OpenAlex: {oa.spent}"]
    open("reports/niches_data.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
