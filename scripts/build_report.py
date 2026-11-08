#!/usr/bin/env python3
"""Render a source-checked paper-review JSON input to standalone HTML and PDF."""
from pathlib import Path
import argparse
import base64
import difflib
import hashlib
import html
import json
import re
import subprocess
import unicodedata
from review_model import manifest_for

SKILL = Path(__file__).resolve().parents[1]
WRAP = "\ue000"
TOKEN = re.compile(r"\s+|[−\-]?\d[\d,]*(?:\.\d+)?%?|[\w’\-–]+|[^\w\s]")
esc = lambda value: html.escape(str(value))


def typography(text):
    return unicodedata.normalize('NFKC', text).translate(str.maketrans({'’': "'", '‘': "'", '“': '"', '”': '"', '‐': '-', '‑': '-'}))


def quote_matches(quote, source):
    """Only source line-wrap hyphens can disappear; internal hyphens remain."""
    source = typography(source)
    source = re.sub(r'(?<=\w)-[ \t]*\n[ \t]*(?=\w)', WRAP, source)
    source = re.sub(r'\s+', ' ', source).strip()
    needle = re.sub(r'\s+', ' ', typography(quote)).strip()
    pattern = []
    for i, character in enumerate(needle):
        if i and re.match(r'\w', needle[i - 1]) and re.match(r'\w', character):
            pattern.append(WRAP + '?')
        pattern.append('(?:-|' + WRAP + ')' if character == '-' else re.escape(character))
    return bool(needle) and re.search(''.join(pattern), source) is not None


def word_diff(before, after):
    a, b = TOKEN.findall(before), TOKEN.findall(after)
    matcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    if matcher.ratio() < .5:
        return esc(before), f'<ins>{esc(after)}</ins>'
    old, new = [], []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        left, right = ''.join(a[i1:i2]), ''.join(b[j1:j2])
        old.append(esc(left) if op == 'equal' or not left.strip() else f'<del>{esc(left)}</del>')
        new.append(esc(right) if op == 'equal' or not right.strip() else f'<ins>{esc(right)}</ins>')
    return ''.join(old), ''.join(new)


def read_source(path):
    if path.suffix.lower() == '.pdf':
        return subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)
    return path.read_text(encoding='utf-8')


def table_markup(table):
    headers, rows = table['headers'], table['rows']
    if not headers or any(len(row) != len(headers) for row in rows):
        raise ValueError('Table row/header lengths differ.')
    parts = [f'<div class="tableblock"><h4>{esc(table["title"])}</h4>', '<table class="data"><thead><tr>']
    parts.extend(f'<th>{esc(cell)}</th>' for cell in headers)
    parts.append('</tr></thead><tbody>')
    for row in rows:
        parts.append('<tr>' + ''.join(f'<td>{esc(cell)}</td>' for cell in row) + '</tr>')
    parts.append('</tbody></table>')
    if table.get('note'):
        parts.append(f'<p class="tablenote">{esc(table["note"])}</p>')
    parts.append('</div>')
    return ''.join(parts)


