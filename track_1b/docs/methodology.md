# Methodology

Version: **0.2.0**  
Status: **Hackathon benchmark design**  
Project: **Apertus Swiss HVET Eval**

## 1. Purpose

This project evaluates the factual reliability of Apertus within a narrowly defined Swiss domain: **Swiss Professional Education**, internationally also referred to as Higher Vocational Education and Training (HVET).

The evaluation is designed for **Hack Apertus 2026 Track 1B — Swiss Voices / Core Task Intelligence**.

The primary aims are to assess:

1. whether Apertus provides factually correct domain information,
2. whether relevant distinctions within the Swiss system are represented correctly,
3. whether responses contain fabricated, unsupported, outdated, or materially false factual claims,
4. how consistently an automated LLM judge agrees with expert human validation,
5. which types of domain-specific errors recur.

The project does not attempt to measure the overall quality of Apertus or to provide a general benchmark of model capabilities.

---

## 2. Research Question

> **How accurately does Apertus represent key concepts, structures, qualifications, institutional relationships, and selected quantitative facts in Swiss Professional Education?**

The core evaluation focuses on German-language interaction in Swiss Standard German.

---

## 3. Track 1B Requirements

The benchmark is designed to meet the current Track 1B Core Task Intelligence requirements.

The core submission will contain at least:

- **300 single-turn Q&A cases**,
- reference answer variations,
- source citations,
- Apertus responses,
- automated LLM-as-a-judge labels,
- labels from a random **20% expert human validation sample**,
- a reported judge-human agreement rate.

The primary judge label set is:

- `correct`,
- `incorrect`,
- `not_attempted`.

The exact public dataset schema and implementation details will be aligned with the official Track 1B Hugging Face and GitHub templates before submission.

---

## 4. Benchmark Composition

The benchmark will contain **at least 300 valid cases**.

The final distribution across categories will be fixed before the complete benchmark is generated.

### 4.1 System and institutions

Cases examine the position and structure of Swiss Professional Education.

Potential topics include:

- position within the Swiss education system,
- Professional Education and tertiary education,
- distinction between Professional Education and higher education,
- Professional Education Institutions,
- institutional responsibilities.

### 4.2 Qualifications and credentials

Cases examine formal qualifications and credential structures, including:

- Federal Professional Examinations,
- Advanced Federal Professional Examinations,
- diplomas from Professional Education Institutions,
- official qualification titles,
- qualification-framework levels,
- selected postgraduate qualifications.

### 4.3 Recognition and responsibilities

Cases examine responsibilities and regulatory relationships involving:

- the State Secretariat for Education, Research and Innovation (SERI / SBFI),
- cantonal authorities where relevant,
- professional organisations,
- education providers,
- recognition and regulation of programmes and qualifications.

### 4.4 Distinctions and common misconceptions

These cases target concepts that are easy to confuse or oversimplify.

Examples may include:

- Professional Education vs. higher education,
- Professional Education Institutions vs. universities of applied sciences,
- qualification-framework level vs. academic degree equivalence,
- formal qualifications vs. continuing education,
- Professional Education diplomas vs. bachelor's degrees,
- postgraduate programmes at Professional Education Institutions vs. CAS programmes.

Some prompts may contain a plausible but incorrect assumption that Apertus should explicitly correct.

### 4.5 Statistics and quantitative domain knowledge

Selected cases may test quantitative factual knowledge derived from official Swiss data.

Possible sources include:

- Federal Statistical Office datasets,
- I14Y,
- opendata.swiss,
- other authoritative structured federal datasets.

These cases must be derived reproducibly from a documented dataset version or snapshot.

---

## 5. Case Provenance Types

The benchmark distinguishes two main provenance types.

### 5.1 Source-curated cases

These cases are created manually from authoritative institutional, regulatory, or legal sources.

Each case should include:

- a unique identifier,
- thematic category and subcategory,
- the German prompt,
- one or more reference answer variations,
- predefined expected facts where useful for quality control,
- authoritative source citations,
- applicable reference date,
- optional misconception target,
- provenance metadata.

