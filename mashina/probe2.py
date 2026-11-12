"""Second probe (13.11.2026): market-side sources for the screen.
SEC full-text search (firms' own filings), Prozorro (Ukrainian public procurement),
TED by CPV code (language-independent), Jobnet (Danish job ads), SIPRI-free check skipped.
Usage: python -m mashina.probe2
"""
import json
import os
import time
import urllib.parse
import urllib.request

SEC_UA = "mashina research mashina-bot@users.noreply.github.com"


def get(url, data=None, headers=None, timeout=60):
    h = {"User-Agent": "mashina research (github.com/Anuspenis/mashina1)"}
    h.update(headers or {})
    t = time.time()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=timeout) as r:
            body = r.read().decode("utf-8", "replace")
            return {"status": r.status, "seconds": round(time.time() - t, 1), "body": body}
    except Exception as e:
        return {"status": "error", "seconds": round(time.time() - t, 1), "body": repr(e)[:400]}


def main():
    out = {}
    for name, q in [("sec_grid", '"interconnection queue"'), ("sec_grid_short", '"transformer" "lead time"'),
                    ("sec_cbam", '"carbon border adjustment"')]:
        r = get("https://efts.sec.gov/LATEST/search-index?" + urllib.parse.urlencode(
            {"q": q, "dateRange": "custom", "startdt": "2025-01-01", "enddt": "2026-11-12"}),
            headers={"User-Agent": SEC_UA})
        try:
            j = json.loads(r["body"]); r["total"] = j.get("hits", {}).get("total"); r["body"] = r["body"][:300]
        except Exception:
            r["body"] = r["body"][:300]
        out[name] = r
        time.sleep(1)
    for name, url in [("prozorro_search", "https://prozorro.gov.ua/api/search/tenders?" + urllib.parse.urlencode({"text": "трансформатор"})),
                      ("prozorro_public", "https://public.api.openprocurement.org/api/2.5/tenders?limit=1")]:
        r = get(url); r["body"] = r["body"][:400]; out[name] = r
    for i, q in enumerate(["classification-cpv=31170000 AND PD>=20250101", "PC=31170000 AND PD>=20250101"]):
        r = get("https://api.ted.europa.eu/v3/notices/search",
                data=json.dumps({"query": q, "fields": ["publication-number"], "limit": 1}).encode(),
                headers={"Content-Type": "application/json"})
        try:
            r["total"] = json.loads(r["body"]).get("totalNoticeCount")
        except Exception:
            pass
        r["body"] = r["body"][:300]
        out[f"ted_cpv_{i}"] = r
    for name, url in [("jobnet", "https://job.jobnet.dk/CV/FindWork/Search?" + urllib.parse.urlencode({"Offset": 0, "SearchString": "CBAM"})),
                      ("jobnet_alt", "https://job.jobnet.dk/CV/FindWork/Search?SearchString=compliance")]:
        r = get(url, headers={"Accept": "application/json"}); r["body"] = r["body"][:400]; out[name] = r
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/probe2.json", "w"), ensure_ascii=False, indent=1)
    for k, v in out.items():
        print(k, v.get("status"), v.get("total"), v["body"][:160].replace("\n", " "))


if __name__ == "__main__":
    main()
