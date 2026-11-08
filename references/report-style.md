# Writing and formatting an actionable paper review

The report should let a coauthor see the current claim, understand the discrepancy and know exactly what to do. More context is useful when it changes a decision; length alone is not a virtue.

## Current draft

Quote the actual target manuscript/proof with a page or precise locator. Label response-memo quotations separately. Use a full sentence or paragraph when the proposed edit replaces it. A fragment beginning after “Of these,” or “To achieve…,” is not a safe replacement anchor for a new complete sentence.

For a table, identify the affected row/column. Use faithful extracted cells or a crop when the text cannot be recovered cleanly. Keep a whole rewritten passage legible; reserve red strikeout for shorter localized deletions and use the green proposed panel for a wholesale replacement.

## Explain the issue concretely

Lead with what actually happened. Then give only the background needed to see why it matters. For example, define a nested comparison by saying that one model must be obtainable solely by restricting the other; explain what changed in this paper's constraints. Do not stop at “identification is inconsistent.”

Where useful, show a short numerical comparison isolating the cause:

- Original coding with original errors.
- Corrected coding with original errors.
- Corrected coding with the proposed inference method.

Explain what a coefficient means in the paper's units. Distinguish a changed sign, a changed point estimate and changed statistical precision. Identify what remains uncertain without making an uncheckable claim about the authors' unseen analysis.

Check the surrounding text. If the draft already discusses low reliability or limited generalizability, target the actual remaining omission or contradictory sentence rather than alleging the entire limitation was ignored.

## Proposed wording

Supply complete replacement prose or a complete insertion, not merely “qualify the claim.” Include needed sample sizes, effect units, tests and uncertainty when supported. For a small number change, a short exact replacement is enough; for a substantive methods issue, give a replacement paragraph and a table note when both need editing.

Specify the whole replacement span. If an old next sentence says “the only exception was X,” replace it too when the new result says X and Y are uncertain. Do not leave a future author to discover that the proposed text conflicts with the immediately adjacent old text.

Distinguish proposed manuscript wording from report commentary. Prerequisites belong in a clearly labeled condition outside the copyable text: “Use after confirming the fielded branching” or “Option A only, with n = …”. Avoid saying the authors have supplied code, updated a deposit or rerun a model until that work has actually happened.

## Real implementation choices

Use options when there is a genuine author/analysis decision, not to pad an obvious typo fix. Mark the recommended route and state its consequences. Useful alternatives include:

- A smaller accurate descriptive interpretation versus a new model-based comparison.
- Transparent historical reproduction versus a corrected primary sample with the historical result as a sensitivity.
- Recovering an original analysis versus adopting a labeled reconstruction.
- Changing primary error estimation versus documenting a specified sensitivity, with required data fixes applied in either case.

An incorrect missing-value rule, mislabeled test or false design statement is not a valid “leave as is” alternative. If an option changes the population, units, model or estimator, identify the dependent results that must be regenerated. A note specific to Option A must not silently apply to B or C.

## Implementation and tables

List coordinated actions in the order needed to apply the change. Name the relevant section/table/note and which values must move together. When reordering a correlation matrix, reorder rows and columns together. When updating a model, keep its coefficients, SEs, intervals, stars and n from the same fit.

Provide corrected values directly when possible. Label replacement tables with the option/sample/model they belong to. Keep historical and new fits distinct. These tables support the issue; do not add a separate appendix of successful replications.

## Appearance

The bundled CSS preserves the approved report language: navy headings, Inter/sans labels, Libertine/serif prose, gray source panels, red short deletions, green additions and an amber prerequisite panel. Mark recommendations with a star only; reserve the blue option background for the author's selected choice. Put the visible issue index at the beginning. Use source page labels, compact tables and simple checkboxes as review aids.

Render one standalone HTML document and print that HTML to a bookmarked PDF. Keep the title/legend short. Default to no executive summary, success ledger, audit-path lists or evidence hyperlinks. A DOI appearing as plain text inside a proposed bibliographic entry is not an evidence-file link.

## Reader questions to solicit

Ask the independent reader to check the generated current report and ask questions such as:

- Which part is a definite correction and which is an inference choice?
- What exactly does this coefficient/test/outcome mean here?
- Is the fielded design established, or only supported by later materials?
- Does the finding concern the reported analysis or an extra diagnostic?
- Can this replacement be pasted without leaving a grammatical fragment or contradictory sentence?
- What must be confirmed or rerun before using each proposed paragraph or table?

Answer from the actual records, integrate the answers and have the reader recheck material changes. Do not provide the reader an obsolete base file while the final report is assembled from additional overrides.