### 5.2 Data-derived cases

These cases are generated or constructed from structured official data.

Each data-derived case must additionally record, where applicable:

- source portal,
- dataset identifier,
- source URL,
- data version or snapshot,
- retrieval date,
- usage terms or licence information,
- transformation or query used to derive the case.

The benchmark should not use automatically generated quantitative questions unless their reference answer can be verified deterministically from the documented source data.

---

## 6. Prompt Design

### 6.1 Language

Core benchmark prompts are written in **German using Swiss Standard German**.

Project documentation is written in English.

### 6.2 Single-turn design

Every core benchmark item is a **single-turn** question-answer case.

Prompts are evaluated independently and do not depend on previous conversation history.

### 6.3 Prompt style

Prompts should resemble realistic information requests rather than artificial examination questions.

The benchmark may include:

- direct factual questions,
- explanatory questions,
- comparison questions,
- scenario-based questions,
- questions containing a plausible misconception,
- quantitative questions derived from official data.

Prompts should not contain obscure traps whose only purpose is to produce model failure.

### 6.4 Reference answer variations

Each case should contain one or more accepted reference-answer formulations where useful.

Reference answer variations should represent substantively equivalent correct answers rather than stylistic paraphrases added merely to increase the number of variants.

### 6.5 Prompt consistency

Prompts are submitted without follow-up correction or clarification.

The initial answer constitutes the evaluated response.

If a prompt is subsequently found to be materially ambiguous, the case should be flagged and excluded or revised rather than interpreted retrospectively in favour of either the model or evaluator.

### 6.6 Closed-book evaluation

The core benchmark is conducted as a **closed-book evaluation**.

Apertus receives only:

- the benchmark prompt, and
- the standard system or runtime context provided by the inference environment.

Apertus does **not** receive:

- reference answers,
- predefined expected facts,
- source citations,
- evaluator notes,
- outputs or ratings from previous benchmark cases,
- retrieval-augmented context,
- web-search results,
- corrective feedback or follow-up hints.

If the inference interface introduces unavoidable external context or system behaviour, this must be documented.

---

## 7. Reference Standard

Reference answers and expected facts are derived from authoritative sources.

The source hierarchy is:

1. current federal legislation or regulation,
2. current official SERI / SBFI information,
3. SERI / SBFI registers, implementation guidance, and FAQs,
4. official Federal Statistical Office or other federal datasets,
5. official Swiss vocational education resources,
6. other authoritative institutional sources where necessary.

The benchmark does not require Apertus to reproduce source wording. Correctness is evaluated semantically.

### 7.1 Time sensitivity

The core benchmark reference date is:

> **1 October 2026**

Swiss Professional Education is subject to regulatory and terminological changes. A response that accurately describes an outdated rule but presents it as current is incorrect for the current benchmark.

### 7.2 Open Government Data

I14Y and opendata.swiss may be used as source-discovery and structured-data infrastructure.

For any actual benchmark item derived from an Open Government Data resource, the specific underlying dataset must be identified and its provenance recorded.

The portal itself is not sufficient as the factual citation for an individual quantitative case.

### 7.3 Additional claims in model responses

A factual claim is not considered false or hallucinated solely because it is not covered by the predefined source set for that case.

Material additional claims may be verified against authoritative sources during evaluation. Such verification must be documented and must not retrospectively change the predefined reference answer.

---

## 8. Apertus Model and Inference Runtime

The planned model family is **Apertus v1.5**.

The final benchmark will use one fixed Apertus model size for the core evaluation:

- Apertus v1.5 8B, or
- Apertus v1.5 70B.

The final choice will be documented before the full run.

### 8.1 Primary inference backend

The planned primary backend is the Swiss AI / CSCS OpenAI-compatible inference API:

```text
https://api.swissai.svc.cscs.ch/v1
```

The benchmark will be executed programmatically rather than manually through a chat interface.

