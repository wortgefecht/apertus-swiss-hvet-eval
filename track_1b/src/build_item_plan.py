#!/usr/bin/env python3
"""Build the deterministic 300-item benchmark plan from the verified fact bank."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

DIFFICULTY_BY_MODE = {
    "direct_fact": "basic",
    "reverse_lookup": "basic",
    "resource_lookup": "basic",
    "format_rule": "basic",

    "classification": "intermediate",
    "relationship": "intermediate",
    "responsibility": "intermediate",
    "comparison": "intermediate",
    "document_lookup": "intermediate",
    "progression": "intermediate",
    "calculation": "intermediate",
    "date_rule": "intermediate",
    "application": "intermediate",

    "misconception": "advanced",
    "boundary": "advanced",
    "edge_case": "advanced",
    "exclusion": "advanced",
}

PLAN_VERSION = "1.0"
PLANNING_RULE = "one_item_per_declared_question_mode"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
    return rows


def fact_number(fact_id: str) -> int:
    try:
        prefix, number = fact_id[0], int(fact_id[1:])
    except (ValueError, IndexError):
        raise SystemExit(f"Invalid fact_id: {fact_id!r}")
    if prefix != "F":
        raise SystemExit(f"Invalid fact_id: {fact_id!r}")
    return number


def validate_fact_bank(facts: list[dict]) -> None:
    if len(facts) != 100:
        raise SystemExit(f"Expected 100 facts, found {len(facts)}")

    ids = [row.get("fact_id") for row in facts]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate fact_id in fact bank")

    expected_ids = [f"F{i:03d}" for i in range(1, 101)]
    if sorted(ids, key=fact_number) != expected_ids:
        raise SystemExit("Expected consecutive fact IDs F001–F100")

    for row in facts:
        fid = row["fact_id"]

        if row.get("verification_status") != "verified":
            raise SystemExit(f"{fid}: verification_status is not 'verified'")

        modes = row.get("question_modes")
        if not isinstance(modes, list) or len(modes) != 3:
            raise SystemExit(f"{fid}: expected exactly 3 question_modes")

        if len(modes) != len(set(modes)):
            raise SystemExit(f"{fid}: duplicate question_mode")

        unknown = [mode for mode in modes if mode not in DIFFICULTY_BY_MODE]
        if unknown:
            raise SystemExit(f"{fid}: unknown question modes: {unknown}")

        if not row.get("category"):
            raise SystemExit(f"{fid}: missing category")

        if not row.get("subcategory"):
            raise SystemExit(f"{fid}: missing subcategory")

        if not row.get("reference_date"):
            raise SystemExit(f"{fid}: missing reference_date")


def build_plan(facts: list[dict]) -> list[dict]:
    plan = []
    case_number = 1

    for fact in sorted(facts, key=lambda row: fact_number(row["fact_id"])):
        for variant_index, question_type in enumerate(fact["question_modes"], start=1):
            plan.append(
                {
                    "case_id": f"PE-{case_number:03d}",
                    "fact_id": fact["fact_id"],
                    "category": fact["category"],
                    "subcategory": fact["subcategory"],
                    "question_type": question_type,
                    "difficulty": DIFFICULTY_BY_MODE[question_type],
                    "variant_index": variant_index,
                    "reference_date": fact["reference_date"],
                    "plan_version": PLAN_VERSION,
                    "planning_rule": PLANNING_RULE,
                }
            )
            case_number += 1

    return plan


def validate_plan(plan: list[dict], facts: list[dict]) -> None:
    if len(plan) != 300:
        raise SystemExit(f"Expected 300 planned items, found {len(plan)}")

    case_ids = [row["case_id"] for row in plan]
    if len(case_ids) != len(set(case_ids)):
        raise SystemExit("Duplicate case_id in item plan")

    expected_cases = [f"PE-{i:03d}" for i in range(1, 301)]
    if case_ids != expected_cases:
        raise SystemExit("Case IDs are not consecutive PE-001–PE-300")

    counts_by_fact = Counter(row["fact_id"] for row in plan)
    bad_counts = {fid: count for fid, count in counts_by_fact.items() if count != 3}
    if bad_counts:
        raise SystemExit(f"Each fact must occur exactly 3 times: {bad_counts}")

    fact_by_id = {row["fact_id"]: row for row in facts}
    planned_pairs = Counter((row["fact_id"], row["question_type"]) for row in plan)

    for fid, fact in fact_by_id.items():
        for mode in fact["question_modes"]:
            if planned_pairs[(fid, mode)] != 1:
                raise SystemExit(
                    f"Expected exactly one planned item for ({fid}, {mode}), "
                    f"found {planned_pairs[(fid, mode)]}"
                )


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":"))
            for row in rows
        ) + "\n",
        encoding="utf-8",
    )


def print_summary(plan: list[dict]) -> None:
    print(f"Plan version: {PLAN_VERSION}")
    print(f"Planning rule: {PLANNING_RULE}")
    print(f"Items: {len(plan)}")
    print(f"Unique facts: {len(set(row['fact_id'] for row in plan))}")

    print("\nCategories:")
    for key, value in sorted(Counter(row["category"] for row in plan).items()):
        print(f"  {key}: {value}")

    print("\nQuestion types:")
    for key, value in sorted(Counter(row["question_type"] for row in plan).items()):
        print(f"  {key}: {value}")

    print("\nDifficulty:")
    for key in ("basic", "intermediate", "advanced"):
        value = Counter(row["difficulty"] for row in plan)[key]
        print(f"  {key}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("track_1b/data/fact_bank.jsonl"),
        help="Verified fact bank JSONL",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("track_1b/data/item_plan.jsonl"),
        help="Output benchmark item plan JSONL",
    )
    args = parser.parse_args()

    facts = load_jsonl(args.input)
    validate_fact_bank(facts)

    plan = build_plan(facts)
    validate_plan(plan, facts)
    write_jsonl(args.output, plan)

    print(f"Wrote: {args.output}")
    print_summary(plan)


if __name__ == "__main__":
    main()
