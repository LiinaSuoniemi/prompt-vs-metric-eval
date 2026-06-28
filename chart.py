"""
Draws the headline chart: genuine-fix rate per guidance condition, grouped by
model, with 95% bootstrap CI error bars. Saves results/chart.png.

Usage: python chart.py
"""
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from analyze import bootstrap_ci  # noqa: E402

ROOT = Path(__file__).resolve().parent
SCORED = ROOT / "results" / "scored.jsonl"
CHART = ROOT / "results" / "chart.png"

COND_ORDER = ["A_bare", "B_behavioral", "C_control"]
COND_LABELS = {"A_bare": "bare metric", "B_behavioral": "behavioral prompt", "C_control": "control"}


def main():
    records = [json.loads(l) for l in SCORED.read_text(encoding="utf-8").splitlines() if l.strip()]
    groups = defaultdict(list)
    for r in records:
        groups[(r["model"], r["condition"])].append(r["verdict"])
    models = sorted({m for m, _ in groups})

    fig, ax = plt.subplots(figsize=(8, 5))
    width = 0.8 / max(len(models), 1)
    xs = range(len(COND_ORDER))

    for i, model in enumerate(models):
        rates, lo_err, hi_err = [], [], []
        for cond in COND_ORDER:
            ind = [1 if v == "genuine" else 0 for v in groups.get((model, cond), [])]
            rate = sum(ind) / len(ind) if ind else 0.0
            lo, hi = bootstrap_ci(ind)
            rates.append(rate * 100)
            lo_err.append((rate - lo) * 100)
            hi_err.append((hi - rate) * 100)
        positions = [x + i * width for x in xs]
        ax.bar(positions, rates, width, yerr=[lo_err, hi_err], capsize=4, label=model)

    ax.set_xticks([x + width * (len(models) - 1) / 2 for x in xs])
    ax.set_xticklabels([COND_LABELS[c] for c in COND_ORDER])
    ax.set_ylabel("genuine fixes (%)")
    ax.set_ylim(0, 100)
    ax.set_title("Genuine-fix rate by guidance and model (95% CI)")
    ax.legend(title="model")
    fig.tight_layout()
    fig.savefig(CHART, dpi=150)
    print(f"Wrote {CHART}")


if __name__ == "__main__":
    main()
