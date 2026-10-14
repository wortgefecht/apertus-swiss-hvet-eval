# Changelog

All notable changes to this project will be documented in this file.

The project follows a lightweight versioning approach during the Hack Apertus evaluation phase. Versions reflect meaningful changes to the project definition, methodology, benchmark structure, source base, evaluation data, or published findings.

## [Unreleased]

### Planned

- Confirm remaining Track 1B implementation details after kick-off and mentoring.
- Finalise benchmark taxonomy and case distribution.
- Inspect and adopt the required Hugging Face dataset schema.
- Confirm the final Apertus v1.5 model size and CSCS access credentials.
- Define and version the LLM-as-a-judge implementation.
- Create at least 300 valid submission benchmark cases.
- Implement the reproducible GitHub submission workflow using Docker and `make run`.
- Run the Apertus evaluation.
- Perform random 20% expert human validation.
- Report judge-human agreement and final findings.
- Consider a small German-English comparison after the core submission work.

## [0.2.0] — 2026-10-01

### Changed

- Updated project status from pre-event planning to active Hack Apertus Track 1B benchmark design.
- Refined Track 1B positioning to **Swiss Voices / Core Task Intelligence**.
- Increased the planned benchmark from approximately 20–30 cases to a minimum of **300 single-turn Q&A cases**.
- Replaced full expert-human scoring as the primary evaluation method with **LLM-as-a-judge** evaluation.
- Adopted the Track 1B primary labels `correct`, `incorrect`, and `not_attempted`.
- Added **random 20% expert human validation** of judge decisions.
- Added judge-human agreement as a required evaluation output.
- Reframed hallucination and critical-error analysis as secondary analytical layers alongside the official Track 1B label scheme.
- Expanded the benchmark scope with **statistics and quantitative domain knowledge**.
- Distinguished **source-curated** and **data-derived** benchmark cases.
- Documented CodeFloe as the development / portfolio repository and GitHub as the formal Hack Apertus submission repository.

### Added

- Reference answer variations and source citations as required benchmark components.
- Planned Apertus v1.5 inference through the Swiss AI / CSCS OpenAI-compatible API.
- Reproducibility requirements for model identifier, backend, generation parameters, judge configuration, human-sample seed, and software versions.
- Planned publication of evaluation and model-response datasets through the required Hugging Face workflow.
- Open Government Data provenance requirements.
- I14Y and opendata.swiss as structured-data discovery sources.
- Hack Apertus Open Data Sources as a documented discovery resource.
- SwissGov-RSD as an optional resource for a later bilingual mini-comparison.
- Explicit provenance and usage-condition guidance for third-party and Open Government Data items in `LICENSE.md`.

### Confirmed

- Core benchmark remains German-language using Swiss Standard German.
- Core evaluation remains closed-book and single-turn.
- Research question and Swiss Professional Education domain remain unchanged.
- SBFI and Fedlex remain the primary reference standard for institutional and regulatory questions.
- The two existing `benchmark.csv` rows remain **pre-event schema examples only** and are excluded from the submission dataset unless deliberately redesigned during the official hackathon period.

## [0.1.0] — 2026-09-29

### Added

- Initial project definition in `README.md`.
- Pre-evaluation methodology in `methodology.md`.
- Curated authoritative source framework in `sources.md`, including canonical URLs, access dates, and version notes for time-sensitive legal sources.
- Initial `benchmark.csv` schema with two clearly marked example cases.
- Multi-licence structure in `LICENSE.md`.
- Initial `CHANGELOG.md`.

### Defined

- Core research question for evaluating Apertus on Swiss Professional Education.
- Expert human evaluation as the originally planned primary evaluation method.
- German-language benchmark prompts using Swiss Standard German.
- English-language project documentation.
- Four preliminary benchmark domains:
  - system and institutions,
  - qualifications and credentials,
  - recognition and responsibilities,
  - distinctions and common misconceptions.
- Initial factuality scale:
  - `2` — correct,
  - `1` — partially correct,
  - `0` — incorrect.
- Separate indicators for hallucinations and critical errors.
- Reference date of **1 October 2026** for current regulatory and institutional facts.
- Separation between benchmark definition and later evaluation results.
- Closed-book evaluation procedure with one independent Apertus run per core benchmark case.
- Reference-standard terminology for predefined expected facts and authoritative evidence.
- Response-level hallucination rate as the proportion of valid evaluated cases containing at least one material hallucination.
- Verification rule for additional factual claims not covered by a case's predefined source set.

### Planned follow-up

- Small exploratory German-English comparison using a subset of cases.
- Possible later comparison between expert human ratings and automated evaluation using Jev.
- Further benchmark development beyond the initial Hack Apertus submission.

## Versioning Notes

- `0.1.0` records the pre-event project scaffold and methodology.
- `0.2.0` records the material redesign required by the official Track 1B requirements released on 1 October 2026.
- Further `0.2.x` versions may refine schemas and implementation without changing the fundamental Track 1B design.
- A later minor version should be used if the benchmark methodology changes materially before the full run.
- `1.0.0` is reserved for the first completed and publicly documented evaluation release.

Methodological changes made after evaluation has started must be documented explicitly and must not silently alter previously evaluated cases.
