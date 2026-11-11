"""Reproduce the browser run of 2026-11-10 from saved data (no network)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mashina import model  # noqa: E402

D = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "rerun_2026-11-10.json")))
ids = [c["id"] for c in D["CONC"]]
single = {ids[int(k)]: v for k, v in D["D"]["ctag"].items()}
pair = {tuple(map(int, k.split("_"))): v for k, v in D["D"]["tag"].items()}


def test_tag_run_matches_browser():
    out = model.evaluate(ids, single, pair)
    assert abs(out[2004]["auc_cos"] - 0.851) < 0.002
    assert abs(out[2008]["auc_cos"] - 0.793) < 0.002
    assert abs(out[2012]["auc_cos"] - 0.749) < 0.002
    assert abs(out[2008]["auc_lr"] - 0.917) < 0.01
    assert abs(out[2012]["auc_lr"] - 0.802) < 0.01
