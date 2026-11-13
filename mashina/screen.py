"""Wide niche screen (13.11.2026): 18 booms x 8 adjacent needs = 144 niches, made by rule.

Why: the 20-niche list was picked by Claude, and Claude's own occupancy scores failed the
data check (reports/niches_data.md). Here the niches come from a rule: every boom is crossed
with every adjacent need, because in the AI boom the money also went to the needs next to
it (data quality, compute, power), not only to the core.

Rule written BEFORE the results (13.11.2026, ~00:30 Copenhagen). Scores 0-3:
  size        boom money flow per year: >=100bn$ 3, 10-100bn$ 2, 1-10bn$ 1 (Claude's coding, notes below)
  demand      EU public tenders (TED) since 2025 matching the niche, median of 3 wordings, by quartile
  momentum    tenders per month since 2025 vs 2023-2024, by quartile (fewer than 6 tenders = 1)
  open        3 - quartile of GitHub repositories (builders); low weight, because crowded != solved
  timing      3 spending now or dated law without delays; 2 dated law with delays/pushback;
              1 waits for an undated political event; 0 no driver
  durable     3 legal obligation or long build times; 2 mixed; 1 shock that fades when the shock ends
  access      the user's own edge: languages, Ukraine, Central Asia, Denmark; minus clearance needs
  capital     ease of taking a share without large capital (by adjacent need)
  wlb         work-life balance of the work itself (by adjacent need)
Weightings: "jackpot" (the user's main criterion: size 3, demand 2, momentum 2, access 2,
durable 1, timing 1, capital 1, wlb 1, open 0.5), equal, and 20 000 random ones.
Shortlist = top 10 by "jackpot" that are also in the random top 20 in at least half the draws.
A niche whose 3 wordings differ more than 3x in tender counts is flagged "unreliable".
Limits: TED counts EU state buying only and mostly English text; GitHub counts programmers.
Usage: python -m mashina.screen
"""
import json
import os
import time
import urllib.parse
import urllib.request

import numpy as np

UA = {"User-Agent": "mashina research (github.com/bogdalbogvsyal/mashina1)"}

