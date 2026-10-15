#!/usr/bin/env python3
"""Prepare and conduct blinded human validation for the Apertus benchmark."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

LABEL_MAP = {
    "c": "correct",
    "i": "incorrect",
    "n": "not_attempted",
    "correct": "correct",
    "incorrect": "incorrect",
    "not_attempted": "not_attempted",
}


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise SystemExit(f"{path}:{lineno}: record is not a JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def prepare_sample(
    evaluation_path: Path,
    responses_path: Path,
    calibration_path: Path,
    sample_path: Path,
    seed: int,
    sample_size: int,
) -> list[dict]:
    evaluation = read_jsonl(evaluation_path)
    responses = read_jsonl(responses_path)
    calibration = read_jsonl(calibration_path)

    eval_by_id = {r["case_id"]: r for r in evaluation}
    resp_by_id = {r["case_id"]: r for r in responses}
    calibration_ids = {r["case_id"] for r in calibration}

    if len(eval_by_id) != 300 or len(resp_by_id) != 300:
        raise SystemExit("Expected 300 unique evaluation cases and 300 unique model responses.")
    if set(eval_by_id) != set(resp_by_id):
        raise SystemExit("Evaluation and response case IDs do not match.")

    eligible = sorted(set(eval_by_id) - calibration_ids)
    if len(eligible) != 300 - len(calibration_ids):
        raise SystemExit("Unexpected calibration exclusion count.")
    if sample_size > len(eligible):
        raise SystemExit("Sample size exceeds eligible hold-out cases.")

    rng = random.Random(seed)
    selected_ids = sorted(rng.sample(eligible, sample_size))

    sample = []
    for cid in selected_ids:
        item = eval_by_id[cid]
        resp = resp_by_id[cid]
        sample.append(
            {
                "case_id": cid,
                "question": item["question"],
                "reference_answer": item["reference_answer"],
                "answer_variations": item.get("answer_variations", []),
                "source_citations": item.get("source_citations", []),
                "model_response": resp["response"],
            }
        )

    write_jsonl(sample_path, sample)
    print(
        f"Prepared blinded hold-out sample: {sample_size} cases "
        f"from {len(eligible)} non-calibration cases; seed={seed}"
    )
    print(f"Sample written to: {sample_path}")
    return sample


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evaluation",
        type=Path,
        default=Path("track_1b/data/evaluation.jsonl"),
    )
    parser.add_argument(
        "--responses",
        type=Path,
        default=Path("track_1b/data/model_responses.jsonl"),
    )
    parser.add_argument(
        "--calibration",
        type=Path,
        default=Path("track_1b/job_output_judge/calibration_qwen_v2.jsonl"),
    )
    parser.add_argument(
        "--sample",
        type=Path,
        default=Path("track_1b/data/human_validation_sample.jsonl"),
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=Path("track_1b/data/human_validation_results.jsonl"),
    )
    parser.add_argument("--seed", type=int, default=20261015)
    parser.add_argument("--sample-size", type=int, default=60)
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Create the blinded sample but do not start interactive review.",
    )
    args = parser.parse_args()

    if args.sample.exists():
        sample = read_jsonl(args.sample)
        if len(sample) != args.sample_size:
            raise SystemExit(
                f"Existing sample has {len(sample)} rows, expected {args.sample_size}. "
                "Delete it before changing seed/sample size."
            )
    else:
        sample = prepare_sample(
            args.evaluation,
            args.responses,
            args.calibration,
            args.sample,
            args.seed,
            args.sample_size,
        )

    if args.prepare_only:
        return

    prior = read_jsonl(args.results) if args.results.exists() else []
    prior_by_id = {r["case_id"]: r for r in prior}

    print()
    print("Human validation")
    print("================")
    print("Judge labels are intentionally hidden.")
    print("Labels: c=correct, i=incorrect, n=not_attempted, q=quit")
    print("An optional note can be entered after each label.")
    print()

    for idx, item in enumerate(sample, 1):
        cid = item["case_id"]
        if cid in prior_by_id:
            continue

        print("=" * 88)
        print(f"{idx}/{len(sample)}  {cid}")
        print("-" * 88)
        print("QUESTION")
        print(item["question"])
        print()
        print("REFERENCE ANSWER")
        print(item["reference_answer"])
        print()

        variations = item.get("answer_variations", [])
        if variations:
            print("VALID ANSWER VARIATIONS")
            for variation in variations:
                print(f"- {variation}")
            print()

        print("MODEL RESPONSE")
        print(item["model_response"])
        print()

        while True:
            raw = input("Human label [c/i/n/q]: ").strip().lower()
            if raw == "q":
                print(f"Stopped. Progress saved in {args.results}")
                return
            if raw in LABEL_MAP:
                label = LABEL_MAP[raw]
                break
            print("Please enter c, i, n, or q.")

        note = input("Optional note [Enter to skip]: ").strip()

        record = {
            "case_id": cid,
            "human_label": label,
            "human_reason": note or None,
            "validation_seed": args.seed,
            "blinded_to_judge": True,
        }
        prior.append(record)
        prior_by_id[cid] = record
        write_jsonl(args.results, prior)
        print(f"Saved: {cid} -> {label}")
        print()

    counts = {}
    for row in prior:
        counts[row["human_label"]] = counts.get(row["human_label"], 0) + 1

    print("=" * 88)
    print(f"Completed {len(prior)}/{len(sample)} human validation cases.")
    print("Human label counts:")
    for label in ("correct", "incorrect", "not_attempted"):
        print(f"  {label:14s} {counts.get(label, 0):3d}")
    print(f"Results: {args.results}")


if __name__ == "__main__":
    main()
