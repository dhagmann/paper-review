"""Shared report identities and decision-file validation; no manuscript mutation."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

FORMAT = 'paper-review-decisions'
VERSION = 1
DECISIONS = ('undecided', 'implement', 'discuss', 'skip')


def report_id(report):
    canonical = json.dumps(report, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return 'sha256:' + hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def manifest_for(report, basename='paper-review'):
    result = {'schema_version': VERSION, 'report': {'id': report_id(report), 'title': report['title']},
              'download_basename': basename, 'issues': []}
    issue_ids = set()
    for issue in report['issues']:
        identifier = issue['id']
        if not isinstance(identifier, str) or not identifier or identifier in issue_ids:
            raise ValueError('Issue ids must be nonempty, unique strings.')
        issue_ids.add(identifier)
        options = [{'id': option.get('id', f'option-{index}'), 'label': option['label']}
                   for index, option in enumerate(issue.get('options', []), 1)]
        if not options:
            options = [{'id': '__apply_revision__', 'label': 'Apply proposed revision', 'synthetic': True}]
        option_ids = [option['id'] for option in options]
        if any(not isinstance(value, str) or not value for value in option_ids) or len(set(option_ids)) != len(option_ids):
            raise ValueError(f'Option ids must be nonempty and unique in {identifier}.')
        changes = []
        for kind, entries in [('edit', issue.get('edits', [])), ('insertion', issue.get('insertions', []))]:
            for index, change in enumerate(entries, 1):
                quote_index = change.get('quote')
                if kind == 'edit' and (type(quote_index) is not int or quote_index < 0 or quote_index >= len(issue['quotes'])):
                    raise ValueError(f'Invalid proposal quotation in {identifier}.')
                applies_to = change.get('option_ids', [])
                if not isinstance(applies_to, list) or any(value not in option_ids for value in applies_to):
                    raise ValueError(f'Unknown proposal option_ids in {identifier}.')
                current = issue['quotes'][quote_index]['text'] if kind == 'edit' else None
                alternative = kind == 'edit' and sum(entry.get('quote') == quote_index for entry in issue.get('edits', [])) > 1
                changes.append({'id': change.get('id', f'{kind}-{index}'), 'label': change['label'],
                                'quote_index': quote_index, 'current_text': current,
                                'condition': change.get('condition', ''), 'option_ids': applies_to,
                                'original_text': change['text'],
                                'default_included': not applies_to and not alternative,
                                'requires_selection': alternative and not applies_to})
        proposal_ids = [change['id'] for change in changes]
        if any(not isinstance(value, str) or not value for value in proposal_ids) or len(set(proposal_ids)) != len(proposal_ids):
            raise ValueError(f'Proposal ids must be nonempty and unique in {identifier}.')
        result['issues'].append({'id': identifier, 'title': issue['title'], 'options': options, 'proposals': changes})
    return result


def validate_decisions(payload, manifest):
    """Return canonical metadata plus editable fields, rejecting stale identities."""
    if not isinstance(payload, dict) or payload.get('format') != FORMAT or type(payload.get('schema_version')) is not int or payload['schema_version'] != VERSION:
        raise ValueError('Not a supported paper-review choices file.')
    if not isinstance(payload.get('report'), dict) or payload['report'].get('id') != manifest['report']['id']:
        raise ValueError('These choices belong to a different report version.')
    reviewer = payload.get('reviewer', '')
    if not isinstance(reviewer, str):
        raise ValueError('Reviewer name must be text.')
    incoming = payload.get('issues')
    if not isinstance(incoming, list) or any(not isinstance(issue, dict) for issue in incoming):
        raise ValueError('Choices must contain a list of issues.')
    incoming_ids = [issue.get('id') for issue in incoming]
    if any(not isinstance(value, str) for value in incoming_ids) or len(set(incoming_ids)) != len(incoming_ids) or set(incoming_ids) != {issue['id'] for issue in manifest['issues']}:
        raise ValueError('Issue ids do not match this report.')
    by_id = {issue['id']: issue for issue in incoming}
    normalized = {'format': FORMAT, 'schema_version': VERSION, 'report': manifest['report'],
                  'reviewer': reviewer, 'exported_at': payload.get('exported_at'), 'issues': []}
    for original in manifest['issues']:
        if not original['options']:
            original = {**original, 'options': [{'id': '__apply_revision__', 'label': 'Apply proposed revision', 'synthetic': True}]}
        item = by_id[original['id']]
        decision, selected, comment = item.get('decision'), item.get('selected_option_id'), item.get('comment', '')
        if decision not in DECISIONS or not isinstance(comment, str):
            raise ValueError(f'Invalid decision or comment for {original["id"]}.')
        valid_options = {option['id']: option['label'] for option in original['options']}
        if decision == 'implement' and selected is None and original['options'][0].get('synthetic'):
            selected = original['options'][0]['id']
        if selected is not None and (not isinstance(selected, str) or selected not in valid_options):
            raise ValueError(f'Unknown option for {original["id"]}.')
        proposed = item.get('proposals')
        if not isinstance(proposed, list) or any(not isinstance(change, dict) for change in proposed):
            raise ValueError(f'Invalid proposed wording for {original["id"]}.')
        ids = [change.get('id') for change in proposed]
        if any(not isinstance(value, str) for value in ids) or len(set(ids)) != len(ids) or set(ids) != {change['id'] for change in original['proposals']}:
            raise ValueError(f'Proposal ids do not match {original["id"]}.')
        changes = {change['id']: change for change in proposed}
        cleaned = []
        for base in original['proposals']:
            change = changes[base['id']]
            if change.get('original_text') != base['original_text']:
                raise ValueError(f'Original proposal text does not match {original["id"]}/{base["id"]}.')
            if not isinstance(change.get('text'), str) or type(change.get('included')) is not bool:
                raise ValueError(f'Invalid edited wording for {original["id"]}/{base["id"]}.')
            cleaned.append({**base, 'text': change['text'], 'included': change['included'],
                            'edited': change['text'] != base['original_text']})
        normalized['issues'].append({'id': original['id'], 'title': original['title'], 'options': original['options'], 'decision': decision,
                                     'selected_option_id': selected, 'selected_option_label': valid_options.get(selected),
                                     'comment': comment, 'proposals': cleaned})
    return normalized


class ManifestParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('id') == 'review-manifest':
            self.inside = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.parts.append(data)


def load_manifest(path):
    path = Path(path)
    if path.suffix.lower() in ('.html', '.htm'):
        parser = ManifestParser()
        parser.feed(path.read_text(encoding='utf-8'))
        if not parser.parts:
            raise ValueError('This HTML report has no interactive review manifest.')
        return json.loads(''.join(parser.parts))
    return manifest_for(json.loads(path.read_text(encoding='utf-8')))
