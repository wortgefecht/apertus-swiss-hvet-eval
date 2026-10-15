# Licensing

Copyright © 2026 Michael Gisiger

This repository uses separate open licences for code, documentation, and benchmark data.

## Documentation and other non-code material

Unless stated otherwise, documentation, written analysis, methodology, reports, and other non-code material in this repository are licensed under:

**Creative Commons Attribution 4.0 International (CC BY 4.0)**

SPDX identifier: `CC-BY-4.0`

This includes, among other files:

- `track_1b/README.md`
- `track_1b/technical_report.md`
- `track_1b/docs/methodology.md`
- `track_1b/docs/project_overview.md`
- `track_1b/docs/sources.md`
- `track_1b/docs/benchmark_spec.md`
- `track_1b/docs/dataset_schema.md`
- `track_1b/docs/CHANGELOG.md`

## Benchmark and evaluation data

Benchmark datasets, evaluation datasets, model-response records, annotations, result tables, and related structured project data are licensed under:

**Community Data License Agreement – Permissive 2.0 (CDLA-Permissive-2.0)**

SPDX identifier: `CDLA-Permissive-2.0`

This includes, in particular:

- `track_1b/data/fact_bank.jsonl`
- `track_1b/data/item_plan.jsonl`
- `track_1b/data/authored_items.jsonl`
- `track_1b/data/evaluation.jsonl`
- `track_1b/data/metadata.jsonl`
- `track_1b/data/model_responses.jsonl`
- `track_1b/data/human_validation_sample.jsonl`
- `track_1b/data/human_validation_results.jsonl`
- `track_1b/data/judge_calibration.jsonl`
- `track_1b/data/judge_human_disagreements.jsonl`
- `track_1b/data/benchmark_summary.json`
- `track_1b/data/benchmark_breakdown.csv`

Instance-level dataset records also carry the applicable dataset licence in metadata.

## Source code

Source code in this repository is licensed under:

**Apache License 2.0**

SPDX identifier: `Apache-2.0`

The repository root `LICENSE` file contains the Apache-2.0 licence text.

## Third-party and official source material

External sources referenced by the project are **not** relicensed by this repository.

Official publications, legislation, webpages, model documentation, third-party datasets, Open Government Data resources, and other referenced materials remain subject to their respective copyright, licensing, and usage conditions.

The benchmark therefore uses original questions, original reference-answer formulations, original classifications, and original annotations rather than reproducing unnecessary source text.

Instance-level provenance records identify relevant source information, including source authority, source title, source URL, retrieval date, source type, and applicable rights note.

## Model responses

Apertus responses in `model_responses.jsonl` were generated during the benchmark evaluation. Their inclusion in the published evaluation dataset follows the applicable Hack Apertus and Apertus terms.

No third-party material that may incidentally appear inside a generated model response is intentionally relicensed by this notice.

## Hack Apertus alignment

The licensing structure is designed to align with the Hack Apertus 2026 submission requirements:

- source code: **Apache-2.0**
- documentation and other non-code materials: **CC BY 4.0**
- datasets: **CDLA-Permissive-2.0**

The public Hugging Face dataset uses **CDLA-Permissive-2.0** and retains instance-level provenance and source-rights metadata.
