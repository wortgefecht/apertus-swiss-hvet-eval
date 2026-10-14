# Dataset schema

The submission dataset consists of three JSONL files.

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
- `source_type`
- `source_authority`
- `source_title`
- `source_url`
- `item_license`
- `source_rights_note`
- `retrieved_at`
- `curation_method`
- `language`

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

Valid grading labels are:

- `correct`
- `incorrect`
- `not_attempted`
