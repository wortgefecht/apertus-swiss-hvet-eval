#!/usr/bin/env python3
"""Export judge-human disagreement cases for qualitative error analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


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
            rows.append(obj)
    return rows


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
        "--metadata",
        type=Path,
        default=Path("track_1b/data/metadata.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("track_1b/data/judge_human_disagreements.jsonl"),
    )
    args = parser.parse_args()

    evaluation = {r["case_id"]: r for r in read_jsonl(args.evaluation)}
    responses = {r["case_id"]: r for r in read_jsonl(args.responses)}
    metadata = {r["case_id"]: r for r in read_jsonl(args.metadata)}

    rows = []
    for cid, response in responses.items():
        if not response.get("human_checked"):
            continue
        human = response.get("human_label")
        judge = response.get("judge_label")
        if human == judge:
            continue

        item = evaluation[cid]
        meta = metadata[cid]
        rows.append({
            "case_id": cid,
            "question": item["question"],
            "reference_answer": item["reference_answer"],
            "answer_variations": item.get("answer_variations", []),
            "model_response": response["response"],
            "judge_label": judge,
            "judge_reason": response.get("judge_reason"),
            "human_label": human,
            "human_reason": response.get("human_reason"),
            "category": meta["category"],
            "question_type": meta["question_type"],
            "difficulty": meta["difficulty"],
        })

    rows.sort(key=lambda r: r["case_id"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"Wrote {len(rows)} disagreement cases to {args.output}")
    if len(rows) != 15:
        print(f"WARNING: expected 15 disagreements from the current validation run, found {len(rows)}")


if __name__ == "__main__":
    main()
