#!/usr/bin/env python3
"""Produce benchmark result summaries by category, question type, and difficulty."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path("track_1b")
RESP = BASE / "data" / "model_responses.jsonl"
META = BASE / "data" / "metadata.jsonl"
OUT_JSON = BASE / "data" / "benchmark_summary.json"
OUT_CSV = BASE / "data" / "benchmark_breakdown.csv"

LABELS = ["correct", "incorrect", "not_attempted"]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def wilson(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = successes / n
    denom = 1 + z*z/n
    centre = (p + z*z/(2*n)) / denom
    margin = z * math.sqrt((p*(1-p)/n) + (z*z/(4*n*n))) / denom
    return centre - margin, centre + margin


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    counts = Counter(r["judge_label"] for r in rows)
    correct = counts["correct"]
    low, high = wilson(correct, n)
    return {
        "n": n,
        "correct": correct,
        "incorrect": counts["incorrect"],
        "not_attempted": counts["not_attempted"],
        "accuracy": correct / n if n else None,
        "accuracy_ci95_low": low if n else None,
        "accuracy_ci95_high": high if n else None,
    }


def grouped(rows: list[dict], field: str) -> dict[str, dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[str(row[field])].append(row)
    return {key: summarize(value) for key, value in sorted(groups.items())}


def main() -> None:
    responses = read_jsonl(RESP)
    metadata = read_jsonl(META)

    if len(responses) != 300 or len(metadata) != 300:
        raise SystemExit("Expected 300 response rows and 300 metadata rows.")

    meta_by_id = {r["case_id"]: r for r in metadata}
    rows = []
    for r in responses:
        cid = r["case_id"]
        if cid not in meta_by_id:
            raise SystemExit(f"Missing metadata for {cid}")
        m = meta_by_id[cid]
        rows.append({
            "case_id": cid,
            "judge_label": r["judge_label"],
            "human_checked": r["human_checked"],
            "human_label": r["human_label"],
            "category": m["category"],
            "question_type": m["question_type"],
            "difficulty": m["difficulty"],
        })

    overall = summarize(rows)
    by_category = grouped(rows, "category")
    by_question_type = grouped(rows, "question_type")
    by_difficulty = grouped(rows, "difficulty")

    category_accuracies = [
        summary["accuracy"] for summary in by_category.values() if summary["n"] > 0
    ]
    macro_category_accuracy = (
        sum(category_accuracies) / len(category_accuracies)
        if category_accuracies else None
    )

    human_rows = [r for r in rows if r["human_checked"]]
    human_summary = None
    if human_rows:
        human_counts = Counter(r["human_label"] for r in human_rows)
        human_correct = human_counts["correct"]
        low, high = wilson(human_correct, len(human_rows))
        human_summary = {
            "n": len(human_rows),
            "correct": human_correct,
            "incorrect": human_counts["incorrect"],
            "not_attempted": human_counts["not_attempted"],
            "accuracy": human_correct / len(human_rows),
            "accuracy_ci95_low": low,
            "accuracy_ci95_high": high,
        }

    summary = {
        "overall_judge": overall,
        "macro_category_accuracy": macro_category_accuracy,
        "human_validation_sample": human_summary,
        "by_category": by_category,
        "by_question_type": by_question_type,
        "by_difficulty": by_difficulty,
    }

    OUT_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "dimension", "value", "n", "correct", "incorrect", "not_attempted",
            "accuracy", "ci95_low", "ci95_high"
        ])
        for dimension, groups in (
            ("category", by_category),
            ("question_type", by_question_type),
            ("difficulty", by_difficulty),
        ):
            for value, s in groups.items():
                writer.writerow([
                    dimension, value, s["n"], s["correct"], s["incorrect"],
                    s["not_attempted"], f"{s['accuracy']:.6f}",
                    f"{s['accuracy_ci95_low']:.6f}",
                    f"{s['accuracy_ci95_high']:.6f}",
                ])

    print("Benchmark summary")
    print("=================")
    print(
        f"Overall judge accuracy: {overall['correct']}/{overall['n']} "
        f"({100*overall['accuracy']:.1f}%; "
        f"95% CI {100*overall['accuracy_ci95_low']:.1f}–"
        f"{100*overall['accuracy_ci95_high']:.1f}%)"
    )
    print(f"Macro category accuracy: {100*macro_category_accuracy:.1f}%")
    if human_summary:
        print(
            f"Human sample accuracy:  {human_summary['correct']}/{human_summary['n']} "
            f"({100*human_summary['accuracy']:.1f}%)"
        )
    print()

    print("By category")
    for name, s in sorted(by_category.items(), key=lambda kv: kv[1]["accuracy"]):
        print(
            f"  {name:38s} {s['correct']:3d}/{s['n']:3d} "
            f"{100*s['accuracy']:5.1f}%"
        )
    print()

    print("By difficulty")
    for name, s in sorted(by_difficulty.items()):
        print(
            f"  {name:16s} {s['correct']:3d}/{s['n']:3d} "
            f"{100*s['accuracy']:5.1f}%"
        )
    print()

    print("By question type")
    for name, s in sorted(by_question_type.items(), key=lambda kv: kv[1]["accuracy"]):
        print(
            f"  {name:24s} {s['correct']:3d}/{s['n']:3d} "
            f"{100*s['accuracy']:5.1f}%"
        )

    print()
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_CSV}")


if __name__ == "__main__":
    main()
