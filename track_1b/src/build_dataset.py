#!/usr/bin/env python3
"""Build evaluation.jsonl and metadata.jsonl from the reviewed authoring layer."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

DEFAULT_FACT_BANK = Path("track_1b/data/fact_bank.jsonl")
DEFAULT_PLAN = Path("track_1b/data/item_plan.jsonl")
DEFAULT_AUTHORED = Path("track_1b/data/authored_items.jsonl")
DEFAULT_EVAL = Path("track_1b/data/evaluation.jsonl")
DEFAULT_META = Path("track_1b/data/metadata.jsonl")

ITEM_LICENSE = "CDLA-Permissive-2.0"
SOURCE_RIGHTS_NOTE = (
    "Benchmark wording is original paraphrase. Source facts are referenced from "
    "authoritative Swiss federal sources; rights in source material remain with the "
    "respective source provider."
)
CURATION_METHOD = (
    "Verified human-curated fact bank; deterministic item plan; LLM-assisted item "
    "drafting; human review before release."
)
LANGUAGE = "de-CH"


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"File not found: {path}")
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":"))
            for row in rows
        ) + "\n",
        encoding="utf-8",
    )


def validate(
    facts: list[dict],
    plan: list[dict],
    authored: list[dict],
    allow_partial: bool,
) -> list[str]:
    errors: list[str] = []
    facts_by_id = {r["fact_id"]: r for r in facts}
    plan_by_case = {r["case_id"]: r for r in plan}

    if len(facts) != 100:
        errors.append(f"Expected 100 facts, found {len(facts)}")
    if len(plan) != 300:
        errors.append(f"Expected 300 planned items, found {len(plan)}")

    authored_ids = [r.get("case_id") for r in authored]
    if len(authored_ids) != len(set(authored_ids)):
        errors.append("Duplicate case_id in authored_items.jsonl")

    if not allow_partial and len(authored) != 300:
        errors.append(f"Expected 300 authored items, found {len(authored)}")
    if allow_partial and len(authored) > 300:
        errors.append(f"Authored item count exceeds 300: {len(authored)}")

    required = {
        "case_id",
        "fact_id",
        "question_type",
        "question",
        "reference_answer",
        "answer_variations",
        "misconception_target",
    }

    for idx, row in enumerate(authored, 1):
        cid = row.get("case_id", f"row {idx}")
        missing = required - set(row)
        if missing:
            errors.append(f"{cid}: missing fields {sorted(missing)}")
            continue

        if cid not in plan_by_case:
            errors.append(f"{cid}: not present in item plan")
            continue

        planned = plan_by_case[cid]
        fid = row["fact_id"]

        if fid != planned["fact_id"]:
            errors.append(
                f"{cid}: fact_id {fid!r} != planned {planned['fact_id']!r}"
            )
        if row["question_type"] != planned["question_type"]:
            errors.append(
                f"{cid}: question_type {row['question_type']!r} != "
                f"planned {planned['question_type']!r}"
            )
        if fid not in facts_by_id:
            errors.append(f"{cid}: unknown fact_id {fid!r}")

        if not isinstance(row["question"], str) or not row["question"].strip():
            errors.append(f"{cid}: empty question")
        if not isinstance(row["reference_answer"], str) or not row["reference_answer"].strip():
            errors.append(f"{cid}: empty reference_answer")

        variations = row["answer_variations"]
        if not isinstance(variations, list) or len(variations) < 2:
            errors.append(f"{cid}: requires at least two answer_variations")
        elif any(not isinstance(v, str) or not v.strip() for v in variations):
            errors.append(f"{cid}: answer_variations contain empty/non-string value")
        elif len(set(v.strip() for v in variations)) != len(variations):
            errors.append(f"{cid}: duplicate answer_variations")

        target = row["misconception_target"]
        if target is not None and (not isinstance(target, str) or not target.strip()):
            errors.append(f"{cid}: misconception_target must be non-empty string or null")

        if row["question_type"] == "misconception" and target is None:
            errors.append(f"{cid}: misconception item requires misconception_target")

    questions = [r.get("question", "").strip().casefold() for r in authored]
    nonempty = [q for q in questions if q]
    if len(nonempty) != len(set(nonempty)):
        errors.append("Exact duplicate question text detected")

    if not allow_partial:
        expected = [f"PE-{i:03d}" for i in range(1, 301)]
        if authored_ids != expected:
            errors.append(
                "Final authored_items.jsonl must be ordered exactly PE-001..PE-300"
            )

    return errors


def build_rows(
    facts: list[dict],
    plan: list[dict],
    authored: list[dict],
) -> tuple[list[dict], list[dict]]:
    facts_by_id = {r["fact_id"]: r for r in facts}
    plan_by_case = {r["case_id"]: r for r in plan}

    evaluation = []
    metadata = []

    for item in authored:
        cid = item["case_id"]
        planned = plan_by_case[cid]
        fact = facts_by_id[item["fact_id"]]
        sources = fact["sources"]

        evaluation.append(
            {
                "case_id": cid,
                "question": item["question"].strip(),
                "reference_answer": item["reference_answer"].strip(),
                "answer_variations": [v.strip() for v in item["answer_variations"]],
                "source_citations": list(dict.fromkeys(s["url"] for s in sources)),
            }
        )

        metadata.append(
            {
                "case_id": cid,
                "fact_id": fact["fact_id"],
                "category": planned["category"],
                "subcategory": planned["subcategory"],
                "difficulty": planned["difficulty"],
                "question_type": planned["question_type"],
                "misconception_target": item["misconception_target"],
                "reference_date": planned["reference_date"],
                "source_type": [s["source_type"] for s in sources],
                "source_authority": [s["authority"] for s in sources],
                "source_title": [s["title"] for s in sources],
                "source_url": [s["url"] for s in sources],
                "item_license": ITEM_LICENSE,
                "source_rights_note": SOURCE_RIGHTS_NOTE,
                "retrieved_at": [s["retrieved_at"] for s in sources],
                "curation_method": CURATION_METHOD,
                "language": LANGUAGE,
            }
        )

    return evaluation, metadata


def print_summary(authored: list[dict], plan: list[dict]) -> None:
    plan_by_case = {r["case_id"]: r for r in plan}
    print(f"Authored items: {len(authored)}")
    print(f"Unique facts: {len(set(r['fact_id'] for r in authored))}")

    type_counts = Counter(r["question_type"] for r in authored)
    print("Question types:")
    for key, value in sorted(type_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {key:34s} {value:3d}")

    difficulty_counts = Counter(
        plan_by_case[r["case_id"]]["difficulty"]
        for r in authored
        if r["case_id"] in plan_by_case
    )
    print("Difficulty:")
    for key in ("basic", "intermediate", "advanced"):
        print(f"  {key:34s} {difficulty_counts[key]:3d}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fact-bank", type=Path, default=DEFAULT_FACT_BANK)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--authored", type=Path, default=DEFAULT_AUTHORED)
    parser.add_argument("--evaluation", type=Path, default=DEFAULT_EVAL)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_META)
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    facts = read_jsonl(args.fact_bank)
    plan = read_jsonl(args.plan)
    authored = read_jsonl(args.authored)

    errors = validate(facts, plan, authored, args.allow_partial)

    print_summary(authored, plan)
    if errors:
        print("\nFAILED")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("\nPASS: authoring layer is structurally valid.")

    if args.validate_only:
        return

    if args.allow_partial:
        print("Partial mode: validation only; final dataset files were not written.")
        return

    evaluation, metadata = build_rows(facts, plan, authored)
    write_jsonl(args.evaluation, evaluation)
    write_jsonl(args.metadata, metadata)

    print(f"Wrote {len(evaluation)} rows to {args.evaluation}")
    print(f"Wrote {len(metadata)} rows to {args.metadata}")


if __name__ == "__main__":
    main()
