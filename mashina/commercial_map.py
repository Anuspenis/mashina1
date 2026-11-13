"""Commercial-science map of ALL sciences (13.11.2026). Produced by a rule, not by a hand-written list.

Why: the author asked several times to look at all sciences and at commercial science. Every niche list
so far (9, 20, 144) was written by Claude from memory. This is the first list that comes from a rule
applied to the whole classification, so it can show what the hand-written lists left out.

RULE (written before the run):
- Units: every OpenAlex subfield (about 250) and every topic (about 4,500), by a work's primary topic.
- Years 2019, 2022, 2025: all works and works with at least one author from a company.
- share = company works / all works. Reported per unit: share in 2025, change 2019->2025 in percentage
  points, ratio share2025/share2019, company works in 2025.
- Units with few company works in 2025 (subfields < 200, topics < 50) are kept but marked "small".
- No weights and no score. DESCRIPTIVE ONLY: this sensor has not been checked on cases with a known
  outcome, so it must not rank niches for a decision.
Cost: filter/group_by requests only (1 credit each); capped at 230 credits.
Usage: python -m mashina.commercial_map
"""
import json
import os
import urllib.error

from mashina.oa import OpenAlex, BudgetExhausted

YEARS = [2019, 2022, 2025]
COMPANY = "authorships.institutions.type:company"
PAGING = {"ok": True}


def groups(oa, filt, by, max_pages=30):
    """All groups of a group_by, following the cursor; stops if the API repeats itself."""
    out, cursor, seen = {}, "*", 0
    for _ in range(max_pages):
        try:
            j = oa.get("/works", {"filter": filt, "group_by": by, "per-page": 200, "cursor": cursor})
        except urllib.error.HTTPError:  # paging of groups not accepted: take the first page only
            j = oa.get("/works", {"filter": filt, "group_by": by})
            PAGING["ok"] = False
        g = j.get("group_by", [])
        new = 0
        for x in g:
            if x["key"] not in out:
                out[x["key"]] = (x.get("key_display_name"), x["count"])
                new += 1
        cursor = (j.get("meta") or {}).get("next_cursor")
        if not g or not cursor or new == 0:
            break
    return out


def topic_meta(oa):
    meta, cursor = {}, "*"
    while cursor:
        j = oa.get("/topics", {"per-page": 200, "cursor": cursor, "select": "id,display_name,subfield,field,domain"})
        for t in j.get("results", []):
            meta[t["id"]] = {"name": t["display_name"], "subfield": (t.get("subfield") or {}).get("display_name"),
                             "field": (t.get("field") or {}).get("display_name"),
                             "domain": (t.get("domain") or {}).get("display_name")}
        cursor = (j.get("meta") or {}).get("next_cursor")
        if not j.get("results"):
            break
    return meta


def table(allc, comp, small):
    rows = []
    keys = set(allc[2025]) | set(comp[2025])
    for k in keys:
        name = (allc[2025].get(k) or comp[2025].get(k) or allc[2019].get(k) or (None, 0))[0]
        r = {"id": k, "name": name}
        for y in YEARS:
            a = (allc[y].get(k) or (None, 0))[1]
            c = (comp[y].get(k) or (None, 0))[1]
            r[f"all_{y}"], r[f"comp_{y}"] = a, c
            r[f"share_{y}"] = round(c / a, 5) if a else None
        s0, s1 = r["share_2019"], r["share_2025"]
        r["pp_change"] = round(100 * (s1 - s0), 3) if s0 is not None and s1 is not None else None
        r["ratio"] = round(s1 / s0, 3) if s0 and s1 is not None else None
        r["small"] = r["comp_2025"] < small
        rows.append(r)
    return rows


def who(oa, out):
    """Second step (13.11.2026): who are the companies behind the largest rises? Descriptive.
    For the 12 topics and 4 subfields with the largest rise of company share: countries and institutions
    on the 2025 works that have a company author (about 32 credits)."""
    tp = sorted([r for r in out["topics"] if r["pp_change"] is not None and not r["small"]], key=lambda r: -r["pp_change"])[:12]
    sf = sorted([r for r in out["subfields"] if r["pp_change"] is not None and not r["small"]], key=lambda r: -r["pp_change"])[:4]
    res = []
    for kind, rows, fld in [("topic", tp, "primary_topic.id"), ("subfield", sf, "primary_topic.subfield.id")]:
        for r in rows:
            f = f"publication_year:2025,{COMPANY},{fld}:{r['id'].rsplit('/', 1)[-1]}"
            c = oa.get("/works", {"filter": f, "group_by": "authorships.institutions.country_code"}).get("group_by", [])
            i = oa.get("/works", {"filter": f, "group_by": "authorships.institutions.id"}).get("group_by", [])
            res.append({"kind": kind, "name": r["name"], "comp_2025": r["comp_2025"],
                        "countries": [[x.get("key_display_name"), x["count"]] for x in c[:5]],
                        "institutions": [[x.get("key_display_name"), x["count"]] for x in i[:6]]})
    return res


