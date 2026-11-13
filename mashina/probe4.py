"""Probe 4 (13.11.2026): audit of probe 3. What do the CPV codes of the tender test really contain?

Reason: in probe 3 the codes were taken from memory and never spot-checked, although the rule
"read 20 results by hand" was written for word searches the same day. This probe pulls sample
titles per code so precision can be read by eye. It also retries Prozorro search with POST
(probe 2 used GET and got 405 Method Not Allowed).
No decision rule here: this is a check of an earlier measurement. No OpenAlex credits.
Usage: python -m mashina.probe4
"""
import json
import os
import time
import urllib.parse
import urllib.request

from mashina.probe3 import CODES, TED, UA, cpv_clause, window


def post(url, body, headers=None, timeout=90):
    h = {**UA, "Content-Type": "application/json"}
    h.update(headers or {})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode(), headers=h),
                                    timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return "error", repr(e)[:300]


def title(n):
    t = n.get("notice-title")
    if isinstance(t, dict):
        return (t.get("eng") or next(iter(t.values()), ""))[:160]
    return str(t)[:160]


def main():
    out = {"samples": {}, "prozorro": {}}
    for name, (codes, label) in CODES.items():
        st, txt = post(TED, {"query": f"{cpv_clause(codes)} AND {window('early')}",
                             "fields": ["publication-number", "notice-title", "buyer-country", "classification-cpv"],
                             "limit": 20})
        try:
            j = json.loads(txt)
            out["samples"][name] = {"label": label, "total": j.get("totalNoticeCount"),
                                    "titles": [[n.get("buyer-country"), n.get("classification-cpv"), title(n)]
                                               for n in j.get("notices", [])]}
        except Exception:
            out["samples"][name] = {"status": st, "body": txt[:300]}
        time.sleep(0.7)
    q = urllib.parse.urlencode({"text": "трансформатор"})
    for key, url, body in [("post_json", "https://prozorro.gov.ua/api/search/tenders", {"text": "трансформатор"}),
                           ("post_query", "https://prozorro.gov.ua/api/search/tenders?" + q, {})]:
        st, txt = post(url, body)
        out["prozorro"][key] = {"status": st, "body": txt[:500]}
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/probe4.json", "w"), ensure_ascii=False, indent=1)
    for k, v in out["samples"].items():
        print(k, v.get("total"), len(v.get("titles", [])))
    print(out["prozorro"])


if __name__ == "__main__":
    main()
