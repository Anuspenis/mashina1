"""Radar v0 (13.11.2026): a scan that runs on a schedule in GitHub Actions and needs no Claude.

Question it serves: where is the sharpest deficit or the biggest boom, without a hand-written list of niches.
A sharp and lasting price rise across a product line is the most direct public trace of a deficit:
buyers pay more and supply does not catch up.

STREAMS (each takes a COMPLETE public list, nothing is picked by hand):
 A. EU producer prices by industry (Eurostat sts_inpp_m, monthly, every industry code published).
 B. World commodity prices (World Bank "Pink Sheet", monthly, every commodity in the sheet).
 C. US producer prices by product (BLS, about 3,700 product lines) - the richest list, but BLS refuses
    requests from GitHub servers without a registered key; kept in the code and reported as "no access".

RULE (written before the first run, same for every stream):
- At month t: rise24 = price(t) / price(t-24) - 1; rise12 and rise36 likewise.
- "Lasting" flag: rise12 > 0 and price(t) >= 0.97 * (highest price of the last 24 months), i.e. the price
  is still at its top and has not fallen back like a short spike.
- Now: the lasting series with the largest rise24 (same title shown once), plus the median rise24.
- Look back (descriptive, no pass/fail yet): the same ranking as of December 2019..2024,
  so a reader can see whether known deficits were visible in time.
- Stream B also lists EPISODES by rule: every time since 2000 a commodity stood at 2x or more of its lowest
  price of the previous 24 months. This is a rule-made list of price shocks for the case table.
- A line at the top is a QUESTION, not an answer: a price can rise because of a tax, a one-off event or a
  change in the index. Whether it is a durable deficit is decided by the four features of the case table
  (physical limit, hard-to-reverse decision, running capacity, binding buyer).

The run also records which other public sources answer from Actions (for the next streams).
No OpenAlex credits. Usage: python -m mashina.radar
"""
import io
import json
import os
import re
import statistics
import time
import urllib.request

UA = {"User-Agent": "mashina-research/0.1 (mashina-bot@users.noreply.github.com)"}
BLS = "https://download.bls.gov/pub/time.series/wp/"
EUROSTAT = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sts_inpp_m"
            "?format=JSON&geo=EU27_2020&sinceTimePeriod=2016-01")
PINK = ("https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/"
        "related/CMO-Historical-Data-Monthly.xlsx")
FIRST_YEAR = 2016


def fetch(url, timeout=180):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)


def probe(url):
    t = time.time()
    try:
        with fetch(url, timeout=60) as r:
            b = r.read(3000)
            return {"status": r.status, "seconds": round(time.time() - t, 1), "sample": b[:300].decode("utf-8", "replace")}
    except Exception as e:
        return {"status": "error", "seconds": round(time.time() - t, 1), "sample": repr(e)[:200]}


def ym(t):
    return f"{t // 12}-{t % 12 + 1:02d}"


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


def latest_month(data):
    months = sorted({k for d in data.values() for k in d})
    count = {t: sum(1 for d in data.values() if t in d) for t in months[-14:]}
    full = max(count.values())
    return max(t for t, c in count.items() if c >= 0.7 * full), months


def summarise(data, titles, k_now, k_back):
    now, months = latest_month(data)
    snap = snapshot(data, titles, now)
    res = {"month": ym(now), "first": ym(months[0]), "series": len(snap),
           "median_rise24": round(statistics.median(r["rise24"] for r in snap), 4),
           "lasting_share": round(sum(r["lasting"] for r in snap) / len(snap), 3),
           "top": top(snap, k_now), "lookback": {}}
    for y in range(2019, 2025):
        s = snapshot(data, titles, y * 12 + 11)
        if s:
            res["lookback"][str(y)] = {"series": len(s), "median_rise24": round(statistics.median(r["rise24"] for r in s), 4),
                                       "top": top(s, k_back)}
    return res