def main():
    if os.path.exists("reports/commercial_map.json"):
        out = json.load(open("reports/commercial_map.json"))
        if out.get("topics") and not out.get("who"):
            oa = OpenAlex(floor=150, max_credits=60)
            out["who"] = who(oa, out)
            out["who_credits"] = oa.spent
            json.dump(out, open("reports/commercial_map.json", "w"), ensure_ascii=False, indent=0)
            L = ["", "## Кто эти компании (работы 2025 года с автором из компании)", "",
                 "| Тема или подобласть | Работ | Страны (число работ) | Организации (число работ) |", "|---|---|---|---|"]
            for w in out["who"]:
                L.append(f"| {w['name']} | {w['comp_2025']} | " + ", ".join(f"{a} {b}" for a, b in w["countries"]) + " | "
                         + "; ".join(f"{a} {b}" for a, b in w["institutions"]) + " |")
            open("reports/commercial_map.md", "a").write("\n".join(L) + "\n")
            print("who done, spent", oa.spent, "remaining", oa.remaining)
            return
    oa = OpenAlex(floor=150, max_credits=230)
    out = {"years": YEARS, "note": "descriptive only; sensor not validated on outcomes"}
    try:
        for level, by, small in [("subfields", "primary_topic.subfield.id", 200), ("topics", "primary_topic.id", 50)]:
            allc, comp = {}, {}
            for y in YEARS:
                allc[y] = groups(oa, f"publication_year:{y}", by)
                comp[y] = groups(oa, f"publication_year:{y},{COMPANY}", by)
            out[level] = table(allc, comp, small)
            out[level + "_groups"] = {str(y): [len(allc[y]), len(comp[y])] for y in YEARS}
        meta = topic_meta(oa)
        for r in out.get("topics", []):
            r.update({k: v for k, v in (meta.get(r["id"]) or {}).items() if k != "name"})
        out["topic_meta_count"] = len(meta)
    except BudgetExhausted as e:
        out["stopped"] = str(e)
    out["credits_spent"], out["credits_remaining"] = oa.spent, oa.remaining
    out["group_paging_ok"] = PAGING["ok"]
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/commercial_map.json", "w"), ensure_ascii=False, indent=0)

    def fmt(r, extra=""):
        return (f"| {r['name']}{extra} | {100 * (r['share_2019'] or 0):.1f}% | {100 * (r['share_2025'] or 0):.1f}% | "
                f"{r['pp_change']:+.1f} | {r['ratio'] if r['ratio'] is not None else '—'} | {r['comp_2025']} |")
    L = ["# Карта коммерческой науки по всем наукам (" + ", ".join(map(str, YEARS)) + ")", "",
         "Составлена по правилу из `mashina/commercial_map.py`, без моих оценок. Доля = работы с автором из компании / все работы.",
         "Это описание, а не рейтинг для решения: датчик не проверен на случаях с известным итогом.", "",
         f"Потрачено кредитов: {oa.spent}. Групп по годам (все, с компанией): {out.get('subfields_groups')} / {out.get('topics_groups')}", ""]
    head = "| Название | Доля 2019 | Доля 2025 | Изменение, п.п. | Отношение | Работ с компанией 2025 |\n|---|---|---|---|---|---|"
    sf = [r for r in out.get("subfields", []) if r["pp_change"] is not None and not r["small"]]
    L += ["## Подобласти: где доля компаний выросла сильнее всего (п.п.)", "", head]
    L += [fmt(r) for r in sorted(sf, key=lambda r: -r["pp_change"])[:25]]
    L += ["", "## Подобласти: где доля компаний упала сильнее всего", "", head]
    L += [fmt(r) for r in sorted(sf, key=lambda r: r["pp_change"])[:15]]
    tp = [r for r in out.get("topics", []) if r["pp_change"] is not None and not r["small"]]
    L += ["", "## Темы: наибольший рост доли компаний (п.п.), не меньше 50 работ с компанией в 2025", "", head]
    L += [fmt(r, f" ({r.get('field')})") for r in sorted(tp, key=lambda r: -r["pp_change"])[:50]]
    L += ["", "## Темы: наибольшее отношение долей 2025/2019 (при доле 2019 > 0)", "", head]
    L += [fmt(r, f" ({r.get('field')})") for r in sorted([r for r in tp if r["ratio"]], key=lambda r: -r["ratio"])[:40]]
    L += ["", "## Темы: наибольшая доля компаний в 2025", "", head]
    L += [fmt(r, f" ({r.get('field')})") for r in sorted(tp, key=lambda r: -(r["share_2025"] or 0))[:40]]
    open("reports/commercial_map.md", "w").write("\n".join(L) + "\n")
    print("spent", oa.spent, "remaining", oa.remaining, out.get("subfields_groups"), out.get("topics_groups"), out.get("stopped"))


if __name__ == "__main__":
    main()
