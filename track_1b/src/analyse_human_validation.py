#!/usr/bin/env python3
"""Analyse judge vs. blinded human validation for the Apertus benchmark."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path("track_1b")
JUDGE = BASE / "job_output_judge" / "judge_results.jsonl"
HUMAN = BASE / "data" / "human_validation_results.jsonl"
SAMPLE = BASE / "data" / "human_validation_sample.jsonl"

LABELS = ["correct", "incorrect", "not_attempted"]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
            rows.append(obj)
    return rows


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) / n) + (z * z / (4 * n * n))) / denom
    return centre - margin, centre + margin


def cohen_kappa(human: list[str], judge: list[str]) -> float:
    n = len(human)
    if n == 0:
        return float("nan")
    observed = sum(h == j for h, j in zip(human, judge)) / n

    h_counts = Counter(human)
    j_counts = Counter(judge)
    expected = sum(
        (h_counts[label] / n) * (j_counts[label] / n)
        for label in LABELS
    )
    if math.isclose(1 - expected, 0.0):
        return float("nan")
    return (observed - expected) / (1 - expected)


def pct(x: float) -> str:
    return f"{100*x:.1f}%"


def main() -> None:
    for path in (JUDGE, HUMAN, SAMPLE):
        if not path.exists():
            raise SystemExit(f"Missing required file: {path}")

    judge_rows = read_jsonl(JUDGE)
    human_rows = read_jsonl(HUMAN)
    sample_rows = read_jsonl(SAMPLE)

    judge_by_id = {r["case_id"]: r for r in judge_rows}
    human_by_id = {r["case_id"]: r for r in human_rows}
    sample_ids = [r["case_id"] for r in sample_rows]

    if len(judge_by_id) != 300:
        raise SystemExit(f"Expected 300 unique judge results, got {len(judge_by_id)}")
    if len(sample_ids) != 60 or len(set(sample_ids)) != 60:
        raise SystemExit("Expected 60 unique human-validation sample IDs")
    if len(human_by_id) != 60:
        raise SystemExit(f"Expected 60 unique human results, got {len(human_by_id)}")
    if set(sample_ids) != set(human_by_id):
        raise SystemExit("Human results do not exactly match the sampled case IDs")
    if not set(sample_ids).issubset(judge_by_id):
        raise SystemExit("Some sampled cases are missing from judge results")

    human_labels = [human_by_id[cid]["human_label"] for cid in sample_ids]
    judge_labels = [judge_by_id[cid]["judge_label"] for cid in sample_ids]

    invalid_h = sorted(set(human_labels) - set(LABELS))
    invalid_j = sorted(set(judge_labels) - set(LABELS))
    if invalid_h or invalid_j:
        raise SystemExit(f"Invalid labels: human={invalid_h}, judge={invalid_j}")

    agreements = sum(h == j for h, j in zip(human_labels, judge_labels))
    n = len(sample_ids)
    agreement = agreements / n
    low, high = wilson_interval(agreements, n)
    kappa = cohen_kappa(human_labels, judge_labels)

    confusion = defaultdict(lambda: Counter())
    disagreements = []
    for cid, h, j in zip(sample_ids, human_labels, judge_labels):
        confusion[h][j] += 1
        if h != j:
            disagreements.append((cid, h, j))

    judge_all_counts = Counter(r["judge_label"] for r in judge_rows)
    judge_correct = judge_all_counts["correct"]
    j_low, j_high = wilson_interval(judge_correct, len(judge_rows))

    human_counts = Counter(human_labels)
    human_correct = human_counts["correct"]
    h_low, h_high = wilson_interval(human_correct, n)

    judge_sample_counts = Counter(judge_labels)
    judge_sample_correct = judge_sample_counts["correct"]
    js_low, js_high = wilson_interval(judge_sample_correct, n)

    print("Judge–human validation")
    print("======================")
    print(f"Human validation cases:       {n}")
    print(f"Exact agreements:             {agreements}/{n}")
    print(f"Percent agreement:            {pct(agreement)}")
    print(f"95% Wilson CI (agreement):    {pct(low)}–{pct(high)}")
    print(f"Cohen's kappa:                {kappa:.3f}")
    print()

    print("Overall judge-labelled benchmark")
    print(f"  correct:                    {judge_all_counts['correct']:3d}/300 ({pct(judge_all_counts['correct']/300)})")
    print(f"  incorrect:                  {judge_all_counts['incorrect']:3d}/300 ({pct(judge_all_counts['incorrect']/300)})")
    print(f"  not_attempted:              {judge_all_counts['not_attempted']:3d}/300 ({pct(judge_all_counts['not_attempted']/300)})")
    print(f"  95% Wilson CI for correct:  {pct(j_low)}–{pct(j_high)}")
    print()

    print("Human-validation sample label rates")
    for label in LABELS:
        print(f"  human {label:14s} {human_counts[label]:3d}/60 ({pct(human_counts[label]/60)})")
    print(f"  human correct 95% CI:       {pct(h_low)}–{pct(h_high)}")
    print()
    for label in LABELS:
        print(f"  judge {label:14s} {judge_sample_counts[label]:3d}/60 ({pct(judge_sample_counts[label]/60)})")
    print(f"  judge correct 95% CI:       {pct(js_low)}–{pct(js_high)}")
    print()

    print("Confusion matrix (rows = human, columns = judge)")
    print(f"{'':16s}{'correct':>12s}{'incorrect':>12s}{'not_attempted':>16s}")
    for h in LABELS:
        print(
            f"{h:16s}"
            f"{confusion[h]['correct']:12d}"
            f"{confusion[h]['incorrect']:12d}"
            f"{confusion[h]['not_attempted']:16d}"
        )
    print()

    print(f"Disagreements: {len(disagreements)}")
    for cid, human_label, judge_label in disagreements:
        print(f"  {cid}: human={human_label}, judge={judge_label}")


if __name__ == "__main__":
    main()