### 8.2 Runtime controls

The final run must document, where available:

- exact model identifier,
- model size,
- inference provider,
- API endpoint,
- evaluation date,
- system prompt or default system context,
- temperature,
- maximum output length,
- top-p or other sampling parameters,
- random seed where supported,
- relevant client-library versions.

All core benchmark cases should use the same backend and generation configuration.

### 8.3 One core run per case

The default core design uses **one independent Apertus run per case**.

If repeated runs are later introduced, they must be documented as a methodological extension and must not be silently combined with the core results.

---

## 9. Automated LLM-as-a-Judge Evaluation

The primary evaluation layer will use an **LLM-as-a-judge** workflow aligned with the Track 1B requirements.

For each Apertus response, the judge receives the benchmark question, the reference answer information required by the official evaluation design, and the Apertus response.

The primary judge label is one of:

- `correct`,
- `incorrect`,
- `not_attempted`.

The final judge model, judge prompt, decoding settings, and implementation will be fixed and versioned before the full evaluation run.

Judge outputs must be stored separately from raw Apertus responses.

The judge should not be allowed to alter the reference answer or source provenance.

---

## 10. Expert Human Validation

A **random 20% sample** of judge-evaluated cases will be independently reviewed by the human evaluator.

With exactly 300 valid benchmark cases, this corresponds to **60 human-reviewed cases**.

The random sample must be selected reproducibly using a documented random seed or equivalent deterministic sampling method.

The human evaluator will use the same primary labels:

- `correct`,
- `incorrect`,
- `not_attempted`.

Human ratings are based on the documented reference answers and authoritative sources rather than unaided recollection.

Where a response cannot be rated confidently, the evaluator should:

1. return to the documented sources,
2. record a validation note,
3. flag genuine ambiguity rather than force a label without evidence.

### 10.1 Judge-human agreement

The project will report the proportion of human-reviewed cases for which the judge label matches the expert human label.

At minimum:

> **agreement rate = matching judge-human labels / total human-reviewed cases**

A confusion matrix or additional agreement statistic may be added if useful, but is not required for the initial design.

### 10.2 Single-rater limitation

The human validation uses one domain-experienced evaluator unless additional expert review becomes available.

This limits conclusions about human inter-rater reliability and must be reported as a limitation.

---

## 11. Hallucination Assessment

Hallucination analysis is retained as a **secondary analytical layer** because Track 1B explicitly concerns factuality and hallucination behaviour.

For this project, a material hallucination is a claim that:

- describes a specific fact, rule, institution, title, process, requirement, or quantitative value, and
- is demonstrably false or appears fabricated after reasonable verification against authoritative sources.

Simple incompleteness is not hallucination.

A response may therefore be incorrect without containing a hallucination.

Where hallucination is recorded as a binary response-level indicator:

- `0` = no material hallucination detected,
- `1` = at least one material hallucination detected.

The response-level hallucination rate is:

> number of valid cases containing at least one material hallucination / total number of valid evaluated cases

The final implementation of hallucination annotation may be automated, human-validated, or derived from the primary judge workflow depending on the official Track 1B implementation template.

---

## 12. Critical Errors

A case may additionally be marked as containing a **critical error**.

A critical error is a false statement that could plausibly lead to a materially incorrect educational or professional decision.

Examples include incorrect claims about:

- admission rights,
- formal equivalence of qualifications,
- recognition status,
- regulatory responsibility,
- entitlement to academic progression,
- protected or official qualification titles.

Critical errors are a secondary qualitative category and are not part of the primary Track 1B label set.

---

## 13. Evaluation Procedure

For each benchmark case:

1. finalise the case before inference,
2. record reference answer variations and source citations,
3. record provenance metadata,
4. submit the prompt once to Apertus in an independent closed-book context,
5. store the complete Apertus response unchanged,
6. run the fixed LLM judge,
7. store the judge label and judge metadata,
8. select the reproducible random 20% validation sample after the complete judge run,
9. perform expert human validation on that sample,
10. compute judge-human agreement,
11. perform planned hallucination and qualitative error analysis,
12. document any excluded or invalid cases.

