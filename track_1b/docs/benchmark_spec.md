# Benchmark specification

## Purpose

This benchmark evaluates how accurately Apertus represents key concepts, structures,
qualifications, institutional responsibilities, regulatory boundaries, and selected
current rules in Swiss Professional Education (höhere Berufsbildung).

The benchmark is closed-book. The target model receives only the single-turn question.
It does not receive the fact bank, reference answer, scope note, or source material.

Reference date: 2026-10-01  
Benchmark language: German (Swiss Standard German)  
Target model: Apertus v1.5 8B

## Source of truth

`track_1b/data/fact_bank.jsonl` is the curated source of truth.

Version 1 contains 100 verified facts. Each fact contains exactly three curated
`question_modes`. The benchmark therefore uses one item for every
fact × question-mode combination:

- 100 facts
- 3 distinct question intents per fact
- 300 benchmark items

This is intentionally not three paraphrases of the same question. Each item must
instantiate the cognitive intent of its assigned `question_type` and must be materially
distinct from the other items derived from the same fact.

No benchmark item may introduce factual claims that are not supported by its assigned
fact, scope note, and cited sources.

## Stable identifiers

Benchmark cases use sequential stable identifiers:

`PE-001` … `PE-300`

Each case is linked to exactly one `fact_id`. The `fact_id` must also be written to
`metadata.jsonl` to preserve provenance from benchmark item to fact bank.

## Category distribution

The category distribution follows the verified fact bank. Each fact contributes three
items.

| Category | Facts | Items |
| --- | ---: | ---: |
| system_structure | 3 | 9 |
| qualifications_titles | 7 | 21 |
| access_pathways_progression | 10 | 30 |
| recognition_quality_regulation | 29 | 87 |
| institutions_responsibilities | 7 | 21 |
| reforms_2026_edge_cases | 21 | 63 |
| funding_financing | 23 | 69 |
| **Total** | **100** | **300** |

The benchmark does not force equal category sizes because doing so would require
arbitrary over-sampling of a small number of facts. To prevent large categories from
dominating interpretation, results should be reported both as overall item-level
accuracy and as a macro-average across categories.

## Question-type distribution

Every declared `question_mode` in the fact bank is used exactly once for its fact.
Current totals are:

| Question type | Items |
| --- | ---: |
| direct_fact | 86 |
| misconception | 57 |
| application | 51 |
| edge_case | 21 |
| classification | 15 |
| comparison | 13 |
| boundary | 12 |
| responsibility | 12 |
| relationship | 7 |
| calculation | 7 |
| date_rule | 5 |
| document_lookup | 5 |
| reverse_lookup | 4 |
| format_rule | 2 |
| exclusion | 1 |
| progression | 1 |
| resource_lookup | 1 |
| **Total** | **300** |

## Difficulty assignment

Difficulty is assigned deterministically from `question_type`.

### Basic

- `direct_fact`
- `reverse_lookup`
- `resource_lookup`
- `format_rule`

Expected total: 93 items.

### Intermediate

- `classification`
- `relationship`
- `responsibility`
- `comparison`
- `document_lookup`
- `progression`
- `calculation`
- `date_rule`
- `application`

Expected total: 116 items.

### Advanced

- `misconception`
- `boundary`
- `edge_case`
- `exclusion`

Expected total: 91 items.

Difficulty describes the intended reasoning burden of the question, not the intrinsic
importance of the underlying fact.

## Item-generation rules

Each item must satisfy all of the following:

1. Test exactly one primary fact from the fact bank.
2. Preserve all material qualifiers in the proposition and scope note, including terms
   such as `grundsätzlich`, `in der Regel`, dates, thresholds, exceptions, and
   jurisdictional boundaries.
3. Implement the assigned `question_type`; items derived from the same fact must differ
   in reasoning intent, not merely wording.
4. Remain answerable as a self-contained single-turn question.
5. Avoid requiring knowledge not contained in the assigned fact and its scope note.
6. Avoid ambiguous pronouns, underspecified dates, and unspecified institutions.
7. Use Swiss Standard German.
8. Do not show source URLs, the reference answer, or the scope note to the target model.
9. Keep the canonical reference answer concise enough for SimpleQA-style grading.
10. Provide at least two semantically valid `answer_variations` that preserve all
    essential qualifications of the canonical answer.
11. Copy all authoritative source URLs from the assigned fact into `source_citations`.
12. Do not use an answer variation to broaden or weaken the ground truth.

## Question-type interpretation

`direct_fact` asks directly for the verified proposition.  
`misconception` presents or tests a plausible false assumption.  
`application` places the rule in a concrete but source-supported scenario.  
`edge_case` tests an exception, transition, or unusual boundary condition.  
`classification` asks which category, credential, or regulatory class applies.  
`comparison` distinguishes two explicitly supported alternatives.  
`boundary` tests where a rule ceases to apply.  
`responsibility` asks which institution or actor is responsible.  
`relationship` asks how two supported concepts or actors relate.  
`calculation` requires only arithmetic directly supported by stated benchmark facts.  
`date_rule` tests a deadline, reference date, or transition date.  
`document_lookup` asks which official instrument or document contains a rule.  
`reverse_lookup` starts from an answer/credential and asks for the corresponding source concept.  
`format_rule` tests an explicitly supported title or naming format.  
`exclusion` asks what is explicitly not included.  
`progression` tests a supported progression relationship.  
`resource_lookup` asks where an official resource is found.

## Dataset linkage

`evaluation.jsonl` contains the user-facing benchmark material:

- `case_id`
- `question`
- `reference_answer`
- `answer_variations`
- `source_citations`

`metadata.jsonl` contains provenance and analysis fields. In addition to the fields
already defined in `dataset_schema.md`, it must contain:

- `fact_id`

`fact_id` links the benchmark case back to the exact verified source-of-truth record.

## Quality gates before model evaluation

The generated benchmark must pass automated validation:

- exactly 300 evaluation records
- exactly 300 metadata records
- case IDs unique and aligned between both files
- every `fact_id` exists in the fact bank
- every fact is represented exactly three times
- every declared fact/question-mode pair is represented exactly once
- no empty question or reference answer
- at least two answer variations per item
- at least one source citation per item
- all source citations originate from the assigned fact
- valid category, question type, difficulty, and reference date
- exact duplicate questions prohibited
- near-duplicate questions flagged for human review

A human content review should then focus on all flagged near-duplicates and on a
stratified sample spanning categories, question types, and difficulty levels.

## Evaluation reporting

At minimum, report:

- overall item-level accuracy
- `correct`, `incorrect`, and `not_attempted` rates
- accuracy by category
- macro-average accuracy across categories
- accuracy by question type
- accuracy by difficulty
- judge–human agreement on the required 20% human-validation sample
- uncertainty/error estimate and 95% confidence interval for the human-validation result

The human-validation sample must contain 60 of the 300 cases and be drawn reproducibly
with a fixed random seed.
