# Apertus Swiss HVET Eval

Domain-specific factuality evaluation of **Apertus v1.5 8B** on **Swiss Professional Education / Higher Vocational Education and Training (HVET)**.

This repository is the GitHub submission for **Hack Apertus 2026 — Track 1B: Swiss Voices / Core Task Intelligence**.

## Research question

> How accurately does Apertus represent key concepts, structures, qualifications, institutional relationships, and selected quantitative facts in Swiss Professional Education?

## Benchmark

The frozen benchmark contains **300 single-turn Q&A cases in Swiss Standard German**, constructed from **100 verified atomic facts** with three deliberately varied questions per fact.

Each case includes:

- a canonical reference answer,
- accepted answer variations,
- authoritative source citations,
- structured provenance and taxonomy metadata.

Reference date: **1 October 2026**.

## Model and evaluation

Final Apertus run:

- model: `swiss-ai/Apertus-v1.5-8B`
- immutable model revision: `ef4bbc54d6fe658bc782280ff9f3b53a10a9758f`
- backend: vLLM
- runtime: Hugging Face Jobs
- hardware: A100 large
- temperature: 0
- seed: 0
- max completion tokens: 1024
- prompt mode: single user message, no system prompt, closed-book

Automated grading used `Qwen/Qwen3-235B-A22B-Instruct-2507` with the SimpleQA-style labels `correct`, `incorrect`, and `not_attempted`.

A blinded human validation sample of **60 cases** was drawn from the 288 non-calibration cases.

## Headline results

- automated judge accuracy: **43.3%** (130/300)
- human-validation sample accuracy: **31.7%** (19/60)
- judge–human exact agreement: **75.0%** (45/60)
- Cohen's κ: **0.515**

The automated judge was somewhat lenient relative to the human evaluator, so the 43.3% automated score should be interpreted together with the human-validation results.

## Reproduce the submitted evaluation

From a clean checkout:

```bash
make run
```

This builds the Docker image and runs an offline deterministic reproduction workflow that:

1. validates benchmark construction,
2. validates the frozen Apertus responses and grading against recorded run metadata,
3. recomputes benchmark summaries,
4. verifies the headline metrics against the frozen submission results.

The default `make run` path requires **no API key and no GPU** because it reproduces the evaluation from the fixed model outputs included in the repository.

The original Apertus inference and external LLM-judge runs require the hosted runtimes and credentials documented in `track_1b/docs/methodology.md` and the run metadata files.

## Dataset

Public Hugging Face dataset:

https://huggingface.co/datasets/gisiger/apertus-swiss-hvet-eval

The published dataset contains the required evaluation, metadata, and model-response configurations plus supplementary validation and reproducibility artefacts.

## Repository structure

```text
track_1b/
├── data/                  # benchmark, model responses, grading, summaries
├── docs/                  # methodology, provenance, schema, licensing
├── src/                   # construction, inference, grading, validation, analysis
├── Dockerfile
├── Makefile
├── requirements.txt
└── technical_report.md
```

## Key documentation

- `track_1b/docs/methodology.md` — final evaluation methodology
- `track_1b/docs/dataset_schema.md` — dataset schema
- `track_1b/docs/sources.md` — source documentation
- `track_1b/docs/licensing.md` — licensing and provenance
- `track_1b/data/run_metadata.json` — final Apertus inference configuration
- `track_1b/data/judge_run_metadata.json` — final judge configuration
- `track_1b/data/benchmark_summary.json` — aggregate results

## Licensing

- source code: **Apache-2.0**
- documentation and other non-code material: **CC BY 4.0**
- benchmark and evaluation data: **CDLA-Permissive-2.0**

See `track_1b/docs/licensing.md` for details.
