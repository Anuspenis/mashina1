"""Check which free market-side sources answer from GitHub Actions (no OpenAlex credits).
Writes reports/probe.json with status, a sample of the response and timing.
Usage: python -m mashina.probe_sources
"""
import json
import os
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "mashina research (github.com/Anuspenis/mashina1)"}


def fetch(url, data=None, headers=None, timeout=60):
    h = dict(UA)
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", "replace")
            return {"status": r.status, "seconds": round(time.time() - t, 1), "sample": body[:1500]}
    except Exception as e:  # record any failure
        return {"status": "error", "seconds": round(time.time() - t, 1), "error": repr(e)[:500]}


def main():
    out = {}
    q = '"carbon border" (shortage OR bottleneck OR delay)'
    out["gdelt_timeline"] = fetch("https://api.gdeltproject.org/api/v2/doc/doc?" + urllib.parse.urlencode(
        {"query": q, "mode": "timelinevolraw", "format": "json", "timespan": "3months"}))
    time.sleep(6)
    out["gdelt_artlist"] = fetch("https://api.gdeltproject.org/api/v2/doc/doc?" + urllib.parse.urlencode(
        {"query": '"power transformer" shortage', "mode": "artlist", "format": "json", "maxrecords": 5, "timespan": "12months"}))
    for i, body in enumerate([
            {"query": 'FT~"carbon border"', "fields": ["publication-number", "notice-title"], "limit": 2},
            {"query": 'notice-title~"transformer"', "fields": ["publication-number", "notice-title"], "limit": 2}]):
        out[f"ted_{i}"] = fetch("https://api.ted.europa.eu/v3/notices/search", data=json.dumps(body).encode(),
                                headers={"Content-Type": "application/json"})
    out["wiki_pageviews"] = fetch(
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
        "Carbon_Border_Adjustment_Mechanism/monthly/20250101/20261031")
    tok = os.environ.get("GITHUB_TOKEN", "")
    out["github_negative"] = fetch("https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": "cbam carbon NOT attention", "per_page": 1}),
        headers={"Authorization": "Bearer " + tok, "Accept": "application/vnd.github+json"})
    out["crossref"] = fetch("https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query.bibliographic": "carbon border adjustment", "filter": "from-pub-date:2023-01-01", "rows": 0}))
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/probe.json", "w"), ensure_ascii=False, indent=1)
    for k, v in out.items():
        print(k, v.get("status"), v.get("seconds"), (v.get("sample") or v.get("error") or "")[:200].replace("\n", " "))


if __name__ == "__main__":
    main()
