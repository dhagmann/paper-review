# Statistical and factual review

Use the checks that matter to the paper; this is not a requirement to run every conceivable robustness analysis.

## Build the chain from materials to claim

For each reported result, identify the source records, inclusion rule, unit of observation, scoring, model/test and displayed rounding. An agreement with a printed number establishes numerical reproduction, not that the underlying decision was justified.

Keep a private computation ledger with source/version identifiers and enough code to recover the finding. The reader-facing report should carry the explanation and needed values, rather than links to that ledger.

## Samples and observations

- Reconcile invited/recruited/paid people, raw starts, duplicate identifiers, completion flags, matches and analysis-specific complete cases. These counts can legitimately differ. Do not declare a paid recruitment denominator wrong merely because the raw export has extra starts.
- Separate observed attention failures, incomplete checks, dropout, missing final markers and demographic exclusions. Show arithmetic that actually reconciles the sample.
- Check whether one person contributes multiple sessions. Pooling sessions changes weighting and invalidates ordinary independence assumptions for many tests; it does not automatically make every descriptive correlation meaningless.
- Keep chronological time, language, condition assignment and actual exposure distinct. Labels created during reshaping are not necessarily chronological.

## Measures and decisions

- Match questions by meaning and response anchors, not only column order. Confirm reverse scoring, item omissions and scale composition.
- A blank answer is not automatically a refusal, zero, neutral response or failure. Distinguish a question that was not offered, an offered question left unanswered, and an observed no.
- Read actual display/branching rules. Explain what an outcome measures using an ordinary example, especially when respondents first select which information they can choose to see.
- Verify language/script eligibility from what was asked. Written-language ability does not establish a particular spoken-language criterion.

## Tests and interpretation

- Check the outcome, contrast direction, independent versus paired units, degrees of freedom, effective n, p-values, intervals, coefficients, units and table stars.
- Separate an actual data/scoring error from an inferential choice. For example, show the change from correcting missingness separately from the additional change under robust standard errors. A positive estimate becoming uncertain does not become a negative effect or proof of no effect.
- Identify b versus standardized beta, Wald versus model-comparison tests, descriptive raw means versus latent means, and overall versus interaction/subtype tests. Explain the distinction only to the depth needed for the issue.
- Verify nesting and compatible identification before interpreting a model difference test. Use the appropriate scaled procedure rather than subtracting scaled chi-squares. A failed nesting comparison does not automatically invalidate every individual fitted model.
- Treat thresholds, intercepts, response scales and factor units explicitly for ordinal models when they affect the conclusion. Changing identification or anchors can require new estimates and prevents casual comparison of coefficients across scales.
- Check whether reliability/omega calculations specify their correlation type, factor model, extraction and missingness. Matching a rounded omega with one reconstruction does not establish which settings the authors used.
- Inspect model admissibility where relevant, but label extra diagnostic models as such. Do not allege that an unreported diagnostic invalidates an otherwise separate reported result.
- Use unrounded statistics for cutoff decisions and rounded statistics for display. A value slightly outside a cutoff does not satisfy it because the printed value rounds to the cutoff.

## Revision and deployment provenance

If a methods description and shared survey disagree, use timestamps and version histories to distinguish a later edited file, a draft save, a published version and the version actually available during collection. Recruitment platforms and survey hosts may hold different parts of this record.

Corroborate version definitions with observed response patterns and collection windows. A later QSF can support a hypothesis about the fielded design but does not by itself prove that design. A remembered deployment bug is a lead to investigate, not a confirmed cause.

When an update occurred during collection, identify what changed and which records could have seen each version. Do not infer exposure only from the latest version or from a save time unrelated to publication. Preserve original participant data privately and report only the relevant design facts and counts.

Keep inspection separate from participation: use version definitions or appropriate previews instead of opening a live participant link in a way that creates a new research response.

## Missing code and simulations

Distinguish a reproduction of supplied code from an independent reconstruction. For simulations, retain population parameters, seeds, attempted replications, convergence, admissibility, errors and summary denominators. Recovery when generating and fitting the same selected model is conditional on that model; it does not establish correct empirical anchors or robustness to misspecification.

Failures in a different independent simulation do not refute an original run with an unknown population or seed. Request the original materials or offer a transparently labeled replacement. Do not combine one run's convergence counts with another run's bias table.

## References and claims

Check specific substantive uses of references and update final publication details when relevant. Avoid turning successful reference checks into report items. Qualify claims that go beyond what the actual samples and design identify, while respecting limitations the authors have already stated.
