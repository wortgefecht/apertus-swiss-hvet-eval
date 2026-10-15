# Apertus Swiss HVET Eval

**Evaluating Apertus on Swiss Professional Education**

Version: **1.0.0**  
Status: **Evaluation complete / submission preparation**  
Hackathon: **Hack Apertus 2026 — Track 1B: Swiss Voices / Core Task Intelligence**

## Overview

Apertus Swiss HVET Eval is a domain-specific benchmark for evaluating factual reliability in **Swiss Professional Education** (Higher Vocational Education and Training, HVET).

The project asks:

> **How accurately does Apertus represent key concepts, structures, qualifications, institutional relationships, and selected quantitative facts in Swiss Professional Education?**

The benchmark targets Swiss-specific terminology, institutional structures, qualification pathways, regulatory responsibilities, financing rules, and selected 2026 reforms that may be difficult for a general-purpose language model.

## Final benchmark

The frozen benchmark contains **300 single-turn Q&A cases** in Swiss Standard German.

It was built from **100 verified atomic facts**, each represented by three deliberately varied questions. Every case includes a canonical reference answer, accepted answer variations, authoritative source citations, and structured provenance and classification metadata.

The benchmark reference date is **1 October 2026**.

The seven final content categories are:

- system structure,
- qualifications and titles,
- access, pathways, and progression,
- institutional responsibilities,
- recognition, quality, and regulation,
- funding and financing,
- 2026 reforms and edge cases.

## Apertus evaluation

The final evaluation uses:

- **Model:** `swiss-ai/Apertus-v1.5-8B`
- **Revision:** `ef4bbc54d6fe658bc782280ff9f3b53a10a9758f`
- **Backend:** vLLM
- **Runtime:** Hugging Face Jobs
- **Hardware:** A100 large
- **Temperature:** 0
- **Seed:** 0
- **Maximum completion tokens:** 1024
- **Prompting:** single user message, no system prompt, closed-book

All **300 cases** completed without final length truncation.

## Grading

The primary automated grading uses a SimpleQA-style three-way label set:

- `correct`
- `incorrect`
- `not_attempted`

The final judge is **Qwen/Qwen3-235B-A22B-Instruct-2507**, served by DeepInfra through Hugging Face Inference Providers.

A fixed 12-case sample was used to calibrate and freeze the judge configuration. Human validation was then performed blind on a fixed-seed random sample of **60 cases drawn from the remaining 288 non-calibration cases**.

## Key results

Automated judge results across all 300 cases:

- **43.3% correct** (130/300)
- **55.0% incorrect** (165/300)
- **1.7% not attempted** (5/300)
- **95% Wilson CI for correct:** 37.8%–49.0%

Human validation of 60 cases:

- **31.7% correct** (19/60)
- **65.0% incorrect** (39/60)
- **3.3% not attempted** (2/60)

Judge–human reliability:

- **75.0% exact agreement** (45/60)
- **95% Wilson CI:** 62.8%–84.2%
- **Cohen's κ:** 0.515

The judge is asymmetric in its disagreements with the human evaluator: it is more likely to accept partially correct answers containing materially false domain claims than to reject answers the human evaluator considers correct.

## Main findings

The weakest category-level performance is observed for:

- **qualifications and titles:** 23.8%
- **institutional responsibilities:** 33.3%

Performance is higher for:

- **funding and financing:** 50.7%
- **2026 reforms and edge cases:** 50.8%
- **system structure:** 55.6%

A notable question-type effect appears in the frozen benchmark:

- **direct factual questions:** 19.8%
- **responsibility questions:** 8.3%
- **misconception questions:** 75.4%

This pattern suggests that Apertus often recognises a false premise or broad conceptual distinction while struggling with precise Swiss terminology, formal institutional allocation, and exact factual recall.

The authoring field `difficulty` should not be interpreted as a psychometric difficulty scale. Its counter-intuitive result — advanced items scoring above basic items — is largely explained by the distribution of question types across those authoring labels.

## Repository structure

Key submission artefacts are located under `track_1b/`:

- `data/evaluation.jsonl` — 300 evaluation cases
- `data/metadata.jsonl` — instance-level provenance and classifications
- `data/model_responses.jsonl` — Apertus responses plus judge and human-validation fields
- `data/run_metadata.json` — frozen Apertus inference configuration
- `data/judge_run_metadata.json` — final judge configuration
- `data/human_validation_sample.jsonl` — blinded 60-case validation sample
- `data/human_validation_results.jsonl` — human labels
- `data/benchmark_summary.json` — aggregate statistics
- `data/benchmark_breakdown.csv` — category/type/difficulty breakdowns
- `data/judge_human_disagreements.jsonl` — qualitative disagreement set
- `docs/methodology.md` — full evaluation methodology
- `docs/sources.md` — source documentation
- `docs/licensing.md` — licensing and provenance policy
- `src/` — dataset construction, inference, judging, validation, and analysis scripts

## Track 1B alignment

The project satisfies the core dataset/evaluation requirements through:

- 300 single-turn Q&A cases,
- reference answer variations,
- authoritative source citations,
- SimpleQA-style three-way grading,
- LLM-as-a-judge evaluation,
- 60-case blinded human validation,
- reported judge–human agreement,
- instance-level provenance and licensing metadata,
- reproducible construction and analysis scripts.

The public Hugging Face dataset has been published, and the root `make run` workflow now reproduces and verifies the frozen evaluation deterministically in Docker. The remaining core submission task is the final technical report and submission QA.

## Scope and limitations

The benchmark is intentionally narrow. It does not evaluate general reasoning, broad multilingual ability, overall safety, or the entire Swiss education system.

It uses one Apertus model size, one response per question, and one expert human validator. Results are therefore best understood as a focused test of **Swiss domain factuality**, particularly where precise terminology and institutional knowledge matter.

## Licensing

The licensing structure is documented in `docs/licensing.md`:

- source code: **Apache-2.0**
- documentation and non-code project material: **CC BY 4.0**
- benchmark and evaluation data: **CDLA-Permissive-2.0**
