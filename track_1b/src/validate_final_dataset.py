#!/usr/bin/env python3
"""Technical validation of the final Track 1B benchmark dataset."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

BASE = Path("track_1b/data")
FACT_BANK = BASE / "fact_bank.jsonl"
ITEM_PLAN = BASE / "item_plan.jsonl"
AUTHORED = BASE / "authored_items.jsonl"
EVALUATION = BASE / "evaluation.jsonl"
METADATA = BASE / "metadata.jsonl"

EXPECTED_EVAL_KEYS = {
    "case_id",
    "question",
    "reference_answer",
    "answer_variations",
    "source_citations",
}

EXPECTED_META_KEYS = {
    "case_id",
    "fact_id",
    "category",
    "subcategory",
    "difficulty",
    "question_type",
    "misconception_target",
    "reference_date",
    "source_type",
    "source_authority",
    "source_title",
    "source_url",
    "item_license",
    "source_rights_note",
    "retrieved_at",
    "curation_method",
    "language",
}

EXPECTED_LICENSE = "CDLA-Permissive-2.0"
EXPECTED_LANGUAGE = "de-CH"
EXPECTED_REFERENCE_DATE = "2026-10-01"
NEAR_DUPLICATE_THRESHOLD = 0.90


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"ERROR: file not found: {path}")

    rows = []
    raw = path.read_bytes()

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"ERROR: {path} is not valid UTF-8: {exc}") from exc

    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"ERROR: {path}:{lineno}: invalid JSON: {exc}") from exc
        if not isinstance(obj, dict):
            raise SystemExit(f"ERROR: {path}:{lineno}: record is not a JSON object")
        rows.append(obj)

    return rows


def normalise_text(value: str) -> str:
    value = value.casefold()
    value = re.sub(r"[^\wäöüéèàç'’]+", " ", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def is_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def add_warning(warnings: list[str], message: str) -> None:
    warnings.append(message)


def main() -> None:
    facts = read_jsonl(FACT_BANK)
    plan = read_jsonl(ITEM_PLAN)
    authored = read_jsonl(AUTHORED)
    evaluation = read_jsonl(EVALUATION)
    metadata = read_jsonl(METADATA)

    errors: list[str] = []
    warnings: list[str] = []

    facts_by_id = {r["fact_id"]: r for r in facts}
    plan_by_case = {r["case_id"]: r for r in plan}
    authored_by_case = {r["case_id"]: r for r in authored}
    eval_by_case = {r["case_id"]: r for r in evaluation}
    meta_by_case = {r["case_id"]: r for r in metadata}

    expected_case_ids = [f"PE-{i:03d}" for i in range(1, 301)]

    # ---------- Counts and ordering ----------
    expected_counts = {
        "fact_bank.jsonl": (facts, 100),
        "item_plan.jsonl": (plan, 300),
        "authored_items.jsonl": (authored, 300),
        "evaluation.jsonl": (evaluation, 300),
        "metadata.jsonl": (metadata, 300),
    }

    for name, (rows, expected) in expected_counts.items():
        if len(rows) != expected:
            add_error(errors, f"{name}: expected {expected} records, found {len(rows)}")

    for name, rows in [
        ("item_plan.jsonl", plan),
        ("authored_items.jsonl", authored),
        ("evaluation.jsonl", evaluation),
        ("metadata.jsonl", metadata),
    ]:
        ids = [r.get("case_id") for r in rows]
        if len(ids) != len(set(ids)):
            add_error(errors, f"{name}: duplicate case_id")
        if ids != expected_case_ids:
            add_error(errors, f"{name}: case_id order is not exactly PE-001..PE-300")

    # ---------- Exact schema ----------
    for row in evaluation:
        cid = row.get("case_id", "?")
        keys = set(row)
        if keys != EXPECTED_EVAL_KEYS:
            add_error(
                errors,
                f"{cid}: evaluation keys differ; missing={sorted(EXPECTED_EVAL_KEYS-keys)}, "
                f"extra={sorted(keys-EXPECTED_EVAL_KEYS)}"
            )

    for row in metadata:
        cid = row.get("case_id", "?")
        keys = set(row)
        if keys != EXPECTED_META_KEYS:
            add_error(
                errors,
                f"{cid}: metadata keys differ; missing={sorted(EXPECTED_META_KEYS-keys)}, "
                f"extra={sorted(keys-EXPECTED_META_KEYS)}"
            )

    # ---------- Cross-file consistency ----------
    if set(plan_by_case) != set(authored_by_case) or set(plan_by_case) != set(eval_by_case) or set(plan_by_case) != set(meta_by_case):
        add_error(errors, "case_id sets differ across plan/authored/evaluation/metadata")

    questions_normalised: dict[str, str] = {}

    for cid in expected_case_ids:
        if cid not in plan_by_case or cid not in authored_by_case or cid not in eval_by_case or cid not in meta_by_case:
            continue

        planned = plan_by_case[cid]
        authored_item = authored_by_case[cid]
        ev = eval_by_case[cid]
        meta = meta_by_case[cid]

        fid = planned["fact_id"]
        if fid not in facts_by_id:
            add_error(errors, f"{cid}: unknown fact_id {fid}")
            continue
        fact = facts_by_id[fid]

        # authored -> evaluation
        if ev["question"] != authored_item["question"].strip():
            add_error(errors, f"{cid}: evaluation question differs from authored item")
        if ev["reference_answer"] != authored_item["reference_answer"].strip():
            add_error(errors, f"{cid}: evaluation reference_answer differs from authored item")
        expected_variations = [v.strip() for v in authored_item["answer_variations"]]
        if ev["answer_variations"] != expected_variations:
            add_error(errors, f"{cid}: answer_variations differ from authored item")

        # plan/fact -> metadata
        comparisons = {
            "fact_id": fid,
            "category": planned["category"],
            "subcategory": planned["subcategory"],
            "difficulty": planned["difficulty"],
            "question_type": planned["question_type"],
            "reference_date": planned["reference_date"],
        }
        for field, expected in comparisons.items():
            if meta.get(field) != expected:
                add_error(errors, f"{cid}: metadata {field}={meta.get(field)!r}, expected {expected!r}")

        if meta.get("misconception_target") != authored_item.get("misconception_target"):
            add_error(errors, f"{cid}: misconception_target differs from authored item")

        if meta.get("language") != EXPECTED_LANGUAGE:
            add_error(errors, f"{cid}: language must be {EXPECTED_LANGUAGE!r}")
        if meta.get("item_license") != EXPECTED_LICENSE:
            add_error(errors, f"{cid}: item_license must be {EXPECTED_LICENSE!r}")
        if meta.get("reference_date") != EXPECTED_REFERENCE_DATE:
            add_error(errors, f"{cid}: unexpected reference_date {meta.get('reference_date')!r}")

        # source provenance
        fact_sources = fact["sources"]
        expected_urls = list(dict.fromkeys(s["url"] for s in fact_sources))
        if ev["source_citations"] != expected_urls:
            add_error(errors, f"{cid}: source_citations do not match assigned fact")

        expected_source_fields = {
            "source_type": [s["source_type"] for s in fact_sources],
            "source_authority": [s["authority"] for s in fact_sources],
            "source_title": [s["title"] for s in fact_sources],
            "source_url": [s["url"] for s in fact_sources],
            "retrieved_at": [s["retrieved_at"] for s in fact_sources],
        }
        for field, expected in expected_source_fields.items():
            if meta.get(field) != expected:
                add_error(errors, f"{cid}: metadata {field} does not match fact-bank sources")

        source_lengths = [
            len(meta["source_type"]),
            len(meta["source_authority"]),
            len(meta["source_title"]),
            len(meta["source_url"]),
            len(meta["retrieved_at"]),
        ]
        if len(set(source_lengths)) != 1:
            add_error(errors, f"{cid}: source metadata arrays have inconsistent lengths")

        for url in ev["source_citations"]:
            if not is_http_url(url):
                add_error(errors, f"{cid}: invalid source URL {url!r}")

        # content-shape checks
        if not isinstance(ev["question"], str) or not ev["question"].strip():
            add_error(errors, f"{cid}: empty question")
        if not isinstance(ev["reference_answer"], str) or not ev["reference_answer"].strip():
            add_error(errors, f"{cid}: empty reference_answer")

        variations = ev["answer_variations"]
        if not isinstance(variations, list) or len(variations) < 2:
            add_error(errors, f"{cid}: fewer than two answer_variations")
        else:
            norm_vars = [normalise_text(v) for v in variations]
            if len(norm_vars) != len(set(norm_vars)):
                add_error(errors, f"{cid}: duplicate answer variation after normalisation")
            ref_norm = normalise_text(ev["reference_answer"])
            if ref_norm in set(norm_vars):
                add_warning(warnings, f"{cid}: answer variation duplicates reference answer after normalisation")

        qnorm = normalise_text(ev["question"])
        if not qnorm:
            add_error(errors, f"{cid}: question normalises to empty string")
        elif qnorm in questions_normalised:
            add_error(
                errors,
                f"{cid}: exact normalised duplicate of {questions_normalised[qnorm]}"
            )
        else:
            questions_normalised[qnorm] = cid

        # misconception field discipline
        target = meta["misconception_target"]
        if meta["question_type"] == "misconception":
            if not isinstance(target, str) or not target.strip():
                add_error(errors, f"{cid}: misconception item lacks target")
        elif target is not None:
            add_warning(warnings, f"{cid}: non-misconception item has misconception_target")

    # ---------- Representation balance ----------
    fact_counts = Counter(r["fact_id"] for r in metadata)
    bad_fact_counts = {fid: n for fid, n in fact_counts.items() if n != 3}
    if bad_fact_counts:
        add_error(errors, f"Each fact must appear exactly 3 times: {bad_fact_counts}")

    # ---------- Near-duplicate question scan ----------
    qrows = [(r["case_id"], normalise_text(r["question"])) for r in evaluation]
    near_duplicates: list[tuple[float, str, str]] = []
    for i in range(len(qrows)):
        cid_a, qa = qrows[i]
        for j in range(i + 1, len(qrows)):
            cid_b, qb = qrows[j]
            ratio = SequenceMatcher(None, qa, qb).ratio()
            if ratio >= NEAR_DUPLICATE_THRESHOLD:
                near_duplicates.append((ratio, cid_a, cid_b))

    near_duplicates.sort(reverse=True)

    # ---------- Report ----------
    print("Final benchmark technical validation")
    print("====================================")
    print(f"Fact bank records:       {len(facts)}")
    print(f"Item-plan records:       {len(plan)}")
    print(f"Authored records:        {len(authored)}")
    print(f"Evaluation records:      {len(evaluation)}")
    print(f"Metadata records:        {len(metadata)}")
    print(f"Unique facts represented:{len(fact_counts):>8}")
    print()

    print("Question types")
    for key, value in sorted(Counter(r["question_type"] for r in metadata).items(), key=lambda x: (-x[1], x[0])):
        print(f"  {key:34s} {value:3d}")
    print()

    print("Difficulty")
    for key in ("basic", "intermediate", "advanced"):
        print(f"  {key:34s} {Counter(r['difficulty'] for r in metadata)[key]:3d}")
    print()

    print("Categories")
    for key, value in sorted(Counter(r["category"] for r in metadata).items()):
        print(f"  {key:34s} {value:3d}")
    print()

    print(f"Near-duplicate question pairs (ratio >= {NEAR_DUPLICATE_THRESHOLD:.2f}): {len(near_duplicates)}")
    for ratio, a, b in near_duplicates[:25]:
        print(f"  {ratio:.3f}  {a} <-> {b}")
    if len(near_duplicates) > 25:
        print(f"  ... plus {len(near_duplicates) - 25} more")
    print()

    if warnings:
        print(f"WARNINGS: {len(warnings)}")
        for warning in warnings[:25]:
            print(f"  - {warning}")
        if len(warnings) > 25:
            print(f"  ... plus {len(warnings) - 25} more")
        print()

    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("PASS: final dataset is technically consistent.")
    if near_duplicates:
        print("NOTE: near-duplicate pairs are warnings for manual review, not technical failures.")


if __name__ == "__main__":
    main()
