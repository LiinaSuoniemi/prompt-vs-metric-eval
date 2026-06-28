"""
Runs each test case through both prompt conditions (and a no-guidance control)
across the configured models, N trials each, and saves the raw model outputs.

Scoring is deliberately a separate step (score.py) so the judge can be re-run
without re-spending API calls. This file only collects raw outputs.

Usage:
    python harness.py                      # full run from the manifest
    python harness.py --trials 1 --models haiku --cases complexity_01   # smoke
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from judge import THRESHOLD, ruff_findings

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
RAW_PATH = RESULTS / "raw.jsonl"

MODELS = {"haiku": "claude-haiku-4-5", "sonnet": "claude-sonnet-4-6"}
TEMPERATURE = 1.0
MAX_TOKENS = 2048

SYSTEM = (
    "You are a senior Python engineer. Apply the fix to the snippet below and "
    "return ONLY the corrected Python code, with no explanation and no commentary."
)

# Condition B is the EXAMINER-hook behavioral prompt, verbatim from examiner_hook.py.
BEHAVIORAL = {
    "C901": (
        "Write in one sentence what this function does. Refactor until the code "
        "reads as close to that sentence as possible. If you cannot say it in one "
        "sentence, it has more than one responsibility."
    ),
    "BLE001": (
        "This catches every error. Name the specific exception you expect, and "
        "make sure the failure is logged or surfaced, never silently swallowed. "
        "A swallowed error is a bug you will debug blind later."
    ),
}


def bare_metric_message(code: str, smell: str) -> str:
    """Condition A guidance: the raw linter message ruff itself emits."""
    config = f"lint.mccabe.max-complexity={THRESHOLD}" if smell == "C901" else None
    findings = ruff_findings(code, smell, config)
    return findings[0]["message"] if findings else f"{smell} reported."


def guidance_for(condition: str, code: str, smell: str) -> str:
    if condition == "A_bare":
        return f"A linter reported: {bare_metric_message(code, smell)}\nFix it."
    if condition == "B_behavioral":
        return BEHAVIORAL[smell]
    if condition == "C_control":
        return "Improve this code."
    raise ValueError(condition)


CONDITIONS = ["A_bare", "B_behavioral", "C_control"]


def extract_code(text: str) -> str:
    """Pull the code out of a model reply, tolerating markdown fences."""
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


def load_cases(only: set[str] | None):
    manifest = json.loads((ROOT / "cases" / "manifest.json").read_text(encoding="utf-8"))
    cases = []
    for c in manifest["cases"]:
        if only and c["id"] not in only:
            continue
        c["code"] = (ROOT / "cases" / c["path"]).read_text(encoding="utf-8")
        cases.append(c)
    return cases


def already_done() -> set[tuple]:
    if not RAW_PATH.exists():
        return set()
    done = set()
    for line in RAW_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        done.add((r["case_id"], r["condition"], r["model"], r["trial"]))
    return done


def call_model(client, model_id: str, user_prompt: str):
    resp = client.messages.create(
        model=model_id,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        system=SYSTEM,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = next((b.text for b in resp.content if b.type == "text"), "")
    return text, resp.stop_reason, resp.usage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--models", default="haiku,sonnet")
    ap.add_argument("--cases", default="")
    args = ap.parse_args()

    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    RESULTS.mkdir(exist_ok=True)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    only = {c.strip() for c in args.cases.split(",") if c.strip()} or None
    cases = load_cases(only)
    done = already_done()

    planned = len(cases) * len(CONDITIONS) * len(models) * args.trials
    print(f"Planned trials: {planned} (already done: {len(done)})")

    with RAW_PATH.open("a", encoding="utf-8") as out:
        for case in cases:
            for condition in CONDITIONS:
                guidance = guidance_for(condition, case["code"], case["smell"])
                user_prompt = f"{guidance}\n\n```python\n{case['code']}\n```"
                for mkey in models:
                    model_id = MODELS[mkey]
                    for trial in range(args.trials):
                        key = (case["id"], condition, mkey, trial)
                        if key in done:
                            continue
                        text, stop, usage = call_model(client, model_id, user_prompt)
                        record = {
                            "case_id": case["id"],
                            "smell": case["smell"],
                            "condition": condition,
                            "model": mkey,
                            "model_id": model_id,
                            "trial": trial,
                            "guidance": guidance,
                            "before": case["code"],
                            "raw_response": text,
                            "after": extract_code(text),
                            "stop_reason": stop,
                            "input_tokens": usage.input_tokens,
                            "output_tokens": usage.output_tokens,
                        }
                        out.write(json.dumps(record) + "\n")
                        out.flush()
                        print(f"  {case['id']:16} {condition:14} {mkey:7} t{trial} "
                              f"[{stop}] {usage.input_tokens}->{usage.output_tokens}")
                        time.sleep(0.3)  # gentle pacing
    print("Done. Raw outputs in results/raw.jsonl")


if __name__ == "__main__":
    main()
