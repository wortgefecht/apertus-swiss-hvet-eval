# Methodology

Version: **1.0.0**  
Status: **Evaluation complete / submission preparation**  
Project: **Apertus Swiss HVET Eval**

## 1. Purpose and research question

This project evaluates the factual reliability of Apertus in a deliberately narrow Swiss domain: **Swiss Professional Education**, also referred to internationally as Higher Vocational Education and Training (HVET).

The core research question is:

> **How accurately does Apertus represent key concepts, structures, qualifications, institutional relationships, and selected quantitative facts in Swiss Professional Education?**

The benchmark targets **Hack Apertus 2026 Track 1B — Swiss Voices / Core Task Intelligence**. It is a domain-specific evaluation, not a general benchmark of Apertus capabilities.

## 2. Benchmark design

The final benchmark contains **300 single-turn German Q&A cases** in Swiss Standard German. It was constructed from **100 verified atomic facts**, with three deliberately varied questions authored for each fact.

Each evaluation item contains a stable case identifier, a single-turn question, a canonical reference answer, accepted answer variations, and authoritative source citations. A separate metadata record provides category, subcategory, question type, difficulty label, source provenance, reference date, and item-level licensing information.

The final dataset was frozen before model evaluation.

## 3. Reference standard and scope

The benchmark reference date is **1 October 2026**.

Reference answers are grounded primarily in authoritative Swiss sources, using the following hierarchy where applicable:

1. federal legislation and regulation,
2. current SERI / SBFI information,
3. SERI / SBFI registers, implementation guidance, and FAQs,
4. official Federal Statistical Office and other federal data,
5. official Swiss vocational education resources,
6. other authoritative institutional sources where necessary.

The benchmark covers system structure, qualifications and titles, access/pathways/progression, institutional responsibilities, recognition/quality/regulation, funding and financing, and 2026 reforms and edge cases.

The dataset includes direct factual questions, application questions, misconception prompts, responsibility questions, boundaries, comparisons, calculations, date rules, document lookups, and other targeted forms.

The metadata field `difficulty` is an authoring taxonomy rather than a psychometrically validated difficulty scale. It must therefore not be interpreted as an independent empirical measure of item difficulty.

## 4. Prompting and closed-book conditions

Each case is evaluated independently in a single-turn setting.

Apertus receives only the benchmark question. It does **not** receive the reference answer, answer variations, source citations, evaluator notes, outputs from other benchmark cases, retrieval-augmented context, web-search results, or corrective follow-up prompts.

The final run uses one user message and no system prompt. Raw model responses are preserved unchanged.

## 5. Apertus inference

The final benchmark run uses:

- **Model:** `swiss-ai/Apertus-v1.5-8B`
- **Model revision:** `ef4bbc54d6fe658bc782280ff9f3b53a10a9758f`
- **Backend:** vLLM
- **vLLM version:** `0.23.1rc1.dev1029+ga601a9d99`
- **Execution environment:** Hugging Face Jobs
- **Hardware:** A100 large
- **Temperature:** 0.0
- **Maximum completion tokens:** 1024
- **Seed:** 0
- **Thinking mode:** false
- **Maximum model length:** 4096
- **Batch size:** 50
- **Prompt mode:** single user message; no system prompt; closed-book

The final run identifier is `6ad08758c66288145224df76`. All **300/300** cases completed with `finish_reason=stop`; no final responses were length-truncated.

Full run provenance is stored in `data/run_metadata.json`.

## 6. LLM-as-a-judge evaluation

The primary automated evaluation uses the Track 1B SimpleQA-style label set:

- `correct`
- `incorrect`
- `not_attempted`

The final judge configuration is:

- **Judge:** `Qwen/Qwen3-235B-A22B-Instruct-2507`
- **Provider:** DeepInfra via Hugging Face Inference Providers
- **Temperature:** 0.0
- **Maximum completion tokens:** 1024
- **Prompt version:** `simpleqa-hvet-v2`

The judge is instructed to treat the reference answer as authoritative, accept substantively equivalent answers, and mark materially false claims about the tested concept as incorrect even when the core answer is partly correct.

Before the full judge run, the final prompt/model configuration was checked on a fixed **12-case calibration sample** selected with seed **20261001**. Calibration was used to finalise the rubric and judge configuration; the judge was then frozen before the full 300-case grading run.

