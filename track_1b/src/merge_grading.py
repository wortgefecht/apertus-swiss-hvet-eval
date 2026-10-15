#!/usr/bin/env python3
"""Merge judge and blinded human-validation labels into model_responses.jsonl."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


LABELS = {"correct", "incorrect", "not_attempted"}


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
            if not isinstance(obj, dict):
                raise SystemExit(f"{path}:{lineno}: record is not an object")
            rows.append(obj)
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    tmp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--responses",
        type=Path,
        default=Path("track_1b/data/model_responses.jsonl"),
    )
    parser.add_argument(
        "--judge-results",
        type=Path,
        default=Path("track_1b/job_output_judge/judge_results.jsonl"),
    )
    parser.add_argument(
        "--human-results",
        type=Path,
        default=Path("track_1b/data/human_validation_results.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("track_1b/data/model_responses.jsonl"),
    )
    parser.add_argument(
        "--backup",
        type=Path,
        default=Path("track_1b/data/model_responses_ungraded.jsonl"),
    )
    args = parser.parse_args()

    responses = read_jsonl(args.responses)
    judge = read_jsonl(args.judge_results)
    human = read_jsonl(args.human_results)

    if len(responses) != 300:
        raise SystemExit(f"Expected 300 model responses, got {len(responses)}")
    if len(judge) != 300:
        raise SystemExit(f"Expected 300 judge results, got {len(judge)}")
    if len(human) != 60:
        raise SystemExit(f"Expected 60 human-validation results, got {len(human)}")

    response_ids = [r["case_id"] for r in responses]
    if len(set(response_ids)) != 300:
        raise SystemExit("Duplicate case_id in model responses.")

    judge_by_id = {r["case_id"]: r for r in judge}
    human_by_id = {r["case_id"]: r for r in human}

    if set(judge_by_id) != set(response_ids):
        raise SystemExit("Judge result IDs do not exactly match model response IDs.")
    if not set(human_by_id).issubset(response_ids):
        raise SystemExit("Human-validation IDs are not a subset of model response IDs.")

    for r in judge:
        if r.get("judge_label") not in LABELS:
            raise SystemExit(f"Invalid judge label in {r['case_id']}: {r.get('judge_label')}")
    for r in human:
        if r.get("human_label") not in LABELS:
            raise SystemExit(f"Invalid human label in {r['case_id']}: {r.get('human_label')}")

    # Preserve the exact pre-grading responses once.
    if args.output.resolve() == args.responses.resolve() and not args.backup.exists():
        shutil.copy2(args.responses, args.backup)

    merged = []
    for row in responses:
        cid = row["case_id"]
        j = judge_by_id[cid]
        h = human_by_id.get(cid)

        out = dict(row)
        out["judge_model"] = j["judge_model"]
        out["judge_label"] = j["judge_label"]
        out["judge_reason"] = j["judge_reason"]
        out["judge_provider"] = j.get("judge_provider")
        out["judge_prompt_version"] = j.get("judge_prompt_version")
        out["judge_generated_at"] = j.get("judge_generated_at")
        out["judge_finish_reason"] = j.get("judge_finish_reason")
        out["judge_prompt_tokens"] = j.get("judge_prompt_tokens")
        out["judge_completion_tokens"] = j.get("judge_completion_tokens")
        out["judge_total_tokens"] = j.get("judge_total_tokens")

        if h is not None:
            out["human_checked"] = True
            out["human_label"] = h["human_label"]
            out["human_reason"] = h.get("human_reason")
            out["human_validation_seed"] = h.get("validation_seed")
            out["human_blinded_to_judge"] = h.get("blinded_to_judge")
        else:
            out["human_checked"] = False
            out["human_label"] = None
            out["human_reason"] = None
            out["human_validation_seed"] = None
            out["human_blinded_to_judge"] = None

        merged.append(out)

    write_jsonl(args.output, merged)

    judge_counts = {}
    human_counts = {}
    for row in merged:
        judge_counts[row["judge_label"]] = judge_counts.get(row["judge_label"], 0) + 1
        if row["human_checked"]:
            human_counts[row["human_label"]] = human_counts.get(row["human_label"], 0) + 1

    print(f"Wrote merged responses: {args.output}")
    print(f"Ungraded backup:         {args.backup}")
    print(f"Rows:                    {len(merged)}")
    print(f"Human checked:           {sum(r['human_checked'] for r in merged)}")
    print(f"Judge labels:            {judge_counts}")
    print(f"Human labels:            {human_counts}")


if __name__ == "__main__":
    main()
