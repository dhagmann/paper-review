#!/usr/bin/env python3
"""Validate a review export and print an implementation handoff. Read-only."""
from collections import Counter
from pathlib import Path
import argparse
import json
from review_model import load_manifest, validate_decisions


def summarize(payload):
    lines = [f'# Review choices: {payload["report"]["title"]}', '']
    if payload['reviewer']:
        lines.extend([f'Reviewer: {payload["reviewer"]}', ''])
    lines.extend(['Selecting an implementation option approves its included changes. Discuss Further and unselected issues are not approvals. Check all prerequisites, '
                  'conflicting alternatives and edited numerical claims before applying wording.', ''])
    count = 0
    for issue in payload['issues']:
        changed = any(proposal['edited'] or proposal['included'] != proposal['default_included'] for proposal in issue['proposals'])
        if issue['decision'] == 'undecided' and not issue['comment'] and not issue['selected_option_id'] and not changed:
            continue
        count += 1
        choice = (issue['selected_option_label'] or 'No implementation option selected') if issue['decision'] == 'implement' else {'discuss': 'Discuss Further', 'skip': 'Skip (imported earlier review)', 'undecided': 'No option selected'}[issue['decision']]
        lines.extend([f'## {issue["id"]}: {issue["title"]}', '', f'Choice: {choice}'])
        if issue['decision'] != 'implement':
            lines.append({'skip': 'Do not implement this issue.', 'discuss': 'Discuss this issue before implementation.',
                          'undecided': 'No implementation decision has been made.'}[issue['decision']])
        if issue['selected_option_id'] and issue['decision'] != 'implement':
            lines.append(f'Earlier candidate, not approved: {issue["selected_option_label"]} ({issue["selected_option_id"]})')
        if issue['comment']:
            lines.extend(['', 'Comment:', issue['comment']])
        included = [proposal for proposal in issue['proposals'] if proposal['included']]
        targets = Counter(proposal['quote_index'] for proposal in included if proposal['quote_index'] is not None)
        if any(value > 1 for value in targets.values()):
            lines.extend(['', 'REQUIRES CLARIFICATION: more than one included replacement targets the same passage.'])
        if issue['decision'] == 'implement' and not included:
            lines.extend(['', 'REQUIRES CLARIFICATION: the selected revision has no wording included.'])
        if issue['decision'] == 'implement' and issue['options'] and not issue['selected_option_id']:
            lines.extend(['', 'REQUIRES CLARIFICATION: no implementation option has been selected.'])
        for proposal in issue['proposals']:
            if not proposal['included'] and not proposal['edited']:
                continue
            lines.extend(['', f'### {proposal["label"]} ({proposal["id"]})'])
            if not proposal['included']:
                lines.extend(['', 'Excluded from implementation. Retain this user-edited draft for reference.'])
            if issue['decision'] == 'implement' and proposal['included'] and proposal['option_ids'] and issue['selected_option_id'] not in proposal['option_ids']:
                lines.append('REQUIRES CLARIFICATION: this wording is linked to a different option.')
            if proposal['condition']:
                lines.extend(['', 'Prerequisite: ' + proposal['condition']])
            if proposal['current_text'] is not None:
                lines.extend(['', 'Current passage:', proposal['current_text']])
            label = 'User-edited wording:' if proposal['edited'] else 'Proposed wording:'
            if not proposal['included']:
                label = 'Retained user-edited wording — not selected for implementation:'
            elif issue['decision'] != 'implement':
                label = 'Draft wording — not approved for implementation:'
            lines.extend(['', label, proposal['text']])
            if proposal['included'] and not proposal['text'].strip():
                lines.append('REQUIRES CLARIFICATION: included wording is empty; confirm whether deletion is intended.')
        lines.append('')
    if count == 0:
        lines.append('No choices, comments or wording edits have been recorded.')
    return '\n'.join(lines).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('choices', type=Path)
    parser.add_argument('--report', required=True, type=Path, help='Original interactive HTML or report-input JSON')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = validate_decisions(json.loads(args.choices.read_text(encoding='utf-8')), load_manifest(args.report))
    except (ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'Choices were not accepted: {error}\n')
    output = summarize(result)
    if args.output:
        args.output.write_text(output, encoding='utf-8')
    else:
        print(output, end='')


if __name__ == '__main__':
    main()
