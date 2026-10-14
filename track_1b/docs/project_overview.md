# Apertus Swiss HVET Eval

**Evaluating Apertus on Swiss Professional Education**

Version: **0.2.0**  
Status: **Hackathon active / benchmark design**  
Hackathon: **Hack Apertus 2026 — Track 1B: Swiss Voices / Core Task Intelligence**

## Overview

This project evaluates how accurately Apertus represents key concepts, structures, qualifications, institutional relationships, and selected quantitative facts in **Swiss Professional Education**.

In this project, *Swiss Professional Education* refers to the non-university tertiary sector of the Swiss education system that is also described internationally as **Higher Vocational Education and Training (HVET)**.

The project is designed as a domain-specific benchmark for Hack Apertus Track 1B. The core benchmark will use German-language prompts in Swiss Standard German and will combine authoritative Swiss reference sources with selected structured Swiss Open Government Data where appropriate.

## Research Question

> **How accurately does Apertus represent key concepts, structures, qualifications, institutional relationships, and selected quantitative facts in Swiss Professional Education?**

The project is not intended to provide a comprehensive assessment of Apertus. It examines a deliberately narrow Swiss domain in which local terminology, institutional structures, qualification frameworks, regulatory changes, and official statistics may challenge a general-purpose language model.

## Track 1B Alignment

The project targets the **Core Task Intelligence** component of Track 1B.

The current Hack Apertus requirements materially shape the benchmark design:

- a minimum of **300 single-turn question-answer cases**,
- reference answer variations and source citations,
- automated evaluation using an **LLM-as-a-judge** approach,
- a three-way evaluation label set based on **correct / incorrect / not attempted**,
- human validation of a **random 20% sample** of judge decisions,
- reporting of **judge-human agreement**,
- publication of the evaluation dataset and model-response dataset,
- reproducible evaluation execution in the formal submission repository,
- a technical report of no more than six pages.

The benchmark and evaluation design may still be refined where the official Track 1B templates require a specific schema or implementation detail.

## Benchmark Scope

The benchmark is expected to cover five broad areas:

1. **System and institutions**
   - Position of Professional Education within the Swiss education system
   - Higher education vs. Professional Education
   - Institutional roles and responsibilities

2. **Qualifications and credentials**
   - Federal Professional Examinations
   - Advanced Federal Professional Examinations
   - Professional Education Institutions and their qualifications
   - Qualification levels and titles

3. **Recognition and responsibilities**
   - Roles of federal authorities, cantons, professional organisations, and education providers
   - Recognition and regulation of programmes and qualifications

4. **Distinctions and common misconceptions**
   - Professional Education vs. universities of applied sciences and universities
   - Diploma equivalence vs. qualification-framework levels
   - Continuing education vs. formal Professional Education
   - Selected edge cases such as postgraduate programmes at Professional Education Institutions

5. **Statistics and quantitative domain knowledge**
   - Selected official statistics on Swiss Professional Education
   - Comparisons across years, education types, fields, or other published dimensions
   - Cases derived reproducibly from structured federal or Open Government Data where suitable

The final case distribution will be defined after the benchmark-generation plan is completed.

## Benchmark Construction

The project will use two complementary case types.

### Source-curated cases

These cases are constructed from authoritative Swiss institutional and legal sources, primarily SERI / SBFI and Fedlex.

They are intended for concepts such as:

- institutional structure,
- recognition,
- qualification titles,
- responsibilities,
- equivalence and non-equivalence,
- current regulation and recent reform.

### Data-derived cases

Where suitable, selected cases may be generated reproducibly from structured Swiss public data, particularly resources discoverable through:

- **I14Y**, Switzerland's national data catalogue,
- **opendata.swiss**, the central Swiss Open Government Data portal,
- official Federal Statistical Office datasets.

For such cases, dataset provenance, data version or snapshot, retrieval date, and usage conditions must be recorded.

## Evaluation Architecture

The planned core workflow is:

```text
benchmark dataset
      ↓
Apertus v1.5 via CSCS inference
      ↓
raw model-response dataset
      ↓
LLM-as-a-judge evaluation
      ↓
random 20% expert human validation
      ↓
judge-human agreement + factuality / hallucination analysis
      ↓
published results and technical report
```

The human review therefore validates a random subset rather than manually rating all 300+ responses. With exactly 300 benchmark cases, the 20% validation sample corresponds to **60 cases**.

## Apertus Access and Runtime

The evaluation is planned against **Apertus v1.5** using the Hack Apertus / Swiss AI hosted inference infrastructure.

Primary planned inference backend:

```text
https://api.swissai.svc.cscs.ch/v1
```

