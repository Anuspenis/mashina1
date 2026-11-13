"""Probe 3 (13.11.2026): is the EU-tender sensor worth anything, and where does the money go by country.

PRE-REGISTERED before any result (13.11.2026, before the run):

Test A - does the tender sensor tell windfalls from flops?
- Sensor S(code, window) = share of all TED notices in that window that carry the CPV code(s),
  divided by the same share in 2019-01-01..2020-12-31. S > 1 means the state buys more of it.
- Windows: early = 2021-01-01..2022-12-31 (what we would have seen in time), late = 2023-01-01..2024-12-31.
- Labels fixed now from public outcomes 2021->2025 for European suppliers; only clear cases:
  windfalls: high-voltage cable (Prysmian/NKT/Nexans), transformers (multi-year lead times),
             ammunition (Rheinmetall, CSG), armoured vehicles, unmanned aerial vehicles
  flops:     hydrogen (Nel, ITM, Plug -80..-95%), heat pumps (EU sales fall 2023-24), wind (Orsted, Siemens Gamesa),
             batteries (Northvolt bankrupt), solar PV modules (EU makers insolvent while installs boomed)
- AUC = share of the 25 windfall/flop pairs where S(windfall) > S(flop) (ties count 1/2), early window.
- Rule for screen v3: AUC >= 0.75 -> tender sensor keeps full weight; 0.60 < AUC < 0.75 -> half weight;
  AUC <= 0.60 -> weight 0 (the sensor measures state money, not windfalls).
- The late window is reported but does not decide anything (by then the outcome was already visible).

Test B - country split (descriptive, no decision):
- Notices 2025-01-01..2026-11-12 carrying the windfall codes, by buyer country, and the country's share of
  those notices divided by its share of all notices (specialisation index; > 1 = buys more of it than its size).

Also: which TED fields return money values, and whether EURES (EU job ads) answers from Actions.
No OpenAlex credits. Usage: python -m mashina.probe3
"""
import json
import os
import time
import urllib.request

TED = "https://api.ted.europa.eu/v3/notices/search"
UA = {"User-Agent": "mashina research (github.com/Anuspenis/mashina1)"}

CODES = {  # name: (list of CPV codes, label)
    "hv_cable": (["31321300"], "windfall"),
    "transformers": (["31170000"], "windfall"),
    "ammunition": (["35330000"], "windfall"),
    "armoured_vehicles": (["35410000", "35412000"], "windfall"),
    "uav": (["35613000"], "windfall"),
    "hydrogen": (["24111600"], "flop"),
    "heat_pumps": (["42511110"], "flop"),
    "wind": (["31121320", "31121340"], "flop"),
    "batteries": (["31440000"], "flop"),
    "pv_modules": (["09331200"], "flop"),
}
WINDOWS = {"base": ("20190101", "20201231"), "early": ("20210101", "20221231"),
           "late": ("20230101", "20241231"), "now": ("20250101", "20261112")}
COUNTRIES = ["POL", "CZE", "SVK", "LTU", "LVA", "EST", "ROU", "BGR", "HUN", "DEU", "FRA", "ITA", "ESP",
             "NLD", "BEL", "DNK", "SWE", "FIN", "NOR", "AUT", "PRT", "GRC", "IRL", "HRV", "UKR"]