Calibration artefacts and final judge metadata are stored in `data/judge_calibration.jsonl`, `data/judge_calibration_metadata.json`, and `data/judge_run_metadata.json`.

## 7. Blinded human validation

To keep judge calibration and validation separate, the 12 calibration cases were excluded from the human-validation sampling pool.

A fixed-seed random sample of **60 cases** was then drawn from the remaining **288 non-calibration cases** using seed **20261015**. This corresponds to 20% of the full 300-case benchmark while preserving a hold-out relationship between judge calibration and human validation.

The human evaluator was blinded to the judge label while rating each sampled response. The same three labels were used: `correct`, `incorrect`, and `not_attempted`.

The human-validation files are `data/human_validation_sample.jsonl` and `data/human_validation_results.jsonl`. The sample file contains no judge labels.

## 8. Agreement and scoring

The final automated judge labels are:

- **130 correct** (43.3%)
- **165 incorrect** (55.0%)
- **5 not attempted** (1.7%)

The Wilson 95% confidence interval for the judge-labelled correct rate is **37.8%–49.0%**.

Within the 60-case human-validation sample:

- **19 correct** (31.7%)
- **39 incorrect** (65.0%)
- **2 not attempted** (3.3%)

Judge–human agreement is:

- **45/60 exact matches**
- **75.0% agreement**
- **95% Wilson CI: 62.8%–84.2%**
- **Cohen's κ = 0.515**

The disagreement pattern is asymmetric: the judge labels 11 human-rated incorrect cases as correct, while it labels 4 human-rated correct cases as incorrect. The automated 43.3% score should therefore be interpreted together with the human validation rather than as a perfectly calibrated estimate of true domain accuracy.

## 9. Result breakdowns

Aggregate result files are generated from the frozen response and metadata files:

- `data/benchmark_summary.json`
- `data/benchmark_breakdown.csv`

Among the larger question types, Apertus performs substantially better on misconception prompts than on direct factual recall. Category-level performance is weakest for qualifications/titles and institutional responsibilities.

The apparent pattern **advanced > intermediate > basic** reflects the benchmark authoring taxonomy: many `advanced` items are misconception or boundary questions, while many `basic` items are direct-fact questions. It must not be interpreted as evidence that intrinsically harder questions are easier for the model.

## 10. Qualitative error analysis

The project preserves all **15 judge–human disagreements** in `data/judge_human_disagreements.jsonl`.

Recurring issues include confusion between qualification types and titles, incorrect institutional responsibilities, correct core answers accompanied by materially false explanations, overgeneralisation from non-Swiss education systems, imprecise use of formal terminology, and missing or incorrect thresholds, dates, and procedural details.

These cases are used for qualitative analysis; they do not trigger retrospective changes to benchmark questions or reference answers.

## 11. Reproducibility

The frozen artefacts include benchmark cases and metadata, exact Apertus responses, model revision and inference parameters, final judge outputs and judge metadata, calibration sample and seed, blinded human sample and seed, scoring and analysis scripts, and aggregate result files.

`make run` from the repository root builds a Docker image and executes a deterministic offline reproduction workflow. It validates benchmark construction, validates the frozen graded Apertus responses against the recorded run metadata, recomputes the aggregate benchmark statistics, and verifies the reproduced headline metrics against the frozen submission results. No API keys are required for this default reproduction path. GPU inference and the external LLM judge are documented separately because they require hosted runtimes and credentials.

## 12. Limitations

The evaluation has deliberate limitations:

- one narrow Swiss domain,
- German-language core benchmark,
- one Apertus model size,
- one response per case,
- one expert human validator,
- judge-model bias,
- no human inter-rater reliability estimate,
- authoring difficulty labels are not psychometric difficulty estimates,
- the reference standard is time-sensitive and fixed to 1 October 2026.

Results should therefore be interpreted as a targeted assessment of factual reliability in Swiss Professional Education, not as a general measure of Apertus quality.

## 13. Licensing

Repository code is licensed under **Apache-2.0**. Documentation and other non-code project material are licensed under **CC BY 4.0**. Benchmark and evaluation data are licensed under **CDLA-Permissive-2.0**.

Detailed provenance and licensing notes are documented in `docs/licensing.md` and in instance-level dataset metadata.
