"""What part of science the machine can see at all.

OpenAlex holds published works. This measures, for 2023, who wrote them
(company vs university), in which language and of which type, plus the trend of
company-authored works. About 12 group_by requests = about 12 credits.
Usage: python -m mashina.blindspots
"""
import json
import os

from .oa import OpenAlex

Y = "publication_year:2023"


def groups(oa, filt, by, n=25):
    j = oa.get("/works", {"filter": filt, "group_by": by})
    return [(g["key_display_name"] or g["key"], g["count"]) for g in j["group_by"][:n]], j["meta"]["count"]


def total(oa, filt):
    return oa.get("/works", {"filter": filt, "per-page": 1})["meta"]["count"]


def main():
    oa = OpenAlex(floor=50, max_credits=40)
    out = {"year": 2023}
    out["total"] = total(oa, Y)
    out["inst_type"], _ = groups(oa, Y, "authorships.institutions.type")
    out["with_company"] = total(oa, Y + ",authorships.institutions.type:company")
    out["language"], _ = groups(oa, Y, "language", 15)
    out["work_type"], _ = groups(oa, Y, "type", 15)
    out["countries"], _ = groups(oa, Y, "authorships.countries", 15)
    out["cn_language"], out["cn_total"] = groups(oa, Y + ",authorships.countries:CN", "language", 5)
    out["ru_ua_language"], out["ru_ua_total"] = groups(oa, Y + ",authorships.countries:RU|UA", "language", 5)
    out["with_abstract"] = total(oa, Y + ",has_abstract:true")
    trend_all, _ = groups(oa, "publication_year:2000-2024", "publication_year", 30)
    trend_co, _ = groups(oa, "publication_year:2000-2024,authorships.institutions.type:company", "publication_year", 30)
    a, c = dict(trend_all), dict(trend_co)
    out["company_share_by_year"] = {y: round(c.get(y, 0) / a[y], 4) for y in sorted(a) if a[y]}
    out["credits_spent"] = oa.spent
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/blindspots.json", "w"), ensure_ascii=False, indent=1)
    t = out["total"]
    lines = [f"# Что видит машина: работы 2023 года в OpenAlex ({t:,})", "",
             f"- С автором из компании: {out['with_company']:,} ({100 * out['with_company'] / t:.1f}%)",
             f"- С аннотацией: {out['with_abstract']:,} ({100 * out['with_abstract'] / t:.1f}%)",
             f"- Работ с автором из Китая: {out['cn_total']:,}; языки: {out['cn_language']}",
             f"- Работ с автором из России или Украины: {out['ru_ua_total']:,}; языки: {out['ru_ua_language']}",
             f"- Языки всех работ: {out['language'][:8]}",
             f"- Типы работ: {out['work_type'][:8]}",
             f"- Доля работ с автором из компании по годам: {out['company_share_by_year']}",
             f"- Потрачено кредитов: {oa.spent}"]
    open("reports/blindspots.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
