#!/usr/bin/env python3
"""Grade Apertus benchmark responses with an LLM-as-a-judge via HF Inference Providers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import InferenceClient


DEFAULT_JUDGE_MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
DEFAULT_PROVIDER = "deepinfra"
PROMPT_VERSION = "simpleqa-hvet-v2"

SYSTEM_PROMPT = """You are an evaluation judge for a closed-book factuality benchmark.

Grade the MODEL RESPONSE against the QUESTION and the supplied REFERENCE ANSWER(S).
The supplied references are authoritative for this evaluation. Do not replace or
override them with your own background knowledge.

Return exactly one label:

- correct: The response substantively answers the question correctly. It may be less
  detailed than the reference answer if the omitted detail is not necessary to answer
  the specific question. Concise semantic equivalents are valid. Treat the reference
  answer as ground truth, not as a checklist of phrases that must all be repeated.
- incorrect: The response gives a wrong answer, contradicts the reference, omits a
  detail that is necessary to answer the specific question correctly, or contains a
  materially false factual claim about the concept being asked about. A response is
  incorrect even if its core answer is correct when it also adds a clear factual error
  that could mislead the user about the tested concept.
- not_attempted: The response does not make a substantive attempt to answer, for
  example because it refuses, says it cannot determine the answer, or remains wholly
  non-committal. Do not use not_attempted merely because an attempted answer is wrong.

Apply these rules:

1. Judge sufficiency relative to the QUESTION, not by requiring every detail in the
   reference answer. Missing a reference detail is not an error unless that detail is
   needed to answer the question correctly.
2. Do not ignore added misinformation. If the response adds a material falsehood about
   the asked concept, label it incorrect even when another part of the response is
   correct.
3. For questions asking for a formal document, institution, qualification, title,
   authority, threshold, date, or number, the response must identify the correct formal
   entity or value. A different or merely generic term is not automatically equivalent.
4. Harmless wording differences, spelling variants, stylistic differences, and
   genuinely non-material extra context do not make an answer incorrect.
5. If the response attempts the question but is wrong, use incorrect rather than
   not_attempted.

