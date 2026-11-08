---
name: paper-review
description: "Review empirical manuscripts, revisions or proofs for statistical and reporting problems, reproduce analyses when data/code are available, and deliver a clear PDF/HTML report showing current text, proposed wording and implementation choices. Use for substantive paper review rather than ordinary copyediting."
---

# Paper review

Produce a report that coauthors can act on without opening audit logs or reconstructing the argument. Review the requested manuscript version, distinguish numerical reproduction from statistical correctness, and turn each material finding into a concrete edit or a clearly bounded author question.

## Establish the review target

- Identify the authoritative draft or proof and keep its page references distinct from response letters, prior submissions and reconstructed manuscripts. Quote the version being reviewed, not a corrected working draft.
- Use available data, scripts, survey definitions, registration/materials and relevant connected sources to resolve factual questions. Keep original inputs, reproducibility calculations and private notes separate from a manuscript repository when appropriate.
- Match the depth of work to the request and available materials. A proof-only review does not automatically require a new statistical project. Missing revision code may prevent exact reproduction even when a transparent independent reconstruction is possible.

For an empirical/statistical review, read [references/review-method.md](references/review-method.md). It covers units, missingness, tests, model comparisons and collection/version provenance.

## Write actionable issues

Read [references/report-style.md](references/report-style.md) before composing the report. The essential shape is:

1. **Current draft:** verified wording with a page or precise location, using enough context to show the actual claim.
2. **What needs to change and why:** the concrete discrepancy, enough statistical/design background to understand it, the numerical or inferential consequence, and any limit on the finding.
3. **Proposed wording:** complete text the authors can copy. Clearly identify the whole sentence/passage/table note replaced or the exact insertion location.
4. **Implementation options:** only genuine choices. State a recommended route, what each route changes and what must be confirmed or rerun first.
5. **Implementation:** specific coordinated edits, affected tables/figures and recalculations. Supply corrected table values where these can be established.

Default to issues that need attention. Do not add a successful-replication ledger, opening executive overview, evidence file links, or audit-path dumps unless requested. Put a numerical problem discovered in an overview into a proper issue instead. Source page references, and bibliographic identifiers within proposed references, are appropriate.

If no material issues are found, state that with the actual review scope and limits; do not manufacture findings to fill the format.

Do not present an optional audit model as a flaw in a paper that never used it. Check whether the draft already acknowledges a limitation before asking the authors to acknowledge it. A result that differs from an unseen original run is not proof that the original run is false.

## Independent reader pass

For a substantive report with analysis/design findings, use a separate subagent as a coauthor reader when delegation is available. Give it the **generated current report** and necessary source material, not an obsolete base file. Ask it to identify unclear mechanisms, missing background, overreach, replacement-span errors and prerequisites, and to ask the main agent clarification questions.

Answer those questions using the actual records/calculations; integrate the answers into the report. Have the reader check material revisions. Keep this exchange in private task notes, not as another report section. Ask the user only for genuinely unavailable information; do not substitute a permission question for work already authorized. For a small purely editorial task, scale the independent pass to the task rather than creating an elaborate review process.

## Render the report

Use the bundled format to preserve the approved appearance: navy headings, serif body text, readable gray current-text panels, red short deletions, green proposed wording, recommendation markers, explicit prerequisite panels and compact tables. Full original passages remain readable during wholesale rewrites. The standalone HTML includes an issue index, next-unreviewed navigation, focused selected wording and optional side-by-side comparison. Authors can select options, comment, edit proposed wording and export their choices. Screen text is sized for desktop/tablet reading. Generate the PDF from that same HTML; print hides the review controls and preserves the original typography and complete stacked report.

Read [references/report-schema.md](references/report-schema.md), write a report JSON input, then run:

```bash
python3 scripts/build_report.py /absolute/path/review.json --output-dir /absolute/path/report
```

Resolve `scripts/` relative to this skill folder, not the paper's working directory. The renderer uses the Python standard library and Node with Playwright/Chromium for PDF output. It discovers an existing installation or accepts explicit paths; it does not install dependencies or contact a remote renderer. If these dependencies are unavailable, prepare the HTML and use the environment's suitable PDF tool, reporting any remaining output limitation. Local browser IPC may require the environment's normal execution-approval mechanism.

The example input in [assets/example-review.json](assets/example-review.json) is synthetic. Do not copy its claims or numbers into a real review.

Give options and proposed changes stable IDs. Link option-specific wording with `option_ids` so selecting an option includes the correct alternatives. A recommendation is not a submitted choice. Keep common changes separate from mutually exclusive replacements.

## Implement returned choices

Read [references/decision-handoff.md](references/decision-handoff.md) when the user returns a choices JSON file. Validate it against the original interactive HTML or report-input JSON with `scripts/read_decisions.py` before applying anything. Selecting an implementation option is the instruction to apply its included wording; **Discuss Further** opens a textbox and holds that issue for discussion. Leave unselected issues pending. Preserve comments and author edits; check prerequisites and recalculate edited numerical claims. Ask about contradictory alternatives or unresolved choices rather than silently combining them. The handoff script summarizes instructions; it does not modify a manuscript.

## Verify and deliver

- Check current quotations against their identified source pages, allowing only typography/layout normalization. For an image/table or multicolumn PDF, obtain a faithful crop or column extraction rather than inventing a searchable quote.
- Verify that proposed text is grammatical over the **entire replacement span**. Remove adjacent old sentences that would contradict the new statement. Link each conditional sentence/note to the applicable option.
- Use numbers from the selected sample, model, estimator and standard-error calculation together. Mark alternatives that require regeneration; do not mix old and new tables or claim pending work is already done.
- Inspect representative PDF pages, including a long issue, a proposed-text block and replacement tables. Check all items render, text/glyphs are legible, and page breaks preserve context. Preserve bookmarks for a longer PDF.
- Return the report PDF and HTML, with a concise description of what was completed and material limits. A report does not authorize sending it, changing a journal submission, publishing data or editing a live study. Apply any existing authorization separately.