Raw model responses must not be edited, shortened, or corrected before evaluation.

---

## 14. Planned Metrics

The core report will include at least:

- number of valid benchmark cases,
- distribution of `correct`, `incorrect`, and `not_attempted` judge labels,
- corresponding human-label distribution for the 20% validation sample,
- judge-human agreement rate,
- response-level hallucination rate if implemented consistently across the full set,
- number of critical errors if annotated,
- category-level breakdowns where meaningful.

Because the benchmark represents one deliberately narrow domain, results must not be interpreted as general Apertus performance estimates.

---

## 15. Qualitative Error Analysis

Recurring errors may be grouped into categories such as:

- institutional confusion,
- incorrect qualification equivalence,
- terminology errors,
- outdated information,
- overgeneralisation from foreign education systems,
- conflation of formal education and continuing education,
- fabricated titles, authorities, or procedures,
- incorrect quantitative claims,
- correct answer with misleading explanation.

Final error categories may be refined after inspecting results, but the underlying case labels and reference answers must not be changed to fit observed outputs.

---

## 16. Reproducibility

The formal Hack Apertus submission must support reproducible execution from a clean checkout using the official Track 1B repository structure, Docker, and `make run` as required by the submission template.

This CodeFloe repository documents the project and benchmark development. A separate GitHub submission repository will implement the required execution structure.

The public dataset will be published using the required Hugging Face dataset workflow.

Reproducibility metadata should include:

- benchmark version,
- source and dataset versions,
- Apertus model identifier,
- CSCS backend configuration,
- inference parameters,
- judge model and judge prompt version,
- human-sample random seed,
- software dependency versions,
- execution date.

---

## 17. German-English Mini-Comparison

If time permits, a small exploratory extension may repeat a subset of cases in English.

The same underlying facts should be tested using official or internationally established English terminology for Swiss Professional Education.

This extension:

- remains separate from the 300+ core German benchmark,
- will not alter the primary Track 1B metrics,
- will not constitute a general multilingual evaluation.

Swiss multilingual resources such as SwissGov-RSD may inform the design of this later extension, but are not part of the core reference standard.

---

## 18. Jev Follow-up

Jev is not part of the core Hack Apertus evaluation design.

A later follow-up may compare:

- expert human labels,
- the Hack Apertus LLM judge,
- classifications from a specialised decision model such as Jev.

This would examine whether a specialised decision model can reproduce expert judgement and support larger evaluation workflows.

---

## 19. Limitations

The initial evaluation has several deliberate limitations:

- one narrow Swiss domain,
- German-language core benchmark,
- one Apertus model size for the core run,
- one model response per benchmark case,
- one expert human validator,
- possible sensitivity to inference backend and generation parameters,
- dependence on the quality and completeness of reference sources,
- potential judge-model bias,
- quantitative data cases may test recall of a specific data snapshot rather than general institutional understanding.

The benchmark should therefore be interpreted as a **targeted domain evaluation**, not as a comprehensive assessment of Apertus.

---

## 20. Versioning

### v0.2.0

Methodology redesigned on **1 October 2026** after publication of the official Hack Apertus Track 1B requirements.

Major changes from v0.1.0:

- benchmark minimum increased from approximately 20–30 cases to at least 300,
- primary evaluation changed from full expert human rating to LLM-as-a-judge,
- primary labels changed to `correct / incorrect / not_attempted`,
- random 20% expert human validation added,
- judge-human agreement added,
- source-curated and data-derived case types introduced,
- Open Government Data provenance requirements added,
- Apertus v1.5 / CSCS inference workflow documented,
- formal GitHub and Hugging Face submission requirements integrated.

### v0.1.0

Pre-event project definition and human-evaluation methodology created before the official Track 1B requirements were released.

No core Apertus evaluation was executed under v0.1.0.