The interface is OpenAI-compatible and will be called programmatically from the evaluation workflow rather than through a manual chat interface.

The final model choice between **Apertus v1.5 8B** and **Apertus v1.5 70B** remains open until the evaluation setup is finalised.

The complete model identifier, backend, generation parameters, system context, evaluation date, and other relevant runtime settings will be recorded for reproducibility.

## Language

The project documentation is written in **English** to make the methodology and results accessible to the wider Apertus community.

The core benchmark prompts and Apertus responses will be in **German using Swiss Standard German**.

This distinction is intentional. The evaluation targets Swiss domain knowledge in the language in which the relevant concepts and terminology are commonly encountered.

A small English-language comparison may later repeat a limited subset of cases using official or internationally established English terminology. It remains outside the core benchmark.

## Reference Sources

Reference-standard expectations will be based primarily on authoritative Swiss sources, including:

- State Secretariat for Education, Research and Innovation (SERI / SBFI),
- Fedlex legislation and ordinances,
- official Swiss vocational education information resources,
- Federal Statistical Office data,
- I14Y and opendata.swiss for selected structured-data cases,
- other authoritative institutional sources where necessary.

The source hierarchy, source identifiers, access dates, and provenance requirements are documented in `sources.md`.

## Repository Roles

This CodeFloe repository serves as the **development and portfolio repository** for the project. It documents the project history, methodology, benchmark design, sources, and findings in a stable public location.

Hack Apertus additionally requires a formal submission repository based on the official Track 1B project template. That repository will be created separately on GitHub and will contain the required reproducible Docker / `make run` workflow.

The final benchmark dataset and model-response dataset will also be published through the required Hugging Face dataset workflow.

## Planned Outputs

The project is expected to produce:

- a documented evaluation methodology,
- a benchmark containing at least 300 single-turn Q&A cases,
- source citations and reference answer variations,
- a public benchmark dataset,
- a public Apertus model-response dataset,
- LLM-as-a-judge ratings,
- expert human validation for a random 20% sample,
- judge-human agreement results,
- hallucination and qualitative error analysis,
- a reproducible GitHub submission repository,
- a Hugging Face dataset publication,
- a technical report of up to six pages,
- a concise set of final findings in this CodeFloe repository.

Current CodeFloe repository structure:

```text
apertus-swiss-hvet-eval/
├── README.md
├── methodology.md
├── benchmark.csv
├── sources.md
├── CHANGELOG.md
└── LICENSE.md
```

Additional files will be added as the benchmark and evaluation progress.

## What This Project Does Not Evaluate

The core project does **not** aim to evaluate:

- general reasoning ability,
- overall model quality,
- safety or alignment in general,
- performance across the entire Swiss education system,
- broad multilingual performance,
- direct comparison with other language models.

These may become separate follow-up projects.

## Possible Follow-up

### 1. German-English mini-comparison

A small subset of benchmark cases may later be repeated in English using official or internationally established terminology for Swiss Professional Education.

This would explore whether Apertus produces equally accurate answers when the same Swiss institutional concepts are expressed in German and English.

### 2. Human vs. specialised decision-model evaluation

A later project may compare expert human ratings with automated classifications from a specialised decision model such as **Jev**.

This is distinct from the Hack Apertus LLM-as-a-judge requirement. It would investigate whether a specialised decision model can reproduce expert judgements sufficiently well to support larger evaluation workflows.

### 3. Further benchmark development

Future versions could extend the benchmark to additional areas of Swiss Professional Education, additional languages, or other models.

## Project Status

**v0.2.0 — Hackathon alignment and benchmark redesign**

Current tasks:

- confirm any remaining Track 1B implementation details during the Hack Apertus kick-off and mentoring,
- finalise benchmark taxonomy and case distribution,
- inspect the required Hugging Face dataset schema,
- confirm the final Apertus model size and CSCS access credentials,
- design the LLM-as-a-judge workflow,
- create the 300+ submission cases after the current planning phase,
- implement the reproducible evaluation workflow in the formal submission repository.

The two rows currently contained in `benchmark.csv` are **pre-event schema examples only** and are excluded from the submission dataset unless deliberately redesigned and reintroduced during the official hackathon period.

No Apertus evaluation results are included in this version.

## Licence

The licensing structure is defined in `LICENSE.md`:

- documentation and other non-code material: **CC BY 4.0**,
- benchmark and evaluation datasets: **CDLA-Permissive-2.0**,
- source code added to the project: **Apache-2.0**.

Dataset provenance and usage conditions for third-party or Open Government Data sources will be recorded at item or source level where applicable.
