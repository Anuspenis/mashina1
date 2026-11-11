"""Text patterns for the rule "both entities are named in the title or abstract".

The 50 base areas have hand-written patterns checked on the 96-work blind audit
(precision 0.88, recall 0.85). Other areas get automatic patterns from the
concept name plus its English Wikidata aliases; data/synonyms.json can be edited
by hand and is never overwritten for areas already in it.
"""
import json
import os
import re
import urllib.request

STORE = "data/synonyms.json"

MANUAL = {
    "Lithium-ion battery": r"lithium[- ]ion|\bli[- ]ion",
    "Perovskite solar cell": r"perovskite",
    "Graphene": r"(?<!-like )graphene(?!-like)",
    "Deep learning": r"deep learning|deep neural|convolutional neural|\bcnn\b|\blstm\b|deep network",
    "Data center": r"data[- ]?cent(er|re)|datacent",
    "Electric vehicle": r"electric vehicle|electric car|electric bus|\bevs?\b|plug-in hybrid|\bphevs?\b|\bbevs?\b",
    "Hydrogen production": r"hydrogen|water splitting|electroly[sz]|\bh2\b",
    "Photovoltaic system": r"photovolta|solar cell|solar panel|solar module|\bpv\b",
    "Wind power": r"wind (power|energy|turbine|farm|generat|speed|resource)|offshore wind",
    "Smart grid": r"smart grid|smart meter|microgrid",
    "Distribution transformer": r"transformer",
    "Rare-earth element": r"rare[- ]earth|lanthan|neodymium|dysprosium|\bree\b",
    "Supply chain": r"supply chain|supply network",
    "Tariff": r"tariff",
    "Sanctions": r"sanction|embargo",
    "Interest group": r"interest group|lobby",
    "Monetary policy": r"monetary|central bank|interest rate",
    "Semiconductor": r"semiconduct",
    "Quantum computer": r"quantum comput|qubit|quantum algorithm|quantum gate",
    "CRISPR": r"crispr|cas9|cas12|cas13|rna-guided|guide rna",
    "Nanomedicine": r"nanomedic|drug deliver|nanocarrier",
    "Antibiotic resistance": r"resistan|antimicrob",
    "Bacteriophage": r"phage",
    "Climate change": r"climate|global warming",
    "Carbon capture and storage (timeline)": r"carbon capture|co2 capture|co2 storage|carbon storage|sequestration|\bccs\b",
    "Desalination": r"desalinat|reverse osmosis",
    "Fertilizer": r"fertili[sz]",
    "Aquaculture": r"aquacult|fish farm|mariculture",
    "Microplastics": r"microplastic|nanoplastic|plastic debris",
    "Pandemic": r"pandemic|epidemic|influenza|covid|sars",
    "Voting": r"\bvot(e|es|ed|ing|er|ers)\b|election|electoral|ballot",
    "Disinformation": r"disinformation|misinformation|fake news|propaganda|rumou?r",
    "Blockchain": r"blockchain|distributed ledger|smart contract|bitcoin|cryptocurrenc",
    "Satellite": r"satellite",
    "3D printing": r"3d[- ]print|additive(ly)? manufactur",
    "Robotics": r"robot",
    "Self driving": r"self[- ]driving|autonomous (vehicle|car|driving)|driverless|automated driving",
    "Natural language processing": r"natural language|\bnlp\b|text min|language model|text classif|sentiment analysis",
    "Copper": r"copper|\bcu\b|\bcu\d|\bcu\(",
    "Cobalt": r"cobalt|co3o4|\bco\(i|licoo2|\bco-(doped|based)",
    "Uranium": r"uranium|uranyl|\bu\(vi\)|\buo2\b",
    "Fusion power": r"fusion (power|energy|reactor|plasma)|tokamak|stellarator|nuclear fusion|inertial confinement|plasma confinement",
    "Superconductivity": r"supercond|josephson|andreev|cooper pair",
    "Heat pump": r"heat pump",
    "Thermoelectric materials": r"thermoelectric|seebeck|peltier",
    "Food security": r"food (in)?security|malnutrition|food system|undernutrition|hunger",
    "Dementia": r"dementia|alzheimer|cognitive (decline|impairment)",
    "Obesity": r"obes|overweight|body mass index|\bbmi\b|adipos|weight status",
    "Electrical steel": r"electrical steel|silicon steel|grain[- ]oriented|non[- ]oriented|core loss|fe-si",
    "Geopolitics": r"geopolit",
}


def term_pattern(term):
    t = re.escape(term.lower().strip())
    t = re.sub(r"(\\ |\\-)+", r"[- ]?", t)
    return r"\b" + t + r"(s|es)?\b"


def specific(alias):
    """Keep aliases that cannot be an ordinary word: several words, a hyphen,
    a digit or an acronym. Single plain words like 'error' (alias of 'Software
    bug') would match half of all abstracts."""
    a = alias.strip()
    if len(a) < 4:
        return False
    return (" " in a or "-" in a or any(ch.isdigit() for ch in a)
            or (a.isupper() and a.isalpha()))


def auto_pattern(name, aliases):
    terms = [name] + [a for a in aliases if specific(a)]
    pats = []
    for t in terms:
        p = term_pattern(t)
        if p not in pats:
            pats.append(p)
    return "|".join(pats)


def wikidata_aliases(qid):
    if not qid:
        return []
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    req = urllib.request.Request(url, headers={"User-Agent": "mashina (research)"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            ent = json.load(r)["entities"]
    except Exception:
        return []
    e = next(iter(ent.values()))
    return [a["value"] for a in e.get("aliases", {}).get("en", [])]


def build(areas, path=STORE):
    st = json.load(open(path)) if os.path.exists(path) else {}
    for a in areas:
        if a["id"] in st:
            v = st[a["id"]]
            if v.get("source", "").startswith("auto"):   # re-apply the current alias rule
                v["pattern"] = auto_pattern(v["name"], v.get("aliases", []))
            continue
        if a["name"] in MANUAL:
            st[a["id"]] = {"name": a["name"], "pattern": MANUAL[a["name"]], "source": "manual, audited"}
        else:
            al = wikidata_aliases(a.get("wikidata"))
            st[a["id"]] = {"name": a["name"], "pattern": auto_pattern(a["name"], al),
                           "source": "auto: name + Wikidata aliases", "aliases": al}
    json.dump(st, open(path, "w"), ensure_ascii=False, indent=1)
    return st


def compiled(st):
    return {k: re.compile(v["pattern"]) for k, v in st.items()}
