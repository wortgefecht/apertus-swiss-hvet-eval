# Apertus Swiss HVET Eval

**Domain-specific factuality evaluation of Apertus v1.5 8B on Swiss Professional Education**

**Track:** Hack Apertus 2026 - Track 1B, Swiss Voices / Core Task Intelligence  
**Event:** Online  
**Team:** Michael Gisiger (solo)  
**GitHub:** https://github.com/wortgefecht/apertus-swiss-hvet-eval  
**Dataset:** https://huggingface.co/datasets/gisiger/apertus-swiss-hvet-eval

## Summary

This project evaluates whether Apertus represents Swiss Professional Education (Higher Vocational Education and Training, HVET) accurately enough for factual information tasks in a locally specific domain. The benchmark contains 300 Swiss Standard German single-turn Q&A cases derived from 100 verified atomic facts and grounded in current SBFI and Fedlex sources. Automated SimpleQA-style grading produced 43.3% correct responses; a blinded 60-case human validation sample showed 75.0% judge-human agreement (Cohen's κ = 0.515) and indicated that the automated judge was more lenient than the human reviewer.

## Use Case Description

Swiss Professional Education is a useful stress test for localised factuality because it combines nationally specific qualification structures, protected or formal titles, multiple institutional responsibilities, financing rules, and current reforms. Errors are often plausible rather than nonsensical: a model may confuse a Federal Professional Examination with an Advanced Federal Professional Examination, assign recognition to the wrong authority, import terminology from Germany, or give a broadly correct answer followed by a materially false explanation.

The research question is:

> **How accurately does Apertus represent key concepts, structures, qualifications, institutional relationships, and selected quantitative facts in Swiss Professional Education?**

The benchmark is deliberately narrow. It does not attempt to measure general reasoning, broad multilingual ability, or overall Apertus quality. Its purpose is to expose whether a general-purpose Swiss model can retrieve and apply precise local knowledge in a domain where terminology and institutional allocation matter.

## Dataset Summary

The final benchmark contains **300 single-turn Q&A cases** in Swiss Standard German. It was constructed from **100 verified atomic facts**, with exactly three deliberately varied questions authored for each fact.

Each evaluation record contains a stable case ID, question, canonical reference answer, accepted answer variations, and source citations. A separate metadata record stores fact ID, category, subcategory, authoring difficulty, question type, misconception target where applicable, reference date, source authority/title/URL, retrieval date, source-rights note, curation method, language, and item licence.

The benchmark reference date is **1 October 2026**. It uses **16 unique source URLs** from two authorities: the State Secretariat for Education, Research and Innovation (SBFI/SERI) and the Swiss Confederation's Fedlex system. Each item cites on average 1.3 sources.

The seven final content categories are:

| Category | Cases |
| --- | ---: |
| Recognition, quality, and regulation | 87 |
| Funding and financing | 69 |
| 2026 reforms and edge cases | 63 |
| Access, pathways, and progression | 30 |
| Qualifications and titles | 21 |
| Institutions and responsibilities | 21 |
| System structure | 9 |
| **Total** | **300** |

Question forms include direct facts, application, misconception, responsibility, comparison, boundary, calculation, classification, relationship, date-rule, document-lookup, reverse-lookup, and several low-frequency specialist forms. The metadata field `difficulty` is an authoring taxonomy, not a psychometrically validated difficulty scale.

## Data Collection Method

The benchmark was built **fact-first rather than prompt-first**. A curated fact bank was created from authoritative Swiss sources, primarily SBFI/SERI and Fedlex. Each atomic fact was then transformed into three deliberately varied questions. Reference answers and answer variations were authored before model inference and frozen together with the final benchmark.

Quality control included:

- exact schema and row-count validation;
- verification that each of the 100 facts appears exactly three times;
- deterministic case ordering (`PE-001` to `PE-300`);
- source provenance, source-array alignment, and item-level licence checks;
- normalised duplicate detection and a near-duplicate scan;
- manual review of nine high-similarity question pairs, which were retained as deliberate variants rather than accidental duplicates;
- final dataset freeze before Apertus inference.

Reference answers are original benchmark formulations rather than copied source passages.

## Dataset Details

The benchmark and evaluation data are licensed under **CDLA-Permissive-2.0**. Source code is **Apache-2.0**, and documentation and other non-code material are **CC BY 4.0**.

External sources are cited but are not redistributed or relicensed. The dataset contains no participant records, personal profiles, private conversations, or sensitive personal information. Questions, reference-answer formulations, classifications, and annotations are original benchmark content.

## Evaluation

### Apertus setup

The final run used:

| Parameter | Final value |
| --- | --- |
| Model | `swiss-ai/Apertus-v1.5-8B` |
| Model revision | `ef4bbc54d6fe658bc782280ff9f3b53a10a9758f` |
| Backend | vLLM `0.23.1rc1.dev1029+ga601a9d99` |
| Runtime | Hugging Face Jobs |
| Hardware | A100 large |
| Temperature | 0.0 |
| Max completion | 1024 tokens |
| Seed | 0 |
| Thinking | false |
| Max model length | 4096 |
| Batch size | 50 |
| Prompting | one user message, no system prompt |
| Context | closed-book, no retrieval |
| Run ID | `6ad08758c66288145224df76` |

All 300 cases completed with `finish_reason=stop`. The longest response used 744 completion tokens, so no final response reached the 1024-token ceiling. Raw model responses were preserved unchanged.

### LLM-as-a-judge

Primary grading follows the Track 1B SimpleQA-style three-way scheme:

- `correct`
- `incorrect`
- `not_attempted`

The final judge was `Qwen/Qwen3-235B-A22B-Instruct-2507`, served by DeepInfra via Hugging Face Inference Providers, with temperature 0 and a 1024-token output limit.

The judge prompt treats the benchmark reference answer as authoritative. A response need not repeat irrelevant reference details, but it is marked incorrect when it contradicts a necessary fact, omits a required formal entity/value, or adds a materially false claim about the concept being tested. `not_attempted` is reserved for refusals, clarification requests, or other responses without a substantive attempt.

Before the full judge run, the final rubric/model combination was checked on a deterministic **12-case calibration sample** (seed `20261001`). The prompt and judge configuration were then frozen.

### Blinded human validation

The 12 calibration cases were excluded from the human-validation sampling pool. A fixed-seed random sample of **60 cases** was then drawn from the remaining **288 non-calibration cases** using seed `20261015`. Thus, 20% of the full 300-case benchmark received human review while calibration and validation remained disjoint.

The human evaluator was blinded to judge labels and used the same three-way rubric. This differs slightly from a simple random sample over all 300 judge decisions because the calibration cases were excluded from the sampling frame. The choice improves independence between judge calibration and validation, but is reported explicitly as a design limitation.

## Results

Automated grading labelled:

- **130/300 correct (43.3%)**
- **165/300 incorrect (55.0%)**
- **5/300 not attempted (1.7%)**

The item-level Wilson 95% interval for the correct rate is **37.8%-49.0%**.

In the 60-case human-validation sample:

- **19/60 correct (31.7%)**
- **39/60 incorrect (65.0%)**
- **2/60 not attempted (3.3%)**

Judge-human agreement was **45/60 = 75.0%** (Wilson 95% CI **62.8%-84.2%**) with **Cohen's κ = 0.515**.

### Category-level automated judge accuracy

| Category | Accuracy |
| --- | ---: |
| Qualifications and titles | 23.8% |
| Institutions and responsibilities | 33.3% |
| Access, pathways, and progression | 36.7% |
| Recognition, quality, and regulation | 40.2% |
| Funding and financing | 50.7% |
| 2026 reforms and edge cases | 50.8% |
| System structure | 55.6% |

The strongest weaknesses therefore occur where formal local precision matters most.

The question-type breakdown is even more striking: **direct factual questions scored 19.8%**, **responsibility questions 8.3%**, and **misconception prompts 75.4%**. This should not be read as a generic reasoning advantage. Many misconception items provide a contrastive frame that helps the model reject an incorrect premise, while direct-fact items demand exact Swiss terminology or values without such scaffolding.

The authoring-labelled `advanced` items scored 69.2%, compared with 42.2% for intermediate and 19.4% for basic. This counter-intuitive pattern reflects taxonomy composition, not validated difficulty: many `advanced` items are misconception or boundary cases, whereas many `basic` items are direct-fact retrieval cases.

### Judge-human disagreement

The 60-case confusion matrix is:

| Human \ Judge | Correct | Incorrect | Not attempted |
| --- | ---: | ---: | ---: |
| Correct | 15 | 4 | 0 |
| Incorrect | 11 | 28 | 0 |
| Not attempted | 0 | 0 | 2 |

Disagreement is asymmetric. Eleven human-rated incorrect answers were labelled correct by the judge, while four human-rated correct answers were labelled incorrect. No disagreement involved `not_attempted`.

The judge therefore tends to be lenient about answers that contain a correct core statement but also include a materially false domain claim. Consequently, the **43.3% automated score should not be treated as unquestioned ground truth**; the **31.7% human sample estimate** provides an important counterpoint.

## Qualitative Error Analysis

All 15 judge-human disagreements are preserved in `data/judge_human_disagreements.jsonl`.

Recurring model-error patterns across the broader benchmark include:

- confusion between Federal Professional Examination, Advanced Federal Professional Examination, HF qualifications, and related title conventions;
- incorrect allocation of responsibilities between SBFI, examination bodies, cantons, and education providers;
- correct yes/no or high-level answers followed by materially false institutional explanations;
- importation of German or generic international education terminology into a Swiss question;
- incorrect thresholds, dates, procedural steps, or document names;
- plausible expansions of abbreviations that are factually invented.

These failures matter for the intended use case because they often produce authoritative-sounding answers that are locally wrong rather than obviously nonsensical.

## Reproducibility

The GitHub repository contains the frozen benchmark, model responses, judge metadata, human-validation sample/results, analysis artefacts, construction and validation scripts, and exact inference metadata.

From a clean checkout:

```bash
make run
```

builds a Docker image and performs a deterministic offline reproduction. It:

1. validates benchmark construction;
2. validates frozen graded Apertus responses against the recorded run metadata and input SHA-256;
3. recomputes aggregate statistics;
4. verifies the headline result counts, agreement, and κ against frozen expected values.

The workflow requires **no API key and no GPU** because it reproduces scoring from fixed model outputs. The original GPU inference and external judge require the documented hosted runtimes and credentials.

The final workflow was tested locally and reproduced **130/165/5 judge labels**, **19/39/2 human labels**, **45/60 agreement**, and **κ = 0.515** exactly.

## Dataset Limitations

The benchmark covers one narrow Swiss domain, one language variety, one Apertus model size, one response per item, and one human evaluator. There is no human inter-rater reliability estimate. Some question-type groups are very small and should not be interpreted independently.

Because each atomic fact yields three items, observations are clustered. The reported Wilson intervals are therefore descriptive item-level intervals rather than cluster-adjusted inferential estimates.

No dedicated contamination analysis against Apertus training data was completed. This is a relevant opportunity for a future benchmark version if a practical training-corpus search method becomes available.

The benchmark is time-sensitive: regulatory and institutional facts can change after the **1 October 2026** reference date.

## Lessons Learnt and Recommendations

For model improvement, the results suggest prioritising:

- precise Swiss entity and title representation;
- institutional-role grounding;
- date and threshold fidelity;
- mechanisms that suppress plausible but unsupported elaboration after a correct core answer.

For benchmark development, a second expert rater, clustered uncertainty estimates, and controlled multilingual variants would provide the highest-value extensions.

A key evaluation lesson is that a domain benchmark should not rely on an automated judge alone. The human validation exposed a systematic leniency pattern that materially affects interpretation of the headline score.

## Conclusion

Apertus demonstrates partial competence in Swiss Professional Education but remains unreliable for precise domain factuality. It performs markedly better when a prompt supplies a misconception or contrastive frame than when it must retrieve exact terminology, responsibilities, or values directly.

The benchmark therefore identifies a concrete localisation gap and provides reusable artefacts for measuring future improvements to Apertus or other models in Swiss Professional Education.

## License

Documentation: **CC BY 4.0**  
Code: **Apache-2.0**  
Dataset: **CDLA-Permissive-2.0**

## References

1. Hack Apertus. *Track 1B - Swiss Voices / Core Task Intelligence*. 2026.
2. Swiss AI Initiative. *Apertus v1.5 8B model repository*. https://huggingface.co/swiss-ai/Apertus-v1.5-8B
3. State Secretariat for Education, Research and Innovation (SBFI/SERI). *Professional Education information and implementation resources*. https://www.sbfi.admin.ch/
4. Swiss Confederation. *Fedlex - Federal law publication platform*. https://www.fedlex.admin.ch/
5. Wei, J., Karina, N., Chung, H. W., Jiao, Y. J., Papay, S., Glaese, A., Schulman, J., & Fedus, W. (2024). *Measuring short-form factuality in large language models*. arXiv:2411.04368.
6. Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20(1), 37-46.
7. Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*, 22(158), 209-212.