# ---------- stream A: Eurostat producer prices by industry ----------
def parse_jsonstat(j):
    ids, size = j["id"], j["size"]
    cats = {d: j["dimension"][d]["category"] for d in ids}
    pick = {}
    for d in ids:
        idx = cats[d]["index"]
        codes = sorted(idx, key=lambda c: idx[c]) if isinstance(idx, dict) else list(idx)
        if d in ("nace_r2", "time"):
            continue
        if len(codes) == 1:
            pick[d] = codes[0]
        elif d == "unit":
            pick[d] = next((c for c in ("I21", "I15", "I10") if c in codes), next((c for c in codes if c.startswith("I")), codes[0]))
        elif d == "s_adj":
            pick[d] = "NSA" if "NSA" in codes else codes[0]
        else:
            pick[d] = codes[0]
    mult, m = {}, 1
    for d, s in zip(reversed(ids), reversed(size)):
        mult[d] = m
        m *= s
    pos = lambda d, c: (cats[d]["index"][c] if isinstance(cats[d]["index"], dict) else cats[d]["index"].index(c))
    base = sum(pos(d, c) * mult[d] for d, c in pick.items())
    val = j["value"]
    get = (lambda i: val.get(str(i))) if isinstance(val, dict) else (lambda i: val[i] if i < len(val) else None)
    nace = cats["nace_r2"]["index"]
    tcat = cats["time"]["index"]
    data, titles = {}, {}
    for code in (nace if isinstance(nace, dict) else list(nace)):
        d = {}
        for tc in (tcat if isinstance(tcat, dict) else list(tcat)):
            v = get(base + pos("nace_r2", code) * mult["nace_r2"] + pos("time", tc) * mult["time"])
            if v is not None:
                y, mth = tc.split("-")[0], tc.split("-")[1].lstrip("M")
                d[int(y) * 12 + int(mth) - 1] = float(v)
        if d:
            data[code] = d
            titles[code] = cats["nace_r2"].get("label", {}).get(code, code) + f" [{code}]"
    return data, titles, pick


def stream_eu():
    with fetch(EUROSTAT, timeout=300) as r:
        j = json.load(r)
    data, titles, pick = parse_jsonstat(j)
    res = summarise(data, titles, 30, 10)
    res["picked"] = pick
    res["updated"] = j.get("updated")
    return res


# ---------- stream B: World Bank commodity prices ----------
def stream_commodities():
    import openpyxl
    with fetch(PINK, timeout=300) as r:
        wb = openpyxl.load_workbook(io.BytesIO(r.read()), read_only=True, data_only=True)
    ws = wb["Monthly Prices"] if "Monthly Prices" in wb.sheetnames else wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    first = next(i for i, row in enumerate(rows) if row and isinstance(row[0], str) and re.match(r"^\d{4}M\d{2}$", row[0].strip()))
    head = max(range(max(0, first - 6), first), key=lambda i: sum(1 for c in rows[i] if isinstance(c, str) and c.strip()))
    names = [str(c).strip() if c else None for c in rows[head]]
    data = {}
    for row in rows[first:]:
        if not row or not isinstance(row[0], str) or not re.match(r"^\d{4}M\d{2}$", row[0].strip()):
            continue
        t = int(row[0][:4]) * 12 + int(row[0][5:7]) - 1
        for c, name in enumerate(names):
            if c == 0 or not name or c >= len(row):
                continue
            v = row[c]
            if isinstance(v, (int, float)) and v > 0:
                data.setdefault(name, {})[t] = float(v)
    titles = {k: k for k in data}
    res = summarise(data, titles, 25, 8)
    # episodes by rule: price at 2x or more of the lowest price of the previous 24 months, since 2000
    episodes = []
    for name, d in data.items():
        cur = None
        for t in sorted(k for k in d if k >= 2000 * 12):
            prev = [d[k] for k in range(t - 24, t) if k in d]
            mult = d[t] / min(prev) if prev else 0
            if mult >= 2.0:
                if cur is None:
                    cur = {"commodity": name, "start": ym(t), "peak_mult": mult, "peak": ym(t)}
                elif mult > cur["peak_mult"]:
                    cur["peak_mult"], cur["peak"] = mult, ym(t)
                cur["end"] = ym(t)
            elif cur is not None:
                episodes.append(cur)
                cur = None
        if cur is not None:
            cur["open"] = True
            episodes.append(cur)
    for e in episodes:
        e["peak_mult"] = round(e["peak_mult"], 2)
    res["episodes"] = sorted(episodes, key=lambda e: e["start"])
    res["commodities"] = len(data)
    return res


# ---------- stream C: US producer prices by product (needs access BLS does not give to GitHub servers) ----------
def stream_bls():
    titles = {}
    with fetch(BLS + "wp.series") as r:
        for i, raw in enumerate(r):
            p = [x.strip() for x in raw.decode("utf-8", "replace").split("\t")]
            if i and len(p) >= 6 and p[0].startswith("WPU"):
                titles[p[0]] = p[5]
    data = {}
    with fetch(BLS + "wp.data.0.Current", timeout=600) as r:
        for i, raw in enumerate(r):
            p = raw.decode("utf-8", "replace").split("\t")
            if not i or len(p) < 4 or p[0].strip() not in titles:
                continue
            per = p[2].strip()
            if per.startswith("M") and per != "M13" and int(p[1]) >= FIRST_YEAR:
                try:
                    data.setdefault(p[0].strip(), {})[int(p[1]) * 12 + int(per[1:]) - 1] = float(p[3])
                except ValueError:
                    pass
    return summarise(data, titles, 40, 15)