def build(input_path, output_dir, basename):
    report = json.loads(input_path.read_text())
    root = input_path.parent
    sources, source_texts, checks = report.get('sources', {}), {}, []
    for key, source in sources.items():
        source_path = root / source.get('text_path', source['path'])
        source_texts[key] = read_source(source_path)
    issues = report['issues']
    if len({issue['id'] for issue in issues}) != len(issues):
        raise ValueError('Issue ids must be unique.')
    if not issues and not report.get('no_issues_message'):
        raise ValueError('An empty review needs an explicit scope-limited no_issues_message.')
    for issue in issues:
        for field in ['title', 'location', 'status', 'quotes', 'explanation', 'steps']:
            if field not in issue:
                raise ValueError(f'Missing {field} in {issue["id"]}.')
        if not issue.get('edits') and not issue.get('insertions'):
            raise ValueError(f'No proposed wording in {issue["id"]}.')
        indices = [edit['quote'] for edit in issue.get('edits', [])]
        for index in set(indices):
            alternatives = [edit for edit in issue.get('edits', []) if edit['quote'] == index]
            if len(alternatives) > 1 and not all(edit.get('condition') for edit in alternatives):
                raise ValueError(f'Alternative replacements need explicit conditions in {issue["id"]}.')
        if set(indices) & set(issue.get('omit_quotes', [])):
            raise ValueError('An edited source quote cannot be omitted.')
        for quote in issue['quotes']:
            if quote.get('page') is None and not quote.get('locator'):
                raise ValueError(f'Quotation needs a page or precise locator in {issue["id"]}.')
            text = source_texts[quote['source']]
            if quote.get('page') is not None:
                pages = text.split('\f')
                if type(quote['page']) is not int or quote['page'] < 1 or quote['page'] > len(pages):
                    raise ValueError(f'Invalid source page in {issue["id"]}.')
                text = pages[quote['page'] - 1]
            if quote.get('verification_text'):
                text = read_source(root / quote['verification_text'])
            matched = quote_matches(quote['text'], text)
            checks.append({'issue': issue['id'], 'source': quote['source'], 'page': quote.get('page'),
                           'locator': quote.get('locator'), 'matched': matched})
            if not matched:
                raise ValueError(f'Current quotation does not match its source in {issue["id"]}.')
    manifest = manifest_for(report, basename)
    interactive_issues = {issue['id']: issue for issue in manifest['issues']}
    style = (SKILL / 'assets/report.css').read_text() + '\n' + (SKILL / 'assets/interactive.css').read_text()
    parts = ['<!doctype html><html lang="en"><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             f'<title>{esc(report["title"])}</title><style>{style}</style>',
             f'<main><h1>{esc(report["title"])}</h1>',
             f'<p class="meta">{esc(report.get("subtitle", ""))}</p>',
             '<nav class="review-toolbar interactive-only" aria-label="Review controls">'
             '<div class="toolbar-heading"><strong>Your review</strong><span id="review-progress" class="review-progress"></span></div>'
             '<div class="toolbar-actions"><button type="button" class="primary" id="export-choices">Export choices</button>'
             '<button type="button" id="import-choices">Import choices</button>'
             '<button type="button" id="print-review">Print / save PDF</button></div>'
             '<div class="toolbar-navigation"><button type="button" id="next-unreviewed">Next unreviewed</button></div>'
             '<p id="review-message" class="review-message" aria-live="polite">Your edits stay in this browser. Export choices to share them.</p>'
             '<input id="import-file" type="file" accept=".json,application/json" hidden></nav>'
             '<noscript><p class="meta">Enable JavaScript to select options, edit wording and export choices. The report remains readable below.</p></noscript>',
             '<p class="legend"><del>Red strikeout</del> marks short deletions; <ins>green</ins> marks additions. '
             'Full rewritten passages remain unmarked in the current-text panel for readability. '
             '★ marks the recommended implementation option.</p>',
             '<nav id="issue-navigation" class="issue-navigation interactive-only" aria-labelledby="issue-index-heading">'
             '<h2 id="issue-index-heading">Issues</h2>'
             '<p class="index-legend">✓ Revision selected · ? Discuss Further · □ Unreviewed</p>'
             '<div id="issue-index-list"></div></nav>']
    classes = {'Reporting fix': 'fix', 'Editorial fix': 'fix', 'Analysis decision': 'decision',
               'Author confirmation': 'confirm', 'Package update': 'package'}
    for number, issue in enumerate(issues, 1):
        edits = issue.get('edits', [])
        by_quote = {}
        for edit in edits:
            by_quote.setdefault(edit['quote'], []).append(edit)
        parts.extend([f'<article class="issue" data-id="{esc(issue["id"])}">',
                      '<div class="itemhead"><span class="check" role="img" aria-label="No option selected" data-state="pending"></span>',
                      f'<h2 tabindex="-1">{number}. {esc(issue["title"])} <span class="pill {classes.get(issue["status"], "confirm")}">'
                      f'{esc(issue["status"])}</span></h2></div>', f'<p class="where">{esc(issue["location"])}</p>'])
        for index, quote in enumerate(issue['quotes']):
            if index in issue.get('omit_quotes', []):
                continue
            label = sources[quote['source']].get('label', quote['source'])
            locator = f'p. {quote["page"]}' if quote.get('page') else quote.get('locator', '')
            variants = by_quote.get(index, [])
            current = word_diff(quote['text'], variants[0]['text'])[0] if len(variants) == 1 else esc(quote['text'])
            parts.append(f'<div class="context"><div class="label">Current draft</div><p class="current-text">{current}</p>'
                         f'<div class="source">{esc(label)}, {esc(locator)}</div></div>')
        for figure in issue.get('figures', []):
            image_path = root / figure['path']
            mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}.get(image_path.suffix.lower())
            if not mime:
                raise ValueError('Context figures must be PNG, JPEG or WebP.')
            image = base64.b64encode(image_path.read_bytes()).decode('ascii')
            parts.append(f'<figure class="tableblock"><figcaption class="label">{esc(figure.get("label", "Figure context"))}</figcaption>'
                         f'<img alt="{esc(figure["caption"])}" style="max-width:100%" src="data:{mime};base64,{image}">'
                         f'<p class="tablenote">{esc(figure["caption"])}</p></figure>')
        parts.append('<h3>What needs to change and why</h3><div class="why">')
        parts.extend(f'<p>{esc(text)}</p>' for text in issue['explanation'])
        parts.extend(table_markup(table) for table in issue.get('tables', []))
        parts.extend(f'<p>{esc(text)}</p>' for text in issue.get('after_table', []))
        parts.append('</div>')
        section_class = '' if issue.get('options') else ' interactive-only'
        parts.append(f'<section class="option-section{section_class}"><h3>Implementation options</h3>'
                     '<button type="button" class="clear-option interactive-only">Clear selection</button><div class="options">')
        for index, option in enumerate(interactive_issues[issue['id']]['options']):
            source_option = issue.get('options', [])[index] if issue.get('options') else {}
            recommended = source_option.get('recommended', False)
            label = ('★ ' if recommended else '') + option['label']
            description = source_option.get('description', 'Use the proposed wording below, with any edits you make.')
            label_id = f'option-label-{number}-{index}'
            description_id = f'option-description-{number}-{index}'
            parts.append(f'<label class="option{" recommended" if recommended else ""}" data-option-id="{esc(option["id"])}">'
                         f'<span class="option-heading"><input class="option-radio interactive-only" type="radio" name="option-{number}" value="{esc(option["id"])}" '
                         f'aria-labelledby="{label_id}" aria-describedby="{description_id}">'
                         f'<strong id="{label_id}"><span class="choice" aria-hidden="true"></span>{esc(label)}</strong>'
                         '<span class="print-selection-label" aria-hidden="true">Selected</span></span>'
                         f'<span class="option-description" id="{description_id}">{esc(description)}</span></label>')
        parts.append(f'<div class="option discussion-option interactive-only"><label class="option-heading">'
                     f'<input class="discussion-radio" type="radio" name="option-{number}" value="discuss">'
                     '<strong><span class="choice" aria-hidden="true"></span>Discuss Further</strong>'
                     '<span class="print-selection-label" aria-hidden="true">Selected</span></label><div class="discussion-details" hidden>'
                     '<label>What would you like to discuss?<textarea class="issue-comment" rows="3" '
                     'placeholder="Add your question, concern or alternative suggestion."></textarea></label>'
                     '<p class="legacy-decision-note" hidden></p></div></div></div></section>'
                     '<p class="review-print-note"></p>')
        parts.append('<div class="wording-heading"><h3>Proposed wording</h3>'
                     '<div class="wording-tools interactive-only"><button type="button" class="show-alternatives" aria-expanded="false" hidden>Show alternatives</button>'
                     '<button type="button" class="compare-wording" aria-pressed="false">Compare side by side</button></div></div>'
                     '<p class="wording-focus-note interactive-only" aria-live="polite"></p>')
        for change in sorted(interactive_issues[issue['id']]['proposals'], key=lambda item: (item['quote_index'] is None, item['quote_index'] or 0)):
            parts.append(f'<section class="proposal-group" data-group-id="{esc(change["id"])}">')
            if change.get('condition'):
                parts.append(f'<div class="condition">{esc(change["condition"])}</div>')
            proposed = word_diff(change['current_text'], change['original_text'])[1] if change['quote_index'] is not None else f'<ins>{esc(change["original_text"])}</ins>'
            parts.append('<div class="comparison-grid">')
            if change['quote_index'] is not None:
                parts.append('<div class="context comparison-current"><div class="label">Current draft</div>'
                             f'<p class="current-text">{esc(change["current_text"])}</p></div>')
            parts.append(f'<div class="proposal" data-proposal-id="{esc(change["id"])}"><div class="label">{esc(change["label"])}</div>'
                         f'<p class="proposed-text">{proposed}</p>'
                         f'<textarea class="wording-editor interactive-only" aria-label="Proposed wording: {esc(change["label"])}" hidden>{esc(change["original_text"])}</textarea>'
                         '<div class="proposal-controls interactive-only"><label><input type="checkbox" class="include-wording"> Include this wording</label>'
                         '<span class="wording-state"></span><button type="button" class="edit-wording" aria-expanded="false">Edit wording</button>'
                         '<button type="button" class="restore-wording" hidden>Restore original</button></div></div></div></section>')
        if issue.get('replacement_tables'):
            parts.append('<h3>Replacement values for the selected approach</h3>')
            parts.extend(table_markup(table) for table in issue['replacement_tables'])
        parts.append('<h3>Implementation</h3><ol class="steps">')
        parts.extend(f'<li>{esc(step)}</li>' for step in issue['steps'])
        parts.append('</ol><p class="issue-conflicts interactive-only" role="alert" hidden></p></article>')
    if not issues:
        parts.append(f'<p>{esc(report["no_issues_message"])}</p>')
    encoded_manifest = json.dumps(manifest, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    parts.extend(['</main>', f'<script type="application/json" id="review-manifest">{encoded_manifest}</script>',
                  '<script>' + (SKILL / 'assets/interactive.js').read_text() + '</script>', '</html>'])
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / f'{basename}.html'
    rendered = '\n'.join(parts)
    assert 'href=' not in rendered
    html_path.write_text(rendered)
    (output_dir / 'issue-register.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (output_dir / 'quote-checks.json').write_text(json.dumps({'issues': len(issues), 'quotes': len(checks),
        'all_matched': all(check['matched'] for check in checks), 'input_sha256': hashlib.sha256(input_path.read_bytes()).hexdigest(),
        'checks': checks}, ensure_ascii=False, indent=2) + '\n')
    noun = 'issue' if len(issues) == 1 else 'issues'
    print(f'Interactive HTML created; checked {len(checks)} source quotations in {len(issues)} {noun}.', flush=True)
    return html_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--basename', default='paper-review')
    parser.add_argument('--html-only', action='store_true')
    for option in ['browser', 'playwright-module', 'preview-dir']:
        parser.add_argument('--' + option)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', args.basename):
        parser.error('The output basename must be a filename stem, not a path.')
    html_path = build(args.input.resolve(), args.output_dir.resolve(), args.basename)
    if not args.html_only:
        command = ['node', str(SKILL / 'scripts/render_pdf.js'), str(html_path), str(html_path.with_suffix('.pdf'))]
        for option in ['browser', 'playwright-module', 'preview-dir']:
            value = getattr(args, option.replace('-', '_'))
            if value:
                command.extend(['--' + option, value])
        subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
