# Report input and renderer

Run the script with paths relative to the skill directory:

```bash
python3 scripts/build_report.py /path/to/review.json --output-dir /path/to/report
```

Outputs are `paper-review.html`, `paper-review.pdf`, `issue-register.json`, and `quote-checks.json`. Override the basename with `--basename`. The HTML contains inline CSS, JavaScript and embedded local figures. Authors can open that one file locally to select options, comment, edit proposed wording, and export/import choices without a server. The PDF hides those controls and preserves the report layout.

The HTML also supplies an issue index with review-status markers, next-unreviewed navigation, focused selected wording and a side-by-side comparison toggle. An option-specific passage is folded only when its `option_ids` exclude the selected option and the author has not included it manually. Other alternatives remain accessible, and print restores all passages in the original stacked format.

Use `--html-only` for content iteration before the final PDF. PDF rendering needs Node, the Playwright package and a Chromium executable. Existing installations are discovered, or supply:

```bash
python3 scripts/build_report.py review.json --output-dir report \
  --playwright-module /path/to/node_modules/playwright \
  --browser /path/to/chromium
```

Do not put credentials in these arguments or in a report input. Optional `--preview-dir /path/to/output/playwright` captures the first issue for visual review.

## Top-level fields

```json
{
  "title": "Paper title — proposed manuscript edits",
  "subtitle": "Page references refer to the dated submission PDF.",
  "sources": {
    "draft": {
      "label": "Manuscript",
      "path": "source/manuscript.pdf",
      "text_path": "source/manuscript-layout.txt"
    }
  },
  "issues": []
}
```

Paths are relative to the input JSON. A source can be a PDF or an extracted UTF-8 text file. PDF text extraction uses Poppler `pdftotext -layout`; a cached `text_path` is optional. Pages in text files are separated by form-feed characters. For an unpaged source, omit `page` in the quotation and provide a precise `locator`.

The source mapping is private provenance. Only its human-facing label and quote page/locator appear in the report, not file links or paths.

## Issue fields

Required fields:

- `id`: unique stable identifier, used for checks and review conversations.
- `title`, `location`: concrete issue heading and manuscript location.
- `status`: human-facing label, usually `Reporting fix`, `Analysis decision`, `Author confirmation`, `Package update` or `Editorial fix`.
- `quotes`: source excerpts, each with `source` (mapping key), `text`, and `page` or `locator`.
- `explanation`: paragraphs explaining the actual problem and consequence.
- At least one `edits` or `insertions` entry with complete proposed wording.
- `steps`: the coordinated implementation actions.

Optional fields:

- `tables`: explanatory/comparison tables placed in the background section.
- `after_table`: further background paragraphs after those tables.
- `options`: meaningful alternatives, each with a stable `id`, `label`, `description` and optional `recommended: true`. The recommended choice receives a star but is not preselected.
- `replacement_tables`: complete replacement values placed after the proposed wording, with their sample/model/option in the title or note.
- `figures`: local images for needed context, each with `path`, `caption` and optional `label`. Use PNG, JPEG or WebP; the renderer embeds the bytes. Visually check source crops and label proposed figures clearly.
- `omit_quotes`: zero-based quote indices not displayed because a fuller displayed passage already covers them. They are still source-checked.

Table objects have `title`, `headers`, `rows`, and optional `note`. Headers and cells are plain text; statistics must be calculated separately. The renderer does not choose models, compute tests or invent data. Each row must have the same length as `headers`.

## Excerpts and changes

```json
{
  "quotes": [
    {"source": "draft", "page": 5, "text": "The full current sentence."}
  ],
  "edits": [
    {
      "quote": 0,
      "id": "participants-observed",
      "label": "Replace the full sentence in Participants",
      "text": "The complete proposed replacement sentence.",
      "condition": "Use only if Option A is selected."
    }
  ],
  "insertions": [
    {
      "label": "Table 2 note — add after the sample description",
      "text": "The complete proposed note.",
      "condition": "Use after the relevant analysis is regenerated."
    }
  ]
}
```

`quote` references a zero-based element of that issue's `quotes` list. `label` locates the replacement/insertion. `condition` is report commentary outside the copyable text. Pair a full replacement sentence with its full current sentence, not only the few words that prompted the issue.

Give every option and proposed change a stable `id`, unique within its issue. An option-specific change also sets `option_ids`, for example `"option_ids": ["observed-outcomes"]`. Selecting an option checks the linked wording; common changes omit `option_ids`. Keep human-facing prerequisites in `condition` as well. Never infer approval from the recommendation marker.

Older inputs can omit these IDs; the renderer assigns positional IDs. For unmapped alternative replacements of the same quotation, no alternative is automatically included. An author must explicitly include the intended wording. For new reports, provide IDs and option mappings so exports remain clear.

Different options can supply multiple `edits` for the same current quote. Give each alternative a distinct label and explicit `condition`. The shared current passage stays unmarked so its deletion highlighting does not imply one option has already been selected; each proposed paragraph highlights its own additions.

For a faithful separate column extraction, a quote can set `verification_text` to a local extracted-text path. Record its original `source` and `page` as usual. The check uses that extraction while the report still identifies the original page. Do not use a newly typed quotation as its own verification source.

The renderer checks every quoted text against its source after whitespace, ligature and line-wrap normalization. It allows a hyphen to be kept or removed where the source actually wraps a line, but it does not discard meaningful internal hyphens everywhere. A failed quote check stops rendering rather than silently labeling a paraphrase as verbatim.

Report text is escaped; HTML markup in text fields is displayed literally. No evidence hyperlinks are generated. A plain DOI URL within a proposed reference is acceptable. The PDF includes headings/bookmarks and is printed from the same HTML.

For a review with no material findings, provide `issues: []` and a `no_issues_message` stating the actual scope and limits; do not invent an issue to populate the layout.

See [decision-handoff.md](decision-handoff.md) for the exported choices format and the read-only validation/summary command.
