# Dataset schema

The submission dataset consists of three JSONL files. An additional
`run_metadata.json` file records the configuration of the model inference run.

## evaluation.jsonl

One record per benchmark case:

- `case_id`: stable unique identifier
- `question`: German single-turn question
- `reference_answer`: canonical ground-truth answer
- `answer_variations`: alternative valid reference answers
- `source_citations`: authoritative source URLs

## metadata.jsonl

One record per benchmark case:

- `case_id`
- `fact_id`
- `category`
- `subcategory`
- `difficulty`
- `question_type`
- `misconception_target`
- `reference_date`
- `source_type`: list, aligned by position with the other source fields
- `source_authority`: list
- `source_title`: list
- `source_url`: list
- `item_license`
- `source_rights_note`
- `retrieved_at`: list
- `curation_method`
- `language`

Multiple sources may support one benchmark item. The source-related arrays
therefore use matching positions across fields.

## model_responses.jsonl

One record per evaluated model response:

- `case_id`
- `model`
- `response`
- `temperature`
- `max_tokens`
- `run_id`
- `generated_at`
- `judge_model`
- `judge_label`
- `judge_reason`
- `human_checked`
- `human_label`
- `model_revision`
- `seed`
- `thinking`
- `finish_reason`
- `prompt_tokens`
- `completion_tokens`

Before grading, the judge fields are `null` and `human_checked` is `false`.
They are populated by the grading and human-validation stages.

Valid grading labels are:

- `correct`
- `incorrect`
- `not_attempted`

## run_metadata.json

Records the inference configuration for the complete benchmark run, including:

- run identifier and timestamps
- model identifier and immutable model revision
- inference backend and version
- hardware flavor
- generation parameters
- prompt mode
- SHA-256 hash of the evaluation dataset
- target and completed case counts

This file provides provenance for the submitted model responses and allows the
exact benchmark run to be identified independently of later grading.
