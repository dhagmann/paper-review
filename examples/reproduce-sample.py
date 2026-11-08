#!/usr/bin/env python3
"""Reproduce the illustrative report's counts and rates using fictional records."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'assets/example-data.json').read_text())
if data.get('fictional') is not True:
    raise ValueError('This demonstration expects explicitly fictional data.')
outcomes = [row['completed_course'] for row in data['participants']]
if any(value is not None and type(value) is not bool for value in outcomes):
    raise ValueError('Outcomes must be true, false or null.')
completed = sum(value is True for value in outcomes)
not_completed = sum(value is False for value in outcomes)
missing = sum(value is None for value in outcomes)
recruited = len(outcomes)
observed = completed + not_completed
results = {
    'fictional': True,
    'recruited': recruited,
    'observed_outcomes': observed,
    'known_completion': completed,
    'known_noncompletion': not_completed,
    'outcome_missing': missing,
    'observed_outcome_completion_percent': round(100 * completed / observed, 1),
    'documented_completion_among_recruits_percent': round(100 * completed / recruited, 1),
    'known_noncompletion_among_recruits_percent': round(100 * not_completed / recruited, 1),
    'missing_among_recruits_percent': round(100 * missing / recruited, 1),
    'full_cohort_completion_lower_bound_percent': round(100 * completed / recruited, 1),
    'full_cohort_completion_upper_bound_percent': round(100 * (completed + missing) / recruited, 1)
}
print(json.dumps(results, indent=2))