def md_stream(L, title, src, s, k=None):
    L += ["", f"## {title}", "",
          f"{src} Рядов: {s['series']}, месяц {s['month']}. Медианный рост за 24 месяца: {100 * s['median_rise24']:+.1f}%. "
          f"Держатся у максимума: {100 * s['lasting_share']:.0f}% рядов.", "",
          "| Что подорожало и держится | 24 мес. | 12 мес. | 36 мес. |", "|---|---|---|---|"]
    for r in s["top"][:k]:
        r36 = f"{100 * r['rise36']:+.0f}%" if r["rise36"] is not None else "—"
        L.append(f"| {r['title']} | {100 * r['rise24']:+.0f}% | {100 * r['rise12']:+.0f}% | {r36} |")
    L += ["", "Взгляд назад, верх списка в декабре каждого года:", ""]
    for y, b in s["lookback"].items():
        L.append(f"- **{y}** (медиана {100 * b['median_rise24']:+.1f}%): "
                 + "; ".join(f"{r['title']} {100 * r['rise24']:+.0f}%" for r in b["top"]))


def main():
    out = {"sources": {}, "run": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}
    for name, url in [("federal_register", "https://www.federalregister.gov/api/v1/documents.json?per_page=1&conditions[type][]=RULE"
                                           "&conditions[publication_date][gte]=2026-10-01"),
                      ("eurlex_rss", "https://eur-lex.europa.eu/EN/display-feed.rss?rssId=162"),
                      ("comext_bulk", "https://ec.europa.eu/eurostat/api/dissemination/files/?sort=1&dir=comext%2FCOMEXT_DATA%2FPRODUCTS")]:
        out["sources"][name] = probe(url)
    for key, fn in [("eu", stream_eu), ("commodities", stream_commodities), ("bls", stream_bls)]:
        try:
            out[key] = fn()
            out["sources"][key] = {"status": 200}
        except Exception as e:
            out[key + "_error"] = repr(e)[:300]
            out["sources"][key] = {"status": "error: " + repr(e)[:80]}
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/radar.json", "w"), ensure_ascii=False, indent=0)

    L = ["# Радар: где цены говорят о дефиците", "",
         f"Запуск {out['run']}. Работает сам, по расписанию в GitHub Actions, каждую неделю. Правило записано в `mashina/radar.py`.",
         "Списки полные, ни один товар не выбран вручную. Строка наверху — это вопрос «почему?», а не ответ:",
         "цена растёт и из-за пошлин, разовых событий, пересчёта индекса."]
    if "eu" in out:
        md_stream(L, "А. Цены производителей ЕС по отраслям", "Источник: Eurostat, все опубликованные коды отраслей.", out["eu"])
    if "commodities" in out:
        md_stream(L, "Б. Мировые цены на сырьё", "Источник: Всемирный банк, все товары таблицы.", out["commodities"])
        ep = out["commodities"]["episodes"]
        L += ["", f"### Эпизоды по правилу: цена в 2 раза и больше выше минимума за предыдущие 24 месяца (с 2000 года, всего {len(ep)})", "",
              "| Товар | Начало | Пик | Во сколько раз | Конец |", "|---|---|---|---|---|"]
        for e in ep:
            L.append(f"| {e['commodity']} | {e['start']} | {e['peak']} | {e['peak_mult']} | {'идёт сейчас' if e.get('open') else e['end']} |")
    if "bls" in out:
        md_stream(L, "В. Цены производителей США по товарам", "Источник: BLS.", out["bls"])
    L += ["", "## Источники", "", "| Источник | Ответ |", "|---|---|"]
    L += [f"| {k} | {v['status']} |" for k, v in out["sources"].items()]
    open("reports/radar.md", "w").write("\n".join(L) + "\n")
    print({k: v["status"] for k, v in out["sources"].items()})
    for k in ("eu", "commodities"):
        if k in out:
            print(k, out[k]["month"], out[k]["series"], out[k]["median_rise24"], [r["title"][:40] for r in out[k]["top"][:5]])
        else:
            print(k, out.get(k + "_error"))


if __name__ == "__main__":
    main()