# key: (name, 3 English wordings, size, timing, durable, access, note)
BOOMS = {
    "ai": ("Вычисления для ИИ и дата-центры", ["data center", "data centre", "hyperscale"], 3, 3, 2, 1,
           "капзатраты гиперскейлеров $209 млрд за III кв. 2026"),
    "grid": ("Электросети и электрификация", ["power grid", "electricity grid", "transmission network"], 3, 3, 3, 2,
             "оценка: сети — сотни млрд $ в год в мире"),
    "rearm": ("Перевооружение Европы", ["defence industry", "ammunition", "military procurement"], 3, 2, 3, 1,
              "ReArm Europe €800 млрд, SAFE €150 млрд; допуск к секретности не раньше ~2032"),
    "drones": ("Дроны и защита от дронов", ["drone", "unmanned aerial", "anti-drone"], 2, 3, 2, 2,
               "оценка; опыт Украины"),
    "ukraine": ("Восстановление Украины", ["Ukraine reconstruction", "Ukraine recovery", "rebuild Ukraine"], 2, 1, 3, 3,
                "RDNA5: $588 млрд за 10 лет; большая волна ждёт перемирия"),
    "energyshock": ("Энергетический шок: СПГ, нефть, переработка", ["LNG", "gas supply", "oil refining"], 3, 3, 1, 2,
                    "Ормуз закрыт с 28.02.2026; доп. расходы ЕС на газ ~€100 млрд/год в сценарии"),
    "euproof": ("Доказательства по законам ЕС (CBAM, метан, батареи, труд)",
                ["carbon border adjustment", "supply chain due diligence", "methane emissions"], 2, 2, 3, 3,
                "оценка; даты в законах, но отсрочки и споры"),
    "minerals": ("Критические минералы и магниты", ["critical raw materials", "rare earth", "battery minerals"], 2, 2, 2, 2,
                 "оценка"),
    "nuclear": ("Ядерное возрождение", ["small modular reactor", "nuclear fuel", "uranium enrichment"], 2, 2, 3, 0,
                "оценка; экспортный контроль"),
    "space": ("Космос", ["satellite", "space launch", "earth observation"], 2, 3, 2, 1,
              "Space Capital: $22,2 млрд за III кв. 2026"),
    "biotech": ("Препараты от ожирения и генная терапия", ["semaglutide", "gene therapy", "lipid nanoparticle"], 2, 3, 2, 1,
                "оценка"),
    "quantum": ("Квантовые технологии", ["quantum computing", "quantum sensor", "qubit"], 1, 1, 2, 1, "оценка"),
    "shipping": ("Судоходство и торговые коридоры", ["container shipping", "Middle Corridor", "shipping route"], 2, 3, 2, 2,
                 "оценка; Maersk и DSV в Дании"),
    "adaptation": ("Адаптация к климату и вода", ["climate adaptation", "flood protection", "water infrastructure"], 2, 2, 3, 2,
                   "оценка"),
    "batteries": ("Батареи и электромобили в Европе", ["battery manufacturing", "battery cell", "electric vehicle battery"], 2, 2, 2, 1,
                  "оценка; провал Northvolt"),
    "chips": ("Полупроводники в Европе", ["semiconductor", "chip manufacturing", "semiconductor fab"], 2, 2, 2, 0, "оценка"),
    "hydrogen": ("Водород (контроль: бум, который не случился)", ["green hydrogen", "electrolyser", "hydrogen production"], 1, 1, 1, 1,
                 "оценка"),
    "aidata": ("Качество данных и проверка ИИ", ["training data", "data annotation", "AI evaluation"], 2, 3, 2, 2,
               "Surge, Mercor, Scale: выручка в млрд $"),
}
# key: (name, 3 English wordings, wlb, capital_ease)
NEEDS = {
    "materials": ("сырьё и материалы", ["raw materials", "materials supply", "feedstock"], 2, 0),
    "energy": ("энергия для этого", ["electricity supply", "power supply", "energy demand"], 1, 1),
    "equipment": ("оборудование и компоненты", ["equipment", "components", "manufacturing capacity"], 2, 0),
    "people": ("люди и навыки", ["skills shortage", "workforce", "training"], 2, 3),
    "data": ("данные, проверка, качество", ["data", "verification", "certification"], 3, 3),
    "permits": ("разрешения и соответствие закону", ["permitting", "compliance", "regulation"], 2, 3),
    "logistics": ("логистика и монтаж", ["logistics", "installation", "transport"], 1, 1),
    "maintenance": ("обслуживание и ремонт", ["maintenance", "repair", "servicing"], 1, 2),
}
WIKI = {"ai": "Data_center", "grid": "Electrical_grid", "rearm": "Arms_industry", "drones": "Unmanned_aerial_vehicle",
        "ukraine": "Reconstruction_of_Ukraine", "energyshock": "Strait_of_Hormuz",
        "euproof": "Carbon_Border_Adjustment_Mechanism", "minerals": "Critical_mineral_raw_materials",
        "nuclear": "Small_modular_reactor", "space": "Satellite", "biotech": "Semaglutide",
        "quantum": "Quantum_computing", "shipping": "Container_ship", "adaptation": "Climate_change_adaptation",
        "batteries": "Lithium-ion_battery", "chips": "Semiconductor_industry", "hydrogen": "Green_hydrogen",
        "aidata": "Training,_validation,_and_test_data_sets"}


def http(url, data=None, headers=None, timeout=60):
    h = dict(UA)
    h.update(headers or {})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=timeout) as r:
                return json.load(r)
        except Exception:
            time.sleep(5 * (attempt + 1))
    return None


def ted(query):
    j = http("https://api.ted.europa.eu/v3/notices/search",
             data=json.dumps({"query": query, "fields": ["publication-number"], "limit": 1}).encode(),
             headers={"Content-Type": "application/json"})
    time.sleep(0.6)
    return None if j is None else j.get("totalNoticeCount")


