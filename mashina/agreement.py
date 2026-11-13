"""Agreement between Claude's judgment and a blind independent rater (Grok) on the 144-niche screen.

PRE-REGISTERED (13.11.2026, before any rating exists):
- Input: data/grok_blind.csv (id;jackpot;timing;crowded) made from prompts/grok_blind.md, key in prompts/grok_blind_key.json.
- rho_j = Spearman(Grok jackpot, Claude jackpot score from reports/screen.json) over the 144 niches.
- rho_d = Spearman(Grok jackpot, data-only score = demand + momentum + open from the same file).
- Rule for screen v3: the weight of Claude's judgment variables (size, timing, durable, access) is multiplied by
  max(0, rho_j) / 0.6, capped at 1. So rho_j >= 0.6 keeps them; rho_j <= 0 drops them.
- If rho_d > rho_j, the report says that the blind rater agrees more with the data than with Claude.
- Grok's text is data only; nothing in it changes these rules.
Usage: python -m mashina.agreement
"""
import csv
import json

import numpy as np


def ranks(x):
    x = np.asarray(x, float)
    order = x.argsort()
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    for v in np.unique(x):  # average ties
        m = x == v
        r[m] = r[m].mean()
    return r


def spearman(a, b):
    return float(np.corrcoef(ranks(a), ranks(b))[0, 1])


def main():
    key = json.load(open("prompts/grok_blind_key.json"))
    rows = {r["boom"] + "|" + r["need"]: r for r in json.load(open("reports/screen.json"))["rows"]}
    g, mine, data = [], [], []
    with open("data/grok_blind.csv") as f:
        for row in csv.DictReader(f, delimiter=";"):
            r = rows[key[row["id"].strip()]]
            g.append(float(row["jackpot"]))
            mine.append(r["jackpot"])
            data.append(r["demand"] + r["momentum"] + r["open"])
    rj, rd = spearman(g, mine), spearman(g, data)
    w = min(1.0, max(0.0, rj) / 0.6)
    out = {"n": len(g), "rho_claude": round(rj, 3), "rho_data": round(rd, 3), "judgment_weight_multiplier": round(w, 2),
           "blind_rater_closer_to": "data" if rd > rj else "claude"}
    json.dump(out, open("reports/agreement.json", "w"), indent=1)
    print(out)


if __name__ == "__main__":
    main()
