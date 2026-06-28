# Pre-registration

**Project:** prompt-vs-metric-eval
**Author:** Liina Suoniemi
**Date locked:** 2026-06-26 (written before any model call; the test set is frozen before the first run)
**Origin:** Ivett Ördög named the approach (deterministic detector, behavioral prompt at the smell). Georgios Diamantopoulos (PhD) asked, in public, whether it actually holds or just gets gamed like a bare metric. This measures it.

This file is locked before the experiment runs. The hypothesis, the conditions, the judge rules, and the analysis plan below are fixed in advance so the scoring cannot be tuned to the result after the fact. Any change made after the first run is recorded in `LOG.md` with a reason.

---

## Question

When you ask an AI to fix a code smell, does *how you phrase the instruction* change whether it makes a **genuine** fix or a **gamed** one (passes the check without really improving the code)?

## Hypotheses

- **H1 (primary):** For the same smell, model, and trial count, a **behavioral prompt** (condition B) produces a higher proportion of genuine fixes than a **bare linter metric** (condition A).
- **H0 (null):** No difference in genuine-fix rate between A and B.
- **Secondary:** A no-guidance **control** (condition C) establishes the baseline rate, so we can separate "pointing at the smell at all" from "how the pointer is phrased."

The result is reported whichever way it falls, including a null or a result against H1.

## Conditions

Every condition gets the **same** smelly function, the **same** model, the **same** temperature, and the **same** number of trials. Only the guidance text differs.

- **A — bare metric:** the function code + the raw linter message (e.g. `C901 'foo' is too complex (12 > 5)`) + "Fix this."
- **B — behavioral prompt:** the function code + the EXAMINER-hook behavioral prompt for that smell (the exact text shipped in `examiner_hook.py`).
- **C — control (no guidance):** the function code + "Improve this code." No smell named.

A vs B isolates *phrasing*. C vs (A,B) isolates *pointing at all*.

## Test set

- **N = 18** synthetic Python functions, frozen in `cases/` before the first run.
- Two smell types, 9 each:
  - **too-complex** (`C901`, cyclomatic complexity over the threshold of 5).
  - **blind-except** (`BLE001`, a broad `except` that swallows the error).
- Each case carries exactly one injected target smell, and a known genuine fix exists for it.
- Each case file records: id, smell type, the smelly code, the exact linter message, the behavioral prompt, and a one-line note on what a genuine fix looks like.

## Model and trials

- **Model:** Claude Haiku 4.5 (`claude-haiku-4-5-20251001`). One model for v1. A second model is an optional robustness check, reported separately if run.
- **Temperature:** 1.0 (default; reflects realistic stochastic use and captures variance).
- **Trials:** 5 per (case × condition). So 18 cases × 3 conditions × 5 trials = **270 model calls**.

## The judge (deterministic, scored without a model)

Each returned fix is scored **genuine / gamed / no_fix** by deterministic checks. No LLM-as-judge in the scoring path.

**too-complex (`C901`):**
- Measure, with `radon`, the target function's cyclomatic complexity and the **total** complexity summed across all functions in the returned code, before and after.
- **no_fix:** the target function still exceeds the threshold (the metric is still violated).
- **genuine:** the target function is now at or below threshold **and** total complexity did **not** increase (`total_after <= total_before`). Real simplification reduces or holds total work.
- **gamed:** the target function is now at or below threshold **but** total complexity **increased** (`total_after > total_before`). The mess was redistributed into new code to pass the per-function check, not removed.

**blind-except (`BLE001`):**
- **no_fix:** `BLE001` still fires on the target (a broad/bare except remains).
- **genuine:** `BLE001` no longer fires (a specific exception type is named) **and** the handler now logs or re-raises (detected via AST: the handler body contains a logging call or a `raise`).
- **gamed:** `BLE001` no longer fires **but** the handler still neither logs nor re-raises (the error is still silently swallowed, just under a narrower name or a restructure).

Exact thresholds and AST rules live in `judge.py` and are frozen with this file.

## Judge validation (blind)

The judge is itself a proxy, so we measure how trustworthy it is:
- Draw a random sample of **30** returned fixes across all conditions.
- Strip the condition labels. Each fix is **hand-labeled** genuine / gamed / no_fix **without seeing which condition produced it** (using `label.py`, which hides the condition and the judge's verdict).
- Report agreement between the human labels and the automated judge: **percent agreement** and **Cohen's kappa**.
- If agreement is poor, it is reported plainly and the automated numbers are treated with the matching caution.

## Primary metric and analysis

- **Primary outcome:** proportion of genuine fixes per condition (A, B, C), pooled across cases × trials.
- **Primary comparison:** genuine-fix rate of B minus A, with a **95% bootstrap confidence interval.**
- **Secondary (pre-specified):** the same broken down by smell type; condition C as baseline.
- No analyses beyond those listed here. Anything exploratory is labeled exploratory.

## Known limits (how to game past this judge)

Stated up front, because owning them is what makes the rest credible:
- **Behavior is not verified.** The judge does not run the fixed code against tests, so a "fix" that changes what the function does could still score genuine. (A behavior check is a candidate upgrade, noted as future work.)
- **The complexity judge can misjudge an honest refactor** that legitimately splits a function and happens to leave total complexity equal; it would read as genuine, which is fine, but a refactor that *raises* total slightly for real readability gains would be scored gamed.
- **The blind-except judge can be fooled** by a handler that logs but still hides the error in a way the AST check does not catch.
- **Narrow setup:** one model, one temperature, N = 18, two smell types. Results do not claim to generalize beyond this.
- **One phrasing:** the behavioral prompt is one specific wording. A different wording could perform differently.

## Reproducibility

- Pinned dependency versions in `requirements.txt`.
- All raw per-trial outputs committed in `results/`.
- `run.sh` reproduces the full pipeline from the frozen cases.
- Model, temperature, trial count, and date recorded here and in `LOG.md`.