def github(q, token):
    j = http("https://api.github.com/search/repositories?" + urllib.parse.urlencode({"q": q, "per_page": 1}),
             headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"})
    time.sleep(2.3)
    return None if j is None else j.get("total_count")


def wiki_trend(article):
    j = http("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
             + urllib.parse.quote(article, safe="") + "/monthly/20250501/20261031")
    if not j or "items" not in j:
        return None
    v = [it["views"] for it in j["items"]]
    if len(v) < 12:
        return None
    return round(sum(v[-6:]) / max(sum(v[-12:-6]), 1), 2)


def quart(x, missing):
    """Quartile 0-3; a missing value gets `missing` instead of being ranked."""
    x = np.asarray(x, float)
    q = np.nanquantile(x, [0.25, 0.5, 0.75])
    out = np.where(x < q[0], 0, np.where(x < q[1], 1, np.where(x < q[2], 2, 3)))
    return np.where(np.isnan(x), missing, out)


def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    rows = []
    for bk, (bname, bterms, size, timing, durable, access, note) in BOOMS.items():
        for nk, (nname, nterms, wlb, capital) in NEEDS.items():
            r = {"boom": bk, "need": nk, "niche": f"{bname} — {nname}", "size": size, "timing": timing,
                 "durable": durable, "access": access, "wlb": wlb, "capital": capital, "note": note,
                 "recent": [], "prior": [], "gh": []}
            for k in range(3):
                core = f'"{bterms[k]}" AND {nterms[k]}'
                r["recent"].append(ted(f"FT~({core}) AND PD>=20250101"))
                r["prior"].append(ted(f"FT~({core}) AND PD>=20230101 AND PD<=20241231"))
                if token:
                    r["gh"].append(github(f'"{bterms[k]}" {nterms[k]}', token))
            rows.append(r)
            print(r["niche"], r["recent"], r["prior"], r["gh"], flush=True)
    wiki = {bk: wiki_trend(a) for bk, a in WIKI.items()}

    def med(v):
        v = [x for x in v if x is not None]
        return float(np.median(v)) if v else np.nan

    for r in rows:
        rec, pri = med(r["recent"]), med(r["prior"])
        r["tenders_recent"], r["tenders_prior"] = rec, pri
        # Fix 13.11.2026: no tenders before = growth unknown (was shown and ranked as a made-up x3.0)
        r["momentum_raw"] = (rec / 22.4) / (pri / 24) if pri and pri > 0 else np.nan
        vals = [x for x in r["recent"] if x]
        r["unreliable"] = bool(vals and max(vals) > 3 * max(min(vals), 1))
        r["gh_median"] = med(r["gh"])
        r["wiki_trend"] = wiki.get(r["boom"])
    demand = quart([r["tenders_recent"] for r in rows], 0)
    mom = quart([r["momentum_raw"] for r in rows], 1)
    open_ = 3 - quart([r["gh_median"] for r in rows], 2)
    for r, d, m, o in zip(rows, demand, mom, open_):
        r["demand"] = int(d)
        r["momentum"] = 1 if (np.nan_to_num(r["tenders_recent"]) + np.nan_to_num(r["tenders_prior"])) < 6 else int(m)
        r["open"] = int(o)
    crit = ["size", "demand", "momentum", "open", "timing", "durable", "access", "capital", "wlb"]
    S = np.array([[r[c] for c in crit] for r in rows], float)
    jack = np.array([3, 2, 2, 0.5, 1, 1, 2, 1, 1])
    js = S @ jack / jack.sum()
    eq = S.mean(1)
    W = np.random.default_rng(42).dirichlet(np.ones(len(crit)), 20000)
    top20 = np.zeros(len(rows))
    for idx in np.argsort(-(W @ S.T), axis=1)[:, :20]:
        top20[idx] += 1
    top20 /= len(W)
    for r, a, b, c in zip(rows, js, eq, top20):
        r["jackpot"], r["equal"], r["random_top20"] = round(float(a), 3), round(float(b), 3), round(float(c), 3)
    order = np.argsort(-js)
    shortlist = [rows[i]["niche"] for i in order[:10] if top20[i] >= 0.5]
    out = {"run": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "criteria": crit, "jackpot_weights": jack.tolist(),
           "wiki_trend_last6_vs_prev6": wiki, "shortlist": shortlist, "rows": rows}
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/screen.json", "w"), ensure_ascii=False, indent=1, default=float)

    lines = [f"# Широкий отбор: 144 ниши ({out['run']})", "",
             "Правило записано до результатов (докстринг `mashina/screen.py`).", "",
             "## Топ-30 по главному критерию: шанс на наибольший куш", "",
             "| # | Ниша | Куш-балл | Ровные веса | В топ-20 при случайных весах | Тендеры ЕС с 2025 | Рост тендеров | Репозитории | Ненадёжно |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for n, i in enumerate(order[:30], 1):
        r = rows[i]
        mr = r["momentum_raw"]
        lines.append(f"| {n} | {r['niche']} | {r['jackpot']:.2f} | {r['equal']:.2f} | {r['random_top20']:.0%} | "
                     f"{r['tenders_recent']:.0f} | {'—' if mr != mr else f'×{mr:.1f}'} | {r['gh_median']:.0f} | {'да' if r['unreliable'] else ''} |")
    lines += ["", "## Короткий список (правило)", ""] + [f"- {s}" for s in shortlist]
    lines += ["", "## Бумы: средний куш-балл по 8 нуждам", ""]
    for bk in BOOMS:
        v = [r["jackpot"] for r in rows if r["boom"] == bk]
        lines.append(f"- {BOOMS[bk][0]}: {np.mean(v):.2f}; внимание в Википедии (6 мес. к прошлым 6): {wiki.get(bk)}")
    lines += ["", "## Смежные нужды: средний куш-балл по 18 бумам", ""]
    for nk in NEEDS:
        v = [r["jackpot"] for r in rows if r["need"] == nk]
        lines.append(f"- {NEEDS[nk][0]}: {np.mean(v):.2f}")
    open("reports/screen.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
