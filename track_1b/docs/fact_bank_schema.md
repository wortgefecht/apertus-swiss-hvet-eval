# Fact bank schema

The fact bank is the curated source of truth used to construct the evaluation dataset.
It is not itself the submitted evaluation dataset.

Each JSONL record contains:

- `fact_id`: stable unique identifier
- `category`: top-level domain category
- `subcategory`: more specific topic
- `proposition_de`: verified factual proposition in German
- `canonical_answer_de`: concise answer expressing the verified fact
- `scope_note`: boundaries or qualifications that must not be lost
- `reference_date`: temporal reference for the fact
- `sources`: list of authoritative supporting sources
  - `authority`
  - `title`
  - `url`
  - `retrieved_at`
  - `source_type`
  - `locator`
- `verification_status`: `verified` or `pending`
- `question_modes`: intended ways in which the fact may be tested

The fact bank contains paraphrased factual propositions, not copied source text.
