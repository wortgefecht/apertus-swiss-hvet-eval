#!/usr/bin/env python3
"""Validate the deterministic benchmark item plan against the verified fact bank."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

FACT_BANK = Path("track_1b/data/fact_bank.jsonl")
ITEM_PLAN = Path("track_1b/data/item_plan.jsonl")

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

EXPECTED_CATEGORY_COUNTS = {
    "system_structure": 9,
    "qualifications_titles": 21,
    "access_pathways_progression": 30,
    "recognition_quality_regulation": 87,
    "institutions_responsibilities": 21,
    "reforms_2026_edge_cases": 63,
    "funding_financing": 69,
}

EXPECTED_DIFFICULTY_COUNTS = {
    "basic": 93,
    "intermediate": 116,
    "advanced": 91,
}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"ERROR: file not found: {path}")
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"ERROR: {path}:{lineno}: {exc}") from exc
    return rows


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> None:
    facts = read_jsonl(FACT_BANK)
    plan = read_jsonl(ITEM_PLAN)
    errors: list[str] = []

    facts_by_id = {r.get("fact_id"): r for r in facts}

    if len(facts) != 100:
        fail(errors, f"fact bank: expected 100 rows, found {len(facts)}")
    if len(facts_by_id) != len(facts):
        fail(errors, "fact bank: duplicate fact_id")

    if len(plan) != 300:
        fail(errors, f"item plan: expected 300 rows, found {len(plan)}")

    case_ids = [r.get("case_id") for r in plan]
    expected_case_ids = [f"PE-{i:03d}" for i in range(1, 301)]
    if case_ids != expected_case_ids:
        fail(errors, "case IDs are not exactly consecutive PE-001..PE-300")
    if len(set(case_ids)) != len(case_ids):
        fail(errors, "duplicate case_id")

    per_fact = Counter()
    planned_pairs = Counter()
    per_fact_modes = defaultdict(list)

    required = {
        "case_id", "fact_id", "category", "subcategory", "question_type",
        "difficulty", "variant_index", "reference_date",
        "plan_version", "planning_rule",
    }

    for idx, row in enumerate(plan, 1):
        cid = row.get("case_id", f"row {idx}")
        missing = required - set(row)
        if missing:
            fail(errors, f"{cid}: missing fields {sorted(missing)}")
            continue

        fid = row["fact_id"]
        if fid not in facts_by_id:
            fail(errors, f"{cid}: unknown fact_id {fid}")
            continue

        fact = facts_by_id[fid]
        mode = row["question_type"]

        per_fact[fid] += 1
        planned_pairs[(fid, mode)] += 1
        per_fact_modes[fid].append(mode)

        if row["category"] != fact["category"]:
            fail(errors, f"{cid}: category mismatch for {fid}")
        if row["subcategory"] != fact["subcategory"]:
            fail(errors, f"{cid}: subcategory mismatch for {fid}")
        if row["reference_date"] != fact["reference_date"]:
            fail(errors, f"{cid}: reference_date mismatch for {fid}")

        if mode not in fact["question_modes"]:
            fail(errors, f"{cid}: mode {mode!r} not declared by {fid}")

        expected_diff = DIFFICULTY_BY_MODE.get(mode)
        if expected_diff is None:
            fail(errors, f"{cid}: unknown question_type {mode!r}")
        elif row["difficulty"] != expected_diff:
            fail(
                errors,
                f"{cid}: difficulty {row['difficulty']!r}, expected {expected_diff!r}"
            )

        if row["variant_index"] not in (1, 2, 3):
            fail(errors, f"{cid}: invalid variant_index {row['variant_index']!r}")

    for fid, fact in sorted(facts_by_id.items()):
        if per_fact[fid] != 3:
            fail(errors, f"{fid}: expected 3 planned items, found {per_fact[fid]}")

        expected_modes = fact["question_modes"]
        actual_modes = per_fact_modes[fid]
        if actual_modes != expected_modes:
            fail(
                errors,
                f"{fid}: question-mode order/content mismatch: "
                f"expected {expected_modes}, found {actual_modes}"
            )

        for mode in expected_modes:
            if planned_pairs[(fid, mode)] != 1:
                fail(
                    errors,
                    f"{fid}/{mode}: expected exactly one item, "
                    f"found {planned_pairs[(fid, mode)]}"
                )

    category_counts = Counter(r["category"] for r in plan)
    difficulty_counts = Counter(r["difficulty"] for r in plan)
    type_counts = Counter(r["question_type"] for r in plan)

    if dict(category_counts) != EXPECTED_CATEGORY_COUNTS:
        fail(
            errors,
            f"category counts differ: {dict(category_counts)}"
        )
    if dict(difficulty_counts) != EXPECTED_DIFFICULTY_COUNTS:
        fail(
            errors,
            f"difficulty counts differ: {dict(difficulty_counts)}"
        )

    print("Benchmark item plan validation")
    print("==============================")
    print(f"Fact bank records:   {len(facts)}")
    print(f"Planned items:       {len(plan)}")
    print(f"Unique case IDs:     {len(set(case_ids))}")
    print(f"Facts represented:   {len(per_fact)}")
    print()

    print("Categories")
    for key in EXPECTED_CATEGORY_COUNTS:
        print(f"  {key:34s} {category_counts[key]:3d}")
    print()

    print("Difficulty")
    for key in ("basic", "intermediate", "advanced"):
        print(f"  {key:34s} {difficulty_counts[key]:3d}")
    print()

    print("Question types")
    for key, value in sorted(type_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {key:34s} {value:3d}")
    print()

    # Structural concentration indicators for methodological review.
    top3 = category_counts["recognition_quality_regulation"] + \
           category_counts["reforms_2026_edge_cases"] + \
           category_counts["funding_financing"]
    print(f"Top three regulation/reform/funding categories: {top3}/300 ({top3/3:.1f}%)")
    print("Note: report overall accuracy AND macro-average across categories.")
    print()

    if errors:
        print("FAILED")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("PASS: item plan is structurally consistent with fact_bank.jsonl.")


if __name__ == "__main__":
    main()
