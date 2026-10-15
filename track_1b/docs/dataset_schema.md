# Dataset schema

The submission dataset consists of three primary JSONL files:
`evaluation.jsonl`, `metadata.jsonl`, and `model_responses.jsonl`.

Additional JSON/JSONL/CSV files record inference provenance, judge calibration,
human validation, and aggregate analysis.

## evaluation.jsonl

One record per benchmark case:

- `case_id`: stable unique identifier
- `question`: German single-turn question
- `reference_answer`: canonical ground-truth answer
- `answer_variations`: list of alternative valid reference answers
- `source_citations`: list of authoritative source URLs

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

Multiple sources may support one benchmark item. Source-related arrays use
matching positions across fields.

## model_responses.jsonl

One record per evaluated model response.

### Inference fields

- `case_id`
- `model`
- `response`
- `temperature`
- `max_tokens`
- `run_id`
- `generated_at`
- `model_revision`
- `seed`
- `thinking`
- `finish_reason`
- `prompt_tokens`
- `completion_tokens`

### LLM-as-a-judge fields

- `judge_model`
- `judge_label`
- `judge_reason`
- `judge_provider`
- `judge_prompt_version`
- `judge_generated_at`
- `judge_finish_reason`
- `judge_prompt_tokens`
- `judge_completion_tokens`
- `judge_total_tokens`

### Human-validation fields

- `human_checked`
- `human_label`
- `human_reason`
- `human_validation_seed`
- `human_blinded_to_judge`

Valid grading labels are:

- `correct`
- `incorrect`
- `not_attempted`

For the 60-case blinded human-validation sample, `human_checked` is `true`.
For all other cases it is `false`, with the human-validation fields set to
`null`.

## run_metadata.json

Records the final Apertus inference configuration for the complete benchmark
run, including:

- run identifier and timestamps
- model identifier and immutable model revision
- inference backend and version
- hardware flavor
- generation parameters
- prompt mode
- SHA-256 hash of the evaluation dataset
- target and completed case counts

## judge_run_metadata.json

Records the final LLM-as-a-judge configuration, including:

- judge model and provider
- generation parameters
- judge prompt version and SHA-256 hash
- SHA-256 hashes of evaluation and response inputs
- target and completed case counts

## judge_calibration.jsonl and judge_calibration_metadata.json

Records the final fixed 12-case calibration sample used before freezing the
judge configuration. Calibration cases are excluded from the subsequent
60-case blinded human-validation hold-out sample.

## human_validation_sample.jsonl

Fixed-seed random sample of 60 benchmark cases drawn from the 288
non-calibration cases. It contains the question, reference answer, accepted
answer variations, source citations, and Apertus response, but no judge label.

## human_validation_results.jsonl

Human labels for the 60-case validation sample. The reviewer was blinded to
the LLM judge labels while rating.

## benchmark_summary.json and benchmark_breakdown.csv

Aggregate benchmark results by category, question type, and difficulty. These
files are derived from the graded `model_responses.jsonl` and `metadata.jsonl`.
