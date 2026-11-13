"""Radar v0 (13.11.2026): a scan that runs on a schedule in GitHub Actions and needs no Claude.

Question it serves: where is the sharpest deficit or the biggest boom, without a hand-written list of niches.

STREAM 1 - prices of everything producers sell (US Bureau of Labor Statistics, Producer Price Index,
all commodity series, monthly). A sharp and lasting price rise across a product line is the most direct
public trace of a deficit: buyers pay more and supply does not catch up.

RULE (written before the first run):
- Universe: every not-seasonally-adjusted commodity series (id starts with WPU) that has a value in the
  months needed. No list of products is written by hand.
- At month t: rise24 = index(t) / index(t-24) - 1; rise12 and rise36 likewise.
- "Lasting" flag: rise12 > 0 and index(t) >= 0.97 * (highest index of the last 24 months), i.e. the price
  is still at its top and has not fallen back like a short spike.
- Now: the 40 lasting series with the largest rise24 (same title shown once), plus the median rise24.
- Look back (descriptive, no pass/fail yet): the same ranking as of December 2019..2024, top 15 each,
  so a reader can see whether known deficits were visible in time.
- Illustration only: percentile of series whose title contains a few known words (transformer, semiconductor,
  lumber, eggs, fertilizer, natural gas, copper, switchgear, turbine). These words do not affect the ranking.
- A product at the top is a QUESTION, not an answer: the price can rise because of a tax, a one-off event
  or a change in the index. Whether it is a durable deficit is decided by the four features of the case table
  (physical limit, hard-to-reverse decision, running capacity, binding buyer).

The run also records which other public sources answer from Actions (for the next streams).
No OpenAlex credits. Usage: python -m mashina.radar
"""
import json
import os
import re
import statistics
import time
import urllib.request

UA = {"User-Agent": "mashina-research/0.1 (mashina-bot@users.noreply.github.com)"}
BLS = "https://download.bls.gov/pub/time.series/wp/"
WATCH = ["transformer", "semiconductor", "softwood lumber", "eggs", "fertilizer", "natural gas", "copper",
         "switchgear", "turbine"]
FIRST_YEAR = 2016


def fetch(url, timeout=180):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)


def probe(url, data=None, headers=None):
    t = time.time()
    try:
        h = dict(UA)
        h.update(headers or {})
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=60) as r:
            b = r.read(3000)
            return {"status": r.status, "seconds": round(time.time() - t, 1), "sample": b[:300].decode("utf-8", "replace")}
    except Exception as e:
        return {"status": "error", "seconds": round(time.time() - t, 1), "sample": repr(e)[:200]}


def load_series():
    titles = {}
    with fetch(BLS + "wp.series") as r:
        for i, raw in enumerate(r):
            p = [x.strip() for x in raw.decode("utf-8", "replace").split("\t")]
            if i == 0 or len(p) < 6:
                continue
            if p[0].startswith("WPU"):
                titles[p[0]] = p[5]
    return titles


def load_data(name, data, keep):
    n = 0
    with fetch(BLS + name, timeout=600) as r:
        for i, raw in enumerate(r):
            p = raw.decode("utf-8", "replace").split("\t")
            if i == 0 or len(p) < 4:
                continue
            sid = p[0].strip()
            if sid not in keep:
                continue
            per = p[2].strip()
            if not per.startswith("M") or per == "M13":
                continue
            try:
                y, m, v = int(p[1]), int(per[1:]), float(p[3])
            except ValueError:
                continue
            if y >= FIRST_YEAR:
                data.setdefault(sid, {})[y * 12 + m - 1] = v
                n += 1
    return n


def snapshot(data, titles, t):
    rows = []
    for sid, d in data.items():
        v, v12, v24 = d.get(t), d.get(t - 12), d.get(t - 24)
        if not v or not v12 or not v24:
            continue
        window = [d[k] for k in range(t - 23, t + 1) if k in d]
        v36 = d.get(t - 36)
        rows.append({"id": sid, "title": titles.get(sid, sid), "rise24": v / v24 - 1, "rise12": v / v12 - 1,
                     "rise36": (v / v36 - 1) if v36 else None,
                     "lasting": (v / v12 - 1) > 0 and v >= 0.97 * max(window)})
    rows.sort(key=lambda r: -r["rise24"])
    n = len(rows)
    for i, r in enumerate(rows):
        r["pct"] = round(100 * (1 - i / max(n - 1, 1)), 1)
    return rows


