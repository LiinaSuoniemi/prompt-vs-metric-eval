"""
Runs the deterministic judge over the raw model outputs and writes a scored
file. Separate from the harness so the judge can be re-run (or fixed) without
re-spending API calls.

Usage: python score.py
"""
import json
from pathlib import Path

from judge import classify_fix

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "results" / "raw.jsonl"
SCORED = ROOT / "results" / "scored.jsonl"


def main():
    lines = [json.loads(l) for l in RAW.read_text(encoding="utf-8").splitlines() if l.strip()]
    with SCORED.open("w", encoding="utf-8") as out:
        for r in lines:
            verdict, details = classify_fix(r["smell"], r["before"], r["after"])
            r["verdict"] = verdict
            r["judge_details"] = details
            out.write(json.dumps(r) + "\n")
    print(f"Scored {len(lines)} records -> results/scored.jsonl")


if __name__ == "__main__":
    main()
