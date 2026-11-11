"""End-to-end run on the 50 saved areas with a fake OpenAlex (no network)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from mashina import collect, model  # noqa: E402
from mashina.oa import BudgetExhausted  # noqa: E402

D = json.load(open(os.path.join(ROOT, "data", "rerun_2026-11-10.json")))
IDS = [c["id"] for c in D["CONC"]]
POS = {a: i for i, a in enumerate(IDS)}


class FakeOA:
    def __init__(self, cap):
        self.spent, self.remaining, self.cap = 0, 10000, cap

    def _pay(self):
        if self.spent >= self.cap:
            raise BudgetExhausted("cap")
        self.spent += 1

    def year_counts(self, filt):
        self._pay()
        ids = [x.split(":")[1] for x in filt.split(",")]
        if len(ids) == 1:
            return D["D"]["ctag"][str(POS[ids[0]])]
        i, j = sorted((POS[ids[0]], POS[ids[1]]))
        return D["D"]["tag"].get(f"{i}_{j}", {})

    def count(self, filt):
        self._pay()
        a, bs = [x.split(":")[1] for x in filt.split(",")[:2]]
        tot = 0
        for b in bs.split("|"):
            i, j = sorted((POS[a], POS[b]))
            tot += sum(D["D"]["tag"].get(f"{i}_{j}", {}).values())
        return tot


def test_resumable_collect(tmp_path):
    path = str(tmp_path / "counts.json")
    done, total = collect.run(FakeOA(cap=300), IDS, path=path, log=lambda *_: None)
    assert done < total                      # first night stops on budget
    done, total = collect.run(FakeOA(cap=10**6), IDS, path=path, log=lambda *_: None)
    assert done == total == 1225             # second night finishes
    st = collect.load(path)
    single = st["single"]
    pair = {}
    for k, v in st["pair"].items():
        a, b = k.split("|")
        pair[tuple(sorted((POS[a], POS[b])))] = v
    out = model.evaluate(IDS, single, pair)
    assert abs(out[2008]["auc_cos"] - 0.793) < 0.002