def post(body, timeout=90):
    req = urllib.request.Request(TED, data=json.dumps(body).encode(),
                                 headers={**UA, "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return 200, json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            err = repr(e)[:300]
            time.sleep(3 * (attempt + 1))
    return "error", err


def count(query):
    st, j = post({"query": query, "fields": ["publication-number"], "limit": 1})
    time.sleep(0.6)
    return j.get("totalNoticeCount") if st == 200 else None


def cpv_clause(codes):
    return "(" + " OR ".join(f"classification-cpv={c}" for c in codes) + ")"


def window(w):
    a, b = WINDOWS[w]
    return f"PD>={a} AND PD<={b}"


def main():
    out = {"fields": {}, "totals": {}, "counts": {}, "country": {}, "eures": None}
    # field discovery
    for f in ["buyer-country", "total-value", "estimated-value-glo", "estimated-value-proc",
              "result-value-notice", "notice-type"]:
        st, j = post({"query": "classification-cpv=31170000 AND PD>=20250101",
                      "fields": ["publication-number", f], "limit": 2})
        out["fields"][f] = {"status": st, "sample": (j.get("notices") if st == 200 else j)}
        time.sleep(0.6)
    # Test A
    for w in WINDOWS:
        out["totals"][w] = count(window(w))
    for name, (codes, label) in CODES.items():
        out["counts"][name] = {"label": label}
        for w in WINDOWS:
            out["counts"][name][w] = count(f"{cpv_clause(codes)} AND {window(w)}")
    res = {}
    for name, d in out["counts"].items():
        try:
            base = d["base"] / out["totals"]["base"]
            res[name] = {k: round((d[k] / out["totals"][k]) / base, 3) for k in ("early", "late", "now")}
        except Exception:
            res[name] = None
    out["S"] = res

    def auc(key):
        wf = [res[n][key] for n, (c, l) in CODES.items() if l == "windfall" and res.get(n)]
        fl = [res[n][key] for n, (c, l) in CODES.items() if l == "flop" and res.get(n)]
        if not wf or not fl:
            return None
        s = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in wf for b in fl)
        return round(s / (len(wf) * len(fl)), 3), len(wf), len(fl)
    out["AUC_early"], out["AUC_late"], out["AUC_now"] = auc("early"), auc("late"), auc("now")
    a = out["AUC_early"][0] if out["AUC_early"] else None
    out["verdict"] = None if a is None else ("full weight" if a >= 0.75 else "half weight" if a > 0.60 else "weight 0")
    # Test B
    wcodes = sum((c for c, l in CODES.values() if l == "windfall"), [])
    wf_all = count(f"{cpv_clause(wcodes)} AND {window('now')}")
    for cc in COUNTRIES:
        tot = count(f"buyer-country={cc} AND {window('now')}")
        wf = count(f"buyer-country={cc} AND {cpv_clause(wcodes)} AND {window('now')}")
        out["country"][cc] = {"all": tot, "windfall_codes": wf}
    allnow = out["totals"]["now"]
    for cc, d in out["country"].items():
        try:
            d["specialisation"] = round((d["windfall_codes"] / wf_all) / (d["all"] / allnow), 2)
        except Exception:
            d["specialisation"] = None
    out["windfall_codes_all_now"] = wf_all
    # EURES job ads
    try:
        body = {"resultsPerPage": 1, "page": 1, "sortSearch": "BEST_MATCH",
                "keywords": [{"keyword": "CBAM", "specificSearchCode": "EVERYWHERE"}],
                "publicationPeriod": None, "occupationUris": [], "skillUris": [], "requiredExperienceCodes": [],
                "positionScheduleCodes": [], "sectorCodes": [], "educationAndQualificationLevelCodes": [],
                "positionOfferingCodes": [], "locationCodes": [], "euresFlagCodes": [], "otherBenefitsCodes": [],
                "requiredLanguages": [], "minNumberPost": None, "sessionId": "mashina"}
        req = urllib.request.Request("https://europa.eu/eures/eures-apps/searchengine/page/jv-search/search",
                                     data=json.dumps(body).encode(),
                                     headers={**UA, "Content-Type": "application/json", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode("utf-8", "replace")
            out["eures"] = {"status": r.status, "sample": txt[:400]}
    except Exception as e:
        out["eures"] = {"status": "error", "sample": repr(e)[:300]}
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/probe3.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("totals", "S", "AUC_early", "AUC_late", "AUC_now", "verdict")}, indent=1))
    print(json.dumps(out["country"], indent=0))
    print("eures", out["eures"])


if __name__ == "__main__":
    main()
