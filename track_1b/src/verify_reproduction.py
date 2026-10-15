#!/usr/bin/env python3
"""Verify that reproduced benchmark metrics match the frozen submission results."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

BASE = Path("track_1b")
RESPONSES = BASE / "data" / "model_responses.jsonl"
HUMAN = BASE / "data" / "human_validation_results.jsonl"
SAMPLE = BASE / "data" / "human_validation_sample.jsonl"
SUMMARY = BASE / "data" / "benchmark_summary.json"

LABELS = ("correct", "incorrect", "not_attempted")

EXPECTED_JUDGE = {
    "correct": 130,
    "incorrect": 165,
    "not_attempted": 5,
}
EXPECTED_HUMAN = {
    "correct": 19,
    "incorrect": 39,
    "not_attempted": 2,
}
EXPECTED_AGREEMENTS = 45
EXPECTED_DISAGREEMENTS = 15
EXPECTED_KAPPA = 0.515


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def cohen_kappa(human: list[str], judge: list[str]) -> float:
    n = len(human)
    observed = sum(h == j for h, j in zip(human, judge)) / n
    hc = Counter(human)
    jc = Counter(judge)
    expected = sum((hc[label] / n) * (jc[label] / n) for label in LABELS)
    return (observed - expected) / (1 - expected)


def fail(message: str) -> None:
    raise SystemExit(f"FAILED: {message}")


def main() -> None:
    responses = read_jsonl(RESPONSES)
    human_rows = read_jsonl(HUMAN)
    sample_rows = read_jsonl(SAMPLE)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    if len(responses) != 300:
        fail(f"expected 300 responses, found {len(responses)}")
    if len(human_rows) != 60 or len(sample_rows) != 60:
        fail("expected exactly 60 human-validation rows and 60 sample rows")

    judge_counts = Counter(r["judge_label"] for r in responses)
    if dict(judge_counts) != EXPECTED_JUDGE:
        fail(f"judge counts changed: {dict(judge_counts)}")

    human_by_id = {r["case_id"]: r for r in human_rows}
    response_by_id = {r["case_id"]: r for r in responses}
    sample_ids = [r["case_id"] for r in sample_rows]

    if len(set(sample_ids)) != 60:
        fail("human-validation sample contains duplicate IDs")
    if set(sample_ids) != set(human_by_id):
        fail("human-validation sample and human results do not contain the same IDs")

    human_labels = [human_by_id[cid]["human_label"] for cid in sample_ids]
    judge_labels = [response_by_id[cid]["judge_label"] for cid in sample_ids]

    human_counts = Counter(human_labels)
    if dict(human_counts) != EXPECTED_HUMAN:
        fail(f"human label counts changed: {dict(human_counts)}")

    agreements = sum(h == j for h, j in zip(human_labels, judge_labels))
    if agreements != EXPECTED_AGREEMENTS:
        fail(f"judge-human agreements changed: {agreements}/60")

    disagreements = 60 - agreements
    if disagreements != EXPECTED_DISAGREEMENTS:
        fail(f"judge-human disagreements changed: {disagreements}")

    kappa = cohen_kappa(human_labels, judge_labels)
    if not math.isclose(kappa, EXPECTED_KAPPA, abs_tol=0.0005):
        fail(f"Cohen's kappa changed: {kappa:.6f}")

    overall = summary.get("overall_judge", {})
    expected_overall = {
        "n": 300,
        "correct": 130,
        "incorrect": 165,
        "not_attempted": 5,
    }
    for key, expected in expected_overall.items():
        if overall.get(key) != expected:
            fail(f"benchmark_summary overall_judge.{key}={overall.get(key)!r}, expected {expected}")

    human_summary = summary.get("human_validation_sample", {})
    expected_human_summary = {
        "n": 60,
        "correct": 19,
        "incorrect": 39,
        "not_attempted": 2,
    }
    for key, expected in expected_human_summary.items():
        if human_summary.get(key) != expected:
            fail(
                f"benchmark_summary human_validation_sample.{key}="
                f"{human_summary.get(key)!r}, expected {expected}"
            )

    checked = [r for r in responses if r.get("human_checked") is True]
    if len(checked) != 60:
        fail(f"model_responses contains {len(checked)} human-checked rows, expected 60")

    print("Frozen-result verification")
    print("==========================")
    print("Judge labels:             130 correct / 165 incorrect / 5 not_attempted")
    print("Human labels:              19 correct / 39 incorrect / 2 not_attempted")
    print("Judge-human agreement:     45/60 (75.0%)")
    print(f"Cohen's kappa:             {kappa:.3f}")
    print("PASS: reproduced metrics match the frozen submission results.")


if __name__ == "__main__":
    main()
