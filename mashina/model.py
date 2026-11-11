"""Link prediction between areas: which unconnected pairs connect within 6 years.

Definitions (unchanged since the first run): at cutoff t a pair is a candidate if
it has at most 5 co-tagged works up to t; it "connects" if it has 10+ in t+1..t+6.
Features known at t: cos (similarity of neighbourhoods), cn (common neighbours),
gr (growth), pa (size), tr (prior co-works), lms (log size of the smaller area).
"""
import math

import numpy as np

CUTS = [1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010, 2012]
FE = ["cos", "cn", "gr", "pa", "tr", "lms"]


def ysum(o, a, b):
    if not o:
        return 0
    return sum(v for y, v in o.items() if a <= int(y) <= b)


def build(ids, single, pair, c, w=6, thr_tr=5, thr_te=10, exclude=()):
    """ids: ordered area ids; pair: {(i, j): {year: n}} with i < j (indices)."""
    n = len(ids)
    size = [ysum(single.get(a), 1950, c) for a in ids]
    g = [(ysum(single.get(a), c - 4, c) + 1) / (ysum(single.get(a), c - 9, c - 5) + 1) for a in ids]
    tr = np.zeros((n, n))
    te = np.zeros((n, n))
    for (i, j), o in pair.items():
        tr[i, j] = tr[j, i] = ysum(o, 1950, c)
        te[i, j] = te[j, i] = ysum(o, c + 1, c + w)
    L = np.log1p(tr)
    adj = tr > thr_tr
    rows = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in exclude or tr[i, j] > thr_tr:
                continue
            mask = np.ones(n, bool)
            mask[[i, j]] = False
            a, b = L[i, mask], L[j, mask]
            den = math.sqrt(float(a @ a) * float(b @ b))
            cos = float(a @ b) / den if den else 0.0
            cn = int(np.sum(adj[i] & adj[j]))
            rows.append({"i": i, "j": j, "tr": tr[i, j], "te": te[i, j], "y": int(te[i, j] >= thr_te),
                         "cos": cos, "cn": cn, "gr": math.log(g[i]) + math.log(g[j]),
                         "pa": math.log1p(size[i]) + math.log1p(size[j]),
                         "lms": math.log1p(min(size[i], size[j]))})
    return rows


def rank(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2
        i = j + 1
    return r / max(len(x) - 1, 1)


def auc(score, y):
    y = np.asarray(y, int)
    r = rank(score) * (len(y) - 1) + 1
    P = y.sum()
    Nn = len(y) - P
    return float((r[y == 1].sum() - P * (P + 1) / 2) / (P * Nn))


def p_at(score, y, k=20):
    idx = np.argsort(-np.asarray(score, float), kind="mergesort")[:k]
    return float(np.asarray(y)[idx].mean())


def features(rows):
    return np.column_stack([rank([r[f] for r in rows]) for f in FE])


def fit_lr(X, y, iters=1500, lr=0.5, l2=0.01):
    """Class-balanced logistic regression by gradient descent (same as the browser runs)."""
    y = np.asarray(y, float)
    wpos = (len(y) - y.sum()) / max(y.sum(), 1)
    wt = np.where(y == 1, wpos, 1.0)
    w = np.zeros(X.shape[1])
    b = 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(X @ w + b)))
        e = (p - y) * wt
        w -= lr * (X.T @ e / len(y) + l2 * w)
        b -= lr * e.mean()
    return w, b


def evaluate(ids, single, pair, labels=None, exclude=()):
    """labels: optional {(cut, i, j): 0/1} overriding tag-based y for positives."""
    data = {}
    for c in CUTS:
        rows = build(ids, single, pair, c, exclude=exclude)
        y = [r["y"] for r in rows]
        if labels is not None:
            y = [labels.get((c, r["i"], r["j"]), yy) if yy else 0 for r, yy in zip(rows, y)]
        data[c] = (rows, features(rows), np.array(y))
    out = {}
    for c in (2004, 2008, 2012):
        rows, X, y = data[c]
        out[c] = {"n": len(rows), "pos": int(y.sum()),
                  "auc_cos": round(auc([r["cos"] for r in rows], y), 3),
                  "auc_gr": round(auc([r["gr"] for r in rows], y), 3),
                  "p20_cos": p_at([r["cos"] for r in rows], y)}
    for c in (2008, 2010, 2012):
        train = [t for t in CUTS if t <= c - 6]
        X = np.vstack([data[t][1] for t in train])
        y = np.concatenate([data[t][2] for t in train])
        w, b = fit_lr(X, y)
        rows, Xt, yt = data[c]
        s = Xt @ w + b
        out.setdefault(c, {})
        out[c]["auc_lr"] = round(auc(s, yt), 3)
        out[c]["p20_lr"] = p_at(s, yt)
    return out
