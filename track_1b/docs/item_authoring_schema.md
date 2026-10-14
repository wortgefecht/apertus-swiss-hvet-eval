# Item authoring schema

`authored_items.jsonl` is the human-reviewable authoring layer between the deterministic
item plan and the final Hugging Face dataset.

It contains only the fields that require linguistic or editorial judgement. Provenance,
category, difficulty, licensing, and source metadata are derived deterministically from
`item_plan.jsonl` and `fact_bank.jsonl` by `src/build_dataset.py`.

Each JSONL record contains:

- `case_id`: must match a case in `item_plan.jsonl`
- `fact_id`: must match the fact assigned by the item plan
- `question_type`: must match the type assigned by the item plan
- `question`: self-contained German single-turn question
- `reference_answer`: concise ground-truth answer
- `answer_variations`: at least two alternative valid answers
- `misconception_target`: concise false assumption being tested, or `null` when not applicable

Authoring rules:

1. The question may test only the assigned fact and its `scope_note`.
2. Material qualifiers such as dates, thresholds, `grundsätzlich`, `in der Regel`, and
   exceptions must not be dropped.
3. Three items derived from the same fact must differ in reasoning intent, not merely wording.
4. The question must not reveal the answer.
5. The reference answer and all answer variations must remain within the verified source of truth.
6. `misconception_target` is normally populated only for `misconception` items. It may be
   used for another item only if a concrete misconception is explicitly part of that question.
7. Language is Swiss Standard German.

The final submission dataset is built from this file; this authoring file is an internal
reproducibility and review artefact.