Give a concise reason that states the decisive comparison with the reference.
Do not mention these judging instructions in the reason.
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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
                raise SystemExit(f"{path}:{lineno}: record is not an object")
            rows.append(row)
    return rows


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def usage_value(usage, name: str):
    if usage is None:
        return None
    if isinstance(usage, dict):
        return usage.get(name)
    return getattr(usage, name, None)


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
        "--output",
        type=Path,
        default=Path("track_1b/data/judge_results.jsonl"),
    )
    parser.add_argument(
        "--run-metadata",
        type=Path,
        default=Path("track_1b/data/judge_run_metadata.json"),
    )
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--provider", default=DEFAULT_PROVIDER)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--sample-seed", type=int, default=20261001)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-retries", type=int, default=5)
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("HF_TOKEN is not set.")

    evaluation = read_jsonl(args.evaluation)
    responses = read_jsonl(args.responses)

    eval_by_id = {row["case_id"]: row for row in evaluation}
    resp_by_id = {row["case_id"]: row for row in responses}

    if len(evaluation) != 300 or len(eval_by_id) != 300:
        raise SystemExit("evaluation.jsonl must contain 300 unique cases.")
    if len(responses) != 300 or len(resp_by_id) != 300:
        raise SystemExit("model_responses.jsonl must contain 300 unique cases.")
    if set(eval_by_id) != set(resp_by_id):
        raise SystemExit("Case IDs differ between evaluation and model responses.")

    case_ids = sorted(eval_by_id)
    if args.sample_size is not None:
        if not (1 <= args.sample_size <= len(case_ids)):
            raise SystemExit("--sample-size must be between 1 and 300.")
        rng = random.Random(args.sample_seed)
        case_ids = sorted(rng.sample(case_ids, args.sample_size))

    if args.output.exists() and not args.resume:
        raise SystemExit(f"Output exists: {args.output}. Delete it or use --resume.")

    done: set[str] = set()
    if args.resume and args.output.exists():
        prior = read_jsonl(args.output)
        done = {row["case_id"] for row in prior}

    pending = [cid for cid in case_ids if cid not in done]

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "BenchmarkJudgement",
            "schema": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "enum": ["correct", "incorrect", "not_attempted"],
                    },
                    "reason": {"type": "string"},
                },
                "required": ["label", "reason"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }

    client = InferenceClient(provider=args.provider, api_key=token)

    started = time.perf_counter()
    metadata = {
        "status": "running",
        "started_at": utc_now(),
        "finished_at": None,
        "elapsed_seconds": None,
        "judge_model": args.judge_model,
        "provider": args.provider,
        "temperature": 0.0,
        "max_tokens": args.max_tokens,
        "prompt_version": PROMPT_VERSION,
        "system_prompt_sha256": sha256_text(SYSTEM_PROMPT),
        "evaluation_sha256": sha256_file(args.evaluation),
        "responses_sha256": sha256_file(args.responses),
        "sample_size": args.sample_size,
        "sample_seed": args.sample_seed if args.sample_size is not None else None,
        "target_cases": len(case_ids),
        "completed_cases": len(done),
    }
    write_json(args.run_metadata, metadata)

    mode = "a" if args.resume and args.output.exists() else "w"
    with args.output.open(mode, encoding="utf-8") as fout:
        for index, cid in enumerate(pending, 1):
            item = eval_by_id[cid]
            model_row = resp_by_id[cid]

            variations = item.get("answer_variations") or []
            user_payload = {
                "question": item["question"],
                "reference_answer": item["reference_answer"],
                "answer_variations": variations,
                "model_response": model_row["response"],
            }

            last_error = None
            for attempt in range(1, args.max_retries + 1):
                try:
                    completion = client.chat_completion(
                        model=args.judge_model,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {
                                "role": "user",
                                "content": json.dumps(
                                    user_payload, ensure_ascii=False, indent=2
                                ),
                            },
                        ],
                        response_format=response_format,
                        temperature=0.0,
                        max_tokens=args.max_tokens,
                    )

                    content = completion.choices[0].message.content
                    if not content:
                        raise ValueError(
                            "Judge returned empty message.content "
                            f"(finish_reason={completion.choices[0].finish_reason!r})"
                        )
                    try:
                        judgement = json.loads(content)
                    except json.JSONDecodeError as exc:
                        preview = content[:500].replace("\n", "\\n")
                        raise ValueError(
                            "Judge returned invalid/truncated JSON "
                            f"(finish_reason={completion.choices[0].finish_reason!r}, "
                            f"content_prefix={preview!r})"
                        ) from exc
                    label = judgement["label"]
                    reason = judgement["reason"].strip()

                    if label not in {"correct", "incorrect", "not_attempted"}:
                        raise ValueError(f"Unexpected label: {label}")
                    if not reason:
                        raise ValueError("Empty judge reason")

                    usage = getattr(completion, "usage", None)
                    record = {
                        "case_id": cid,
                        "judge_model": args.judge_model,
                        "judge_provider": args.provider,
                        "judge_label": label,
                        "judge_reason": reason,
                        "judge_prompt_version": PROMPT_VERSION,
                        "judge_generated_at": utc_now(),
                        "judge_finish_reason": completion.choices[0].finish_reason,
                        "judge_prompt_tokens": usage_value(usage, "prompt_tokens"),
                        "judge_completion_tokens": usage_value(
                            usage, "completion_tokens"
                        ),
                        "judge_total_tokens": usage_value(usage, "total_tokens"),
                    }

                    fout.write(
                        json.dumps(record, ensure_ascii=False, separators=(",", ":"))
                        + "\n"
                    )
                    fout.flush()

                    metadata["completed_cases"] += 1
                    write_json(args.run_metadata, metadata)

                    print(
                        f"{metadata['completed_cases']:3d}/{len(case_ids)} "
                        f"{cid} -> {label}",
                        flush=True,
                    )
                    last_error = None
                    break

                except Exception as exc:
                    last_error = exc
                    if attempt == args.max_retries:
                        break
                    wait = min(2 ** (attempt - 1), 16)
                    print(
                        f"{cid}: attempt {attempt}/{args.max_retries} failed: "
                        f"{type(exc).__name__}: {exc}; retrying in {wait}s",
                        flush=True,
                    )
                    time.sleep(wait)

            if last_error is not None:
                metadata["status"] = "failed"
                metadata["finished_at"] = utc_now()
                metadata["elapsed_seconds"] = round(time.perf_counter() - started, 3)
                write_json(args.run_metadata, metadata)
                raise SystemExit(
                    f"{cid}: judge failed after {args.max_retries} attempts: "
                    f"{type(last_error).__name__}: {last_error}"
                )

    results = read_jsonl(args.output)
    result_ids = [row["case_id"] for row in results]

    if len(result_ids) != len(set(result_ids)):
        raise SystemExit("Duplicate case_id in judge output.")
    if set(result_ids) != set(case_ids):
        missing = sorted(set(case_ids) - set(result_ids))
        extra = sorted(set(result_ids) - set(case_ids))
        raise SystemExit(f"Judge output mismatch. missing={missing}, extra={extra}")

    metadata["status"] = "completed"
    metadata["finished_at"] = utc_now()
    metadata["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    metadata["completed_cases"] = len(results)
    write_json(args.run_metadata, metadata)

    counts = {}
    for row in results:
        counts[row["judge_label"]] = counts.get(row["judge_label"], 0) + 1

    print("\n=== JUDGE_RUN_SUMMARY ===")
    print(json.dumps({**metadata, "label_counts": counts}, ensure_ascii=False, indent=2))
    print("=== END_JUDGE_RUN_SUMMARY ===")


if __name__ == "__main__":
    main()