def top(rows, k, lasting_only=True):
    out, seen = [], set()
    for r in rows:
        if lasting_only and not r["lasting"]:
            continue
        key = r["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
        if len(out) == k:
            break
    return out


def ym(t):
    return f"{t // 12}-{t % 12 + 1:02d}"


def main():
    out = {"sources": {}, "run": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}
    out["sources"]["eurostat_ppi"] = probe("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sts_inpp_m"
                                           "?format=JSON&geo=EU27_2020&sinceTimePeriod=2025-01&nace_r2=C27")
    out["sources"]["worldbank_pink"] = probe("https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/"
                                             "related/CMO-Historical-Data-Monthly.xlsx")
    out["sources"]["stooq"] = probe("https://stooq.com/q/d/l/?s=xlu.us&i=m")
    out["sources"]["federal_register"] = probe("https://www.federalregister.gov/api/v1/documents.json?per_page=1"
                                               "&conditions[type][]=RULE&conditions[publication_date][gte]=2026-10-01")
    out["sources"]["eurlex_rss"] = probe("https://eur-lex.europa.eu/EN/display-feed.rss?rssId=162")
    out["sources"]["comext_bulk"] = probe("https://ec.europa.eu/eurostat/api/dissemination/files/?sort=1&dir=comext%2FCOMEXT_DATA%2FPRODUCTS")
    try:
        titles = load_series()
        data = {}
        rows_read = load_data("wp.data.0.Current", data, titles)
        months = sorted({k for d in data.values() for k in d})
        out["bls"] = {"series": len(titles), "rows": rows_read, "first": ym(months[0]), "last": ym(months[-1])}
        if months[0] > 2017 * 12:  # the "Current" file is too short: read the full files by product group
            listing = fetch(BLS).read().decode("utf-8", "replace")
            names = sorted(set(re.findall(r"wp\.data\.\d+\.[A-Za-z0-9_\-]+", listing)) - {"wp.data.0.Current"})
            for nm in names:
                try:
                    rows_read += load_data(nm, data, titles)
                except Exception as e:
                    out["bls"].setdefault("failed", []).append(nm + " " + repr(e)[:80])
            months = sorted({k for d in data.values() for k in d})
            out["bls"].update({"rows": rows_read, "first": ym(months[0]), "last": ym(months[-1]), "files": len(names) + 1})
        count = {t: sum(1 for d in data.values() if t in d) for t in months[-14:]}
        full = max(count.values())
        now = max(t for t, c in count.items() if c >= 0.7 * full)
        snap = snapshot(data, titles, now)
        out["now"] = {"month": ym(now), "series": len(snap), "median_rise24": round(statistics.median(r["rise24"] for r in snap), 4),
                      "lasting_share": round(sum(r["lasting"] for r in snap) / len(snap), 3),
                      "top": top(snap, 40), "top_any": top(snap, 15, lasting_only=False)}
        out["lookback"] = {}
        for y in range(2019, 2025):
            t = y * 12 + 11
            s = snapshot(data, titles, t)
            if not s:
                continue
            w = {}
            for word in WATCH:
                m = [r for r in s if word in r["title"].lower()]
                if m:
                    w[word] = {"n": len(m), "median_pct": round(statistics.median(r["pct"] for r in m), 1),
                               "best_pct": max(r["pct"] for r in m), "median_rise24": round(statistics.median(r["rise24"] for r in m), 3)}
            out["lookback"][str(y)] = {"series": len(s), "median_rise24": round(statistics.median(r["rise24"] for r in s), 4),
                                       "top": top(s, 15), "watch": w}
        w = {}
        for word in WATCH:
            m = [r for r in snap if word in r["title"].lower()]
            if m:
                w[word] = {"n": len(m), "median_pct": round(statistics.median(r["pct"] for r in m), 1),
                           "best_pct": max(r["pct"] for r in m), "median_rise24": round(statistics.median(r["rise24"] for r in m), 3)}
        out["now"]["watch"] = w
    except Exception as e:
        out["bls_error"] = repr(e)[:400]
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/radar.json", "w"), ensure_ascii=False, indent=0)

    L = ["# Радар: где цены говорят о дефиците", "",
         f"Запуск {out['run']}. Работает по расписанию в GitHub Actions, без участия Claude. Правило записано в `mashina/radar.py`.", ""]
    if "now" in out:
        n = out["now"]
        L += [f"Источник: индекс цен производителей США (BLS), {n['series']} рядов без сезонной поправки, месяц {n['month']}.",
              f"Медианный рост за 24 месяца: {100 * n['median_rise24']:.1f}%. Доля рядов с флагом «держится»: {100 * n['lasting_share']:.0f}%.",
              "Верх списка — это вопрос «почему?», а не ответ: цена растёт и из-за пошлин, разовых событий, пересчёта индекса.", "",
              "## Сейчас: 40 рядов с наибольшим ростом за 24 месяца, которые держатся у максимума", "",
              "| Товар (название BLS) | 24 мес. | 12 мес. | 36 мес. |", "|---|---|---|---|"]
        for r in n["top"]:
            r36 = f"{100 * r['rise36']:+.0f}%" if r["rise36"] is not None else "—"
            L.append(f"| {r['title']} | {100 * r['rise24']:+.0f}% | {100 * r['rise12']:+.0f}% | {r36} |")
        L += ["", "## Взгляд назад: что было наверху в декабре каждого года", ""]
        for y, s in out["lookback"].items():
            L += [f"**Декабрь {y}** (медиана {100 * s['median_rise24']:+.1f}%): "
                  + "; ".join(f"{r['title']} {100 * r['rise24']:+.0f}%" for r in s["top"]), ""]
        L += ["## Иллюстрация: где стояли знакомые товары (процентиль по росту за 24 месяца, 100 = самый верх)", "",
              "| Слово в названии | " + " | ".join(out["lookback"].keys()) + " | сейчас |", "|---|" + "---|" * (len(out["lookback"]) + 1)]
        for word in WATCH:
            cells = [str(s["watch"].get(word, {}).get("median_pct", "—")) for s in out["lookback"].values()]
            cells.append(str(n["watch"].get(word, {}).get("median_pct", "—")))
            L.append(f"| {word} | " + " | ".join(cells) + " |")
    else:
        L += ["Данные BLS не загрузились: " + out.get("bls_error", "?"), ""]
    L += ["", "## Какие источники отвечают с GitHub (для следующих потоков)", "", "| Источник | Ответ |", "|---|---|"]
    L += [f"| {k} | {v['status']} |" for k, v in out["sources"].items()]
    open("reports/radar.md", "w").write("\n".join(L) + "\n")
    print(json.dumps({k: out.get(k) for k in ("bls", "bls_error")}, ensure_ascii=False))
    print({k: v["status"] for k, v in out["sources"].items()})
    if "now" in out:
        print(out["now"]["month"], out["now"]["series"], out["now"]["median_rise24"])


if __name__ == "__main__":
    main()
