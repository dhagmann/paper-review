# Author choices and implementation handoff

The interactive HTML works as a local file. Authors select one proposed implementation option, or **Discuss Further**, which appears after the proposed options and opens a textbox. Selecting an implementation option approves its included wording. Discuss Further holds the issue for discussion; leaving all options unselected keeps it pending. There is no separate decision control or name field. Issues with a single proposed correction offer **Apply proposed revision** followed by Discuss Further.

Changes save in the current browser when local storage is available. **Export choices** downloads a JSON file for sharing or backup; **Import choices** restores it in another browser. Browser storage is a convenience, while the exported file is the portable record. The controls make no network requests.

The issue index and **Next unreviewed** help navigate long reports. Selected revisions fold unrelated alternatives; authors can reveal them or compare the original and proposed wording side by side. These are reading preferences, not implementation choices: changing the view does not change included flags, discard hidden text or alter an export. Print retains the complete stacked report, including alternatives folded on screen.

Printed selections use a filled radio marker, a bold outline and a Selected label, including Discuss Further. The selection note and comments appear beside the options. These indicators remain visible when background graphics are disabled; the browser still controls its own colour-printing preferences.

## Read a returned export

Keep the original report and the choices file together. Run, resolving `scripts/` relative to the skill:

```bash
python3 scripts/read_decisions.py author-choices.json --report paper-review.html
```

The original report-input JSON or generated `issue-register.json` can replace the HTML. An optional `--output implementation-notes.md` saves the summary. The command is read-only with respect to the report and manuscript.

Validation checks the report fingerprint, issue and proposal IDs, selected options, baseline wording and field types. Choices from a different report revision are rejected. A source report is required: a matching issue number alone does not establish that an export applies to a newer draft.

The summary contains the selected option, discussion comments, included wording, original target passage and prerequisites. It also retains edited but excluded wording under an explicit label stating that it is not selected for implementation. It flags conflicting replacements, option/wording mismatches, blank wording and missing choices. A valid JSON file can still contain an unresolved author question; the flags are questions to resolve before implementation.

## Apply the instructions

- A selected implementation option authorizes its included changes. **Discuss Further** and unselected issues do not authorize implementation, even when they contain edited drafts.
- Treat `included` as a wording selection within the chosen option, not as approval by itself.
- Follow the selected option. Do not apply every alternative in the original report. Common changes can accompany either option.
- Preserve user-edited wording and comments, but verify claims and numerical consistency. An edited coefficient or denominator may require rerunning analyses; editing prose does not itself do that work.
- Check the original prerequisites. Exported text does not establish that a pending analysis, source check or repository update has happened.
- If a comment contradicts the structured choice, two alternatives replace the same passage, or an included passage is empty, resolve the ambiguity before applying that part. Continue with independent, unambiguous approved changes.

## Format

Exports use `format: "paper-review-decisions"` and integer `schema_version: 1`. They carry a SHA-256 report fingerprint, report title, export time and one entry per issue. Each issue includes:

- Stable `id`, `selected_option_id`, its label and `comment`. The retained `decision` field is derived automatically: `implement` for a revision option, `discuss` for Discuss Further, and `undecided` when cleared. It is not a second author input.
- Proposed passages identified by stable IDs, with baseline `original_text`, current editable `text`, `included`, the source `current_text` when replacing a quote, and any `condition`/`option_ids`.
- An `edited` flag for convenience; the validator recomputes it from the original wording.

The validator recovers labels, source passages and prerequisites from the original report rather than trusting altered metadata in an imported file. It preserves the author's choice, comment, included flags and edited text. Only report content needed to understand the choices is embedded; local source-file paths and participant data are not included.

Older exports remain readable. An earlier unapproved candidate does not become approved merely by importing it. An imported Skip remains unapproved and is identified inside the discussion panel. Existing discussion text and edited alternatives are retained when switching choices or clearing a selection.
