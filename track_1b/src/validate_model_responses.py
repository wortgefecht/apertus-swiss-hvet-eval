#!/usr/bin/env python3
"""Validate Apertus benchmark model responses against run metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

EXPECTED_CASE_IDS = [f"PE-{i:03d}" for i in range(1, 301)]
EXPECTED_MODEL = "swiss-ai/Apertus-v1.5-8B"
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
                raise SystemExit(f"{path}:{lineno}: record is not a JSON object")
            rows.append(obj)
    return rows


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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
        "--run-metadata",
        type=Path,
        default=Path("track_1b/data/run_metadata.json"),
    )
    parser.add_argument(
        "--graded",
        action="store_true",
        help="Validate final graded responses instead of pre-grading responses.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    for path in (args.evaluation, args.responses, args.run_metadata):
        if not path.exists():
            raise SystemExit(f"ERROR: missing file: {path}")

    evaluation = read_jsonl(args.evaluation)
    responses = read_jsonl(args.responses)
    run_meta = json.loads(args.run_metadata.read_text(encoding="utf-8"))

    run_id = run_meta.get("run_id")
    model = run_meta.get("model")
    model_revision = run_meta.get("model_revision")
    temperature = run_meta.get("temperature")
    max_tokens = run_meta.get("max_tokens")
    seed = run_meta.get("seed")
    thinking = run_meta.get("thinking")

    if len(evaluation) != 300:
        errors.append(f"evaluation.jsonl: expected 300 rows, found {len(evaluation)}")
    if len(responses) != 300:
        errors.append(f"model_responses.jsonl: expected 300 rows, found {len(responses)}")

    eval_ids = [r.get("case_id") for r in evaluation]
    resp_ids = [r.get("case_id") for r in responses]

    if eval_ids != EXPECTED_CASE_IDS:
        errors.append("evaluation.jsonl case IDs are not exactly PE-001..PE-300 in order")
    if resp_ids != EXPECTED_CASE_IDS:
        errors.append("model_responses.jsonl case IDs are not exactly PE-001..PE-300 in order")
    if len(resp_ids) != len(set(resp_ids)):
        errors.append("duplicate case_id in model_responses.jsonl")
    if set(resp_ids) != set(eval_ids):
        errors.append("case_id sets differ between evaluation.jsonl and model_responses.jsonl")

    if run_meta.get("status") != "completed":
        errors.append(f"run status is {run_meta.get('status')!r}, expected 'completed'")
    if run_meta.get("completed_cases") != 300:
        errors.append(f"completed_cases={run_meta.get('completed_cases')!r}, expected 300")
    if model != EXPECTED_MODEL:
        errors.append(f"run model={model!r}, expected {EXPECTED_MODEL!r}")

    current_sha = sha256_file(args.evaluation)
    if run_meta.get("input_sha256") != current_sha:
        errors.append("evaluation.jsonl SHA-256 differs from the file used for the benchmark run")

    finish_reasons = Counter()
    completion_tokens: list[int] = []
    prompt_tokens: list[int] = []
    char_lengths: list[int] = []
    empty_ids: list[str] = []
    truncated_ids: list[str] = []
    repeated_texts = Counter()
    judge_counts = Counter()
    human_counts = Counter()
    human_checked_count = 0

    for row in responses:
        cid = row.get("case_id", "?")

        expected_pairs = {
            "model": model,
            "model_revision": model_revision,
            "run_id": run_id,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed,
            "thinking": thinking,
        }
        for field, expected in expected_pairs.items():
            if row.get(field) != expected:
                errors.append(
                    f"{cid}: {field}={row.get(field)!r}, expected {expected!r}"
                )

        response = row.get("response")
        if not isinstance(response, str) or not response.strip():
            empty_ids.append(cid)
            continue

        repeated_texts[response.strip()] += 1
        char_lengths.append(len(response))

        finish = row.get("finish_reason")
        finish_reasons[finish] += 1

        c_tokens = row.get("completion_tokens")
        p_tokens = row.get("prompt_tokens")

        if not isinstance(c_tokens, int) or c_tokens < 0:
            errors.append(f"{cid}: invalid completion_tokens={c_tokens!r}")
        else:
            completion_tokens.append(c_tokens)
            if finish != "stop" or (
                isinstance(max_tokens, int) and c_tokens >= max_tokens
            ):
                truncated_ids.append(cid)

        if not isinstance(p_tokens, int) or p_tokens < 0:
            errors.append(f"{cid}: invalid prompt_tokens={p_tokens!r}")
        else:
            prompt_tokens.append(p_tokens)

        if args.graded:
            judge_label = row.get("judge_label")
            if judge_label not in LABELS:
                errors.append(f"{cid}: invalid judge_label={judge_label!r}")
            else:
                judge_counts[judge_label] += 1

            if not isinstance(row.get("judge_model"), str) or not row["judge_model"].strip():
                errors.append(f"{cid}: missing judge_model")
            if not isinstance(row.get("judge_reason"), str) or not row["judge_reason"].strip():
                errors.append(f"{cid}: missing judge_reason")

            checked = row.get("human_checked")
            if not isinstance(checked, bool):
                errors.append(f"{cid}: human_checked must be boolean")
            elif checked:
                human_checked_count += 1
                label = row.get("human_label")
                if label not in LABELS:
                    errors.append(f"{cid}: invalid human_label={label!r}")
                else:
                    human_counts[label] += 1
                if row.get("human_validation_seed") != 20261015:
                    errors.append(f"{cid}: unexpected human_validation_seed")
                if row.get("human_blinded_to_judge") is not True:
                    errors.append(f"{cid}: human_blinded_to_judge must be true")
            else:
                for field in (
                    "human_label",
                    "human_reason",
                    "human_validation_seed",
                    "human_blinded_to_judge",
                ):
                    if row.get(field) is not None:
                        errors.append(f"{cid}: {field} must be null when human_checked=false")
        else:
            for field in ("judge_model", "judge_label", "judge_reason", "human_label"):
                if row.get(field) is not None:
                    errors.append(f"{cid}: {field} should still be null before grading")
            if row.get("human_checked") is not False:
                errors.append(f"{cid}: human_checked should be false before grading")

    if empty_ids:
        errors.append(f"empty model responses: {', '.join(empty_ids)}")

    if truncated_ids:
        warnings.append(
            "potentially truncated/non-stop responses: " + ", ".join(truncated_ids)
        )

    if args.graded:
        if sum(judge_counts.values()) != 300:
            errors.append("graded response file does not contain 300 valid judge labels")
        if human_checked_count != 60:
            errors.append(f"expected 60 human-checked rows, found {human_checked_count}")

    repeated = sorted(
        ((count, text) for text, count in repeated_texts.items() if count > 1),
        reverse=True,
    )

    print("Apertus response validation")
    print("===========================")
    print(f"Mode:                     {'graded' if args.graded else 'pre-grading'}")
    print(f"Evaluation rows:          {len(evaluation)}")
    print(f"Response rows:            {len(responses)}")
    print(f"Unique case IDs:          {len(set(resp_ids))}")
    print(f"Model:                    {model}")
    print(f"Model revision:           {model_revision}")
    print(f"Run ID:                   {run_id}")
    print(f"Run elapsed seconds:      {run_meta.get('elapsed_seconds')}")
    print(f"max_tokens:               {max_tokens}")
    print(f"Input SHA-256 matches:    {run_meta.get('input_sha256') == current_sha}")
    print()

    print("Finish reasons")
    for key, value in finish_reasons.items():
        print(f"  {str(key):20s} {value:3d}")
    print()

    if args.graded:
        print("Judge labels")
        for label in ("correct", "incorrect", "not_attempted"):
            print(f"  {label:20s} {judge_counts[label]:3d}")
        print(f"Human checked:            {human_checked_count}")
        for label in ("correct", "incorrect", "not_attempted"):
            print(f"  human {label:14s} {human_counts[label]:3d}")
        print()

    if completion_tokens:
        print("Completion tokens")
        print(f"  min:                    {min(completion_tokens)}")
        print(f"  median:                 {statistics.median(completion_tokens):.1f}")
        print(f"  mean:                   {statistics.mean(completion_tokens):.2f}")
        print(f"  max:                    {max(completion_tokens)}")
        if isinstance(max_tokens, int):
            print(
                f"  at max_tokens (>={max_tokens}): "
                f"{sum(x >= max_tokens for x in completion_tokens)}"
            )
        print()

    if prompt_tokens:
        print("Prompt tokens")
        print(f"  min:                    {min(prompt_tokens)}")
        print(f"  median:                 {statistics.median(prompt_tokens):.1f}")
        print(f"  mean:                   {statistics.mean(prompt_tokens):.2f}")
        print(f"  max:                    {max(prompt_tokens)}")
        print()

    if char_lengths:
        print("Response length (characters)")
        print(f"  min:                    {min(char_lengths)}")
        print(f"  median:                 {statistics.median(char_lengths):.1f}")
        print(f"  mean:                   {statistics.mean(char_lengths):.2f}")
        print(f"  max:                    {max(char_lengths)}")
        print()

    print(f"Repeated identical response texts: {len(repeated)}")
    for count, text in repeated[:10]:
        preview = text.replace("\n", " ")[:120]
        print(f"  {count:3d}x  {preview}")
    print()

    if warnings:
        print(f"WARNINGS: {len(warnings)}")
        for warning in warnings:
            print(f"  - {warning}")
        print()

    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("PASS: model responses are technically consistent.")
    if truncated_ids:
        print("NOTE: review the listed non-stop/max-token responses before judging.")


if __name__ == "__main__":
    main()
