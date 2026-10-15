#!/usr/bin/env python3
"""Run the 300-item closed-book Apertus benchmark on Hugging Face Jobs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import vllm
from huggingface_hub import HfApi
from vllm import LLM, SamplingParams


DEFAULT_MODEL = "swiss-ai/Apertus-v1.5-8B"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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
            rows.append(row)
    return rows


def existing_case_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {row["case_id"] for row in read_jsonl(path)}


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--run-metadata", required=True, type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--max-model-len", type=int, default=4096)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.6)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--hardware", default="a100-large")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    if args.batch_size < 1:
        raise SystemExit("--batch-size must be >= 1")

    started_wall = utc_now()
    started_perf = time.perf_counter()

    rows = read_jsonl(args.input)
    expected_ids = [f"PE-{i:03d}" for i in range(1, 301)]
    input_ids = [row.get("case_id") for row in rows]

    if input_ids != expected_ids:
        raise SystemExit("Input must contain exactly PE-001..PE-300 in order.")

    if args.limit is not None:
        rows = rows[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.run_metadata.parent.mkdir(parents=True, exist_ok=True)

    if args.output.exists() and not args.resume:
        raise SystemExit(
            f"Output already exists: {args.output}. "
            "Delete it or use --resume."
        )

    done = existing_case_ids(args.output) if args.resume else set()
    pending = [row for row in rows if row["case_id"] not in done]

    run_id = os.environ.get("JOB_ID") or f"local-{int(time.time())}"
    model_revision = HfApi().model_info(
        args.model, token=os.environ.get("HF_TOKEN")
    ).sha

    metadata = {
        "run_id": run_id,
        "status": "running",
        "started_at": started_wall,
        "finished_at": None,
        "elapsed_seconds": None,
        "model": args.model,
        "model_revision": model_revision,
        "inference_backend": "vllm",
        "vllm_version": vllm.__version__,
        "hardware_flavor": args.hardware,
        "accelerator_env": os.environ.get("ACCELERATOR"),
        "temperature": 0.0,
        "max_tokens": args.max_tokens,
        "seed": args.seed,
        "thinking": False,
        "max_model_len": args.max_model_len,
        "gpu_memory_utilization": args.gpu_memory_utilization,
        "batch_size": args.batch_size,
        "prompt_mode": "single user message; no system prompt; closed-book",
        "input_file": args.input.name,
        "input_sha256": sha256_file(args.input),
        "target_cases": len(rows),
        "already_present_on_resume": len(done),
        "completed_cases": len(done),
    }
    write_json(args.run_metadata, metadata)

    print(f"Run ID: {run_id}")
    print(f"Model: {args.model}")
    print(f"Revision: {model_revision}")
    print(f"Cases in run: {len(rows)}")
    print(f"Pending: {len(pending)}")

    llm = LLM(
        model=args.model,
        revision=model_revision,
        tokenizer_revision=model_revision,
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_model_len,
    )

    sampling = SamplingParams(
        temperature=0.0,
        max_tokens=args.max_tokens,
        seed=args.seed,
    )

    mode = "a" if args.resume and args.output.exists() else "w"
    with args.output.open(mode, encoding="utf-8") as fout:
        for offset in range(0, len(pending), args.batch_size):
            batch = pending[offset : offset + args.batch_size]
            conversations = [
                [{"role": "user", "content": row["question"]}]
                for row in batch
            ]

            batch_started = time.perf_counter()
            outputs = llm.chat(
                conversations,
                sampling_params=sampling,
                use_tqdm=False,
                chat_template_content_format="string",
                chat_template_kwargs={"enable_thinking": False},
            )
            batch_elapsed = time.perf_counter() - batch_started

            if len(outputs) != len(batch):
                raise RuntimeError(
                    f"Expected {len(batch)} outputs, got {len(outputs)}."
                )

            generated_at = utc_now()
            for row, request_output in zip(batch, outputs):
                candidate = request_output.outputs[0]
                record = {
                    "case_id": row["case_id"],
                    "model": args.model,
                    "response": candidate.text,
                    "temperature": 0.0,
                    "max_tokens": args.max_tokens,
                    "run_id": run_id,
                    "generated_at": generated_at,
                    "judge_model": None,
                    "judge_label": None,
                    "judge_reason": None,
                    "human_checked": False,
                    "human_label": None,
                    "model_revision": model_revision,
                    "seed": args.seed,
                    "thinking": False,
                    "finish_reason": getattr(candidate, "finish_reason", None),
                    "prompt_tokens": len(request_output.prompt_token_ids or []),
                    "completion_tokens": len(candidate.token_ids or []),
                }
                fout.write(
                    json.dumps(record, ensure_ascii=False, separators=(",", ":"))
                    + "\n"
                )
                fout.flush()

            metadata["completed_cases"] += len(batch)
            metadata["last_batch_seconds"] = round(batch_elapsed, 3)
            write_json(args.run_metadata, metadata)

            print(
                f"Completed {metadata['completed_cases']}/{len(rows)} "
                f"(batch {len(batch)} in {batch_elapsed:.2f}s)",
                flush=True,
            )

    # Validate final output for this run.
    final_rows = read_jsonl(args.output)
    final_ids = [row["case_id"] for row in final_rows]
    target_ids = [row["case_id"] for row in rows]

    if len(final_ids) != len(set(final_ids)):
        raise RuntimeError("Duplicate case_id detected in output.")
    if set(final_ids) != set(target_ids):
        missing = sorted(set(target_ids) - set(final_ids))
        extra = sorted(set(final_ids) - set(target_ids))
        raise RuntimeError(f"Output mismatch. missing={missing}, extra={extra}")

    metadata["status"] = "completed"
    metadata["finished_at"] = utc_now()
    metadata["elapsed_seconds"] = round(time.perf_counter() - started_perf, 3)
    metadata["completed_cases"] = len(final_rows)
    metadata.pop("last_batch_seconds", None)
    write_json(args.run_metadata, metadata)

    print("\n=== APERTUS_BATCH_SUMMARY ===")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    print("=== END_APERTUS_BATCH_SUMMARY ===")


if __name__ == "__main__":
    main()
