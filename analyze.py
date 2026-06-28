"""
Aggregates the scored trials into the headline result: genuine-fix rate per
condition and model, with a 95% bootstrap confidence interval, and the primary
behavioral-minus-bare comparison.

Usage: python analyze.py
"""
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCORED = ROOT / "results" / "scored.jsonl"
SUMMARY = ROOT / "results" / "summary.md"


def bootstrap_ci(indicators, n=2000, seed=0):
    """Percentile bootstrap 95% CI for the mean of a 0/1 list."""
    if not indicators:
        return 0.0, 0.0
    rng = random.Random(seed)
    k = len(indicators)
    props = sorted(sum(indicators[rng.randrange(k)] for _ in range(k)) / k for _ in range(n))
    return props[int(0.025 * n)], props[int(0.975 * n)]


def rate_line(model, cond, verdicts):
    n = len(verdicts)
    genuine = sum(v == "genuine" for v in verdicts)
    gamed = sum(v == "gamed" for v in verdicts)
    nofix = sum(v == "no_fix" for v in verdicts)
    ind = [1 if v == "genuine" else 0 for v in verdicts]
    lo, hi = bootstrap_ci(ind)
    rate = genuine / n if n else 0.0
    return (f"{model:8} {cond:14} {n:3} {genuine:8} {gamed:6} {nofix:7} "
            f"{rate:8.1%}  [{lo:5.1%}, {hi:5.1%}]")


def main():
    records = [json.loads(l) for l in SCORED.read_text(encoding="utf-8").splitlines() if l.strip()]
    groups = defaultdict(list)
    for r in records:
        groups[(r["model"], r["condition"])].append(r["verdict"])

    header = (f"{'model':8} {'condition':14} {'n':>3} {'genuine':>8} {'gamed':>6} "
              f"{'no_fix':>7} {'%genuine':>9}  {'95% CI':>16}")
    lines = [header, "-" * len(header)]
    for key in sorted(groups):
        lines.append(rate_line(key[0], key[1], groups[key]))

    lines.append("")
    lines.append("Primary comparison (genuine-fix rate, behavioral B minus bare A):")
    for model in sorted({m for m, _ in groups}):
        a = [1 if v == "genuine" else 0 for v in groups.get((model, "A_bare"), [])]
        b = [1 if v == "genuine" else 0 for v in groups.get((model, "B_behavioral"), [])]
        if a and b:
            lines.append(f"  {model}: {sum(b) / len(b) - sum(a) / len(a):+.1%}")

    for line in lines:
        print(line)
    SUMMARY.write_text("# Results\n\n```\n" + "\n".join(lines) + "\n```\n", encoding="utf-8")
    print(f"\nWrote {SUMMARY.name}")


if __name__ == "__main__":
    main()
