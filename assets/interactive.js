/* Offline review choices: browser autosave, JSON export/import, plain-text edits. */
(() => {
  'use strict';
  const manifest = JSON.parse(document.getElementById('review-manifest').textContent);
  const format = 'paper-review-decisions';
  const storageKey = 'paper-review:v1:' + manifest.report.id;
  const decisions = ['undecided', 'implement', 'discuss', 'skip'];
  const message = document.getElementById('review-message');
  const issueNodes = new Map([...document.querySelectorAll('article.issue')].map(node => [node.dataset.id, node]));
  const navigation = document.getElementById('issue-navigation');
  const nextUnreviewed = document.getElementById('next-unreviewed');
  const indexNodes = new Map();
  const showAlternatives = new Set();
  const comparisons = new Set();
  navigation.hidden = !manifest.issues.length;
  manifest.issues.forEach((issue, index) => {
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'issue-index-link'; button.dataset.jumpId = issue.id;
    const marker = document.createElement('span');
    marker.className = 'check index-marker'; marker.setAttribute('aria-hidden', 'true');
    const number = document.createElement('span'); number.className = 'index-number'; number.textContent = (index + 1) + '.';
    const title = document.createElement('span'); title.className = 'index-title'; title.textContent = issue.title;
    button.append(marker, number, title);
    button.addEventListener('click', () => jumpToIssue(issue.id));
    document.getElementById('issue-index-list').appendChild(button);
    indexNodes.set(issue.id, button);
  });
  const originalMarkup = new Map();
  for (const [issueId, node] of issueNodes) {
    for (const proposal of node.querySelectorAll('[data-proposal-id]')) {
      originalMarkup.set(issueId + '\n' + proposal.dataset.proposalId, proposal.querySelector('.proposed-text').innerHTML);
    }
  }

  function initialState() {
    return {format, schema_version: 1, report: manifest.report, reviewer: '', exported_at: null, updated_at: null,
      issues: manifest.issues.map(issue => ({id: issue.id, title: issue.title, decision: 'undecided',
        selected_option_id: null, selected_option_label: null, comment: '',
        proposals: issue.proposals.map(proposal => ({...proposal, text: proposal.original_text,
          included: proposal.default_included, edited: false}))}))};
  }

  function validate(payload) {
    if (!payload || payload.format !== format || payload.schema_version !== 1) throw new Error('Not a supported paper-review choices file.');
    if (!payload.report || payload.report.id !== manifest.report.id) throw new Error('These choices belong to a different report version.');
    if ((payload.reviewer != null && typeof payload.reviewer !== 'string') || !Array.isArray(payload.issues)) throw new Error('Invalid issue list or imported reviewer metadata.');
    const incoming = new Map(payload.issues.map(issue => [issue?.id, issue]));
    if (incoming.size !== payload.issues.length || incoming.size !== manifest.issues.length) throw new Error('Issue ids do not match this report.');
    const clean = initialState();
    clean.reviewer = payload.reviewer ?? '';
    clean.exported_at = payload.exported_at;
    clean.updated_at = payload.updated_at;
    for (const issue of clean.issues) {
      const value = incoming.get(issue.id);
      if (!value || !decisions.includes(value.decision) || typeof value.comment !== 'string') throw new Error('Invalid decision or comment for ' + issue.id + '.');
      const meta = manifest.issues.find(item => item.id === issue.id);
      if (value.decision === 'implement' && value.selected_option_id === null && meta.options[0]?.synthetic) {
        value.selected_option_id = meta.options[0].id;
      }
      if (value.selected_option_id !== null && !meta.options.some(option => option.id === value.selected_option_id)) throw new Error('Unknown option for ' + issue.id + '.');
      if (!Array.isArray(value.proposals)) throw new Error('Invalid wording list for ' + issue.id + '.');
      const changes = new Map(value.proposals.map(proposal => [proposal?.id, proposal]));
      if (changes.size !== value.proposals.length || changes.size !== issue.proposals.length) throw new Error('Proposal ids do not match ' + issue.id + '.');
      issue.decision = value.decision;
      issue.comment = value.comment;
      issue.selected_option_id = value.selected_option_id;
      issue.selected_option_label = meta.options.find(option => option.id === value.selected_option_id)?.label ?? null;
      for (const proposal of issue.proposals) {
        const change = changes.get(proposal.id);
        if (!change || change.original_text !== proposal.original_text) throw new Error('Original wording does not match ' + issue.id + '/' + proposal.id + '.');
        if (typeof change.text !== 'string' || typeof change.included !== 'boolean') throw new Error('Invalid edited wording for ' + issue.id + '/' + proposal.id + '.');
        proposal.text = change.text;
        proposal.included = change.included;
        proposal.edited = change.text !== proposal.original_text;
      }
    }
    return clean;
  }

  function announce(text, error = false) {
    message.textContent = text;
    message.dataset.tone = error ? 'error' : 'normal';
  }

  let state = initialState();
  try {
    const cached = localStorage.getItem(storageKey);
    if (cached) {state = validate(JSON.parse(cached)); announce('Restored your choices from this browser. Export choices to share them.');}
  } catch (_) {
    announce('Browser saving is unavailable or the saved review could not be restored. Export choices to keep your edits.');
  }

  function save() {
    state.updated_at = new Date().toISOString();
    try {
      localStorage.setItem(storageKey, JSON.stringify(state));
      announce('Saved in this browser. Export choices to share them.');
    } catch (_) {
      announce('Browser saving is unavailable. Export choices to keep your edits.');
    }
    renderProgress();
  }

  function renderProgress() {
    const count = state.issues.filter(issue => issue.decision !== 'undecided').length;
    document.getElementById('review-progress').textContent = count + ' of ' + state.issues.length + ' reviewed';
    nextUnreviewed.disabled = !state.issues.some(issue => issue.decision === 'undecided');
  }

  function jumpToIssue(id) {
    const node = issueNodes.get(id);
    if (!node) return;
    const toolbar = document.querySelector('.review-toolbar');
    const top = window.scrollY + node.getBoundingClientRect().top - toolbar.getBoundingClientRect().height - 20;
    window.scrollTo({top: Math.max(0, top), behavior: 'instant'});
    node.querySelector('h2').focus({preventScroll: true});
  }

  function renderWordingFocus(issue) {
    const node = issueNodes.get(issue.id);
    const unused = issue.proposals.filter(proposal => issue.decision === 'implement' &&
      proposal.option_ids.length && !proposal.option_ids.includes(issue.selected_option_id) && !proposal.included);
    const unusedIds = new Set(unused.map(proposal => proposal.id));
    for (const group of node.querySelectorAll('.proposal-group')) {
      const proposal = issue.proposals.find(item => item.id === group.dataset.groupId);
      group.hidden = unusedIds.has(proposal.id) && !showAlternatives.has(issue.id);
      group.classList.toggle('side-by-side', comparisons.has(issue.id) && proposal.current_text !== null);
    }
    const alternatives = node.querySelector('.show-alternatives');
    alternatives.hidden = !unused.length;
    alternatives.textContent = showAlternatives.has(issue.id) ? 'Hide other alternatives' : 'Show ' + unused.length + ' other alternative' + (unused.length === 1 ? '' : 's');
    alternatives.setAttribute('aria-expanded', String(showAlternatives.has(issue.id)));
    const compare = node.querySelector('.compare-wording');
    compare.hidden = !issue.proposals.some(proposal => proposal.current_text !== null);
    compare.setAttribute('aria-pressed', String(comparisons.has(issue.id)));
    compare.textContent = comparisons.has(issue.id) ? 'Exit comparison' : 'Compare side by side';
    const note = node.querySelector('.wording-focus-note');
    if (unused.length) note.textContent = showAlternatives.has(issue.id) ? 'All alternatives are shown. Only included wording belongs to your selected revision.' : 'Showing common changes and your selected wording. Other alternatives are folded.';
    else if (issue.decision === 'discuss' || issue.decision === 'skip') note.textContent = 'All proposed wording is shown for discussion.';
    else note.textContent = '';
  }

  function renderIssue(issue) {
    const node = issueNodes.get(issue.id);
    const discussing = issue.decision === 'discuss' || issue.decision === 'skip';
    const implementing = issue.decision === 'implement' && Boolean(issue.selected_option_id);
    const marker = node.querySelector('.check');
    marker.dataset.state = discussing ? 'discuss' : implementing ? 'selected' : 'pending';
    marker.textContent = discussing ? '?' : implementing ? '✓' : '';
    marker.setAttribute('aria-label', discussing ? 'Discuss Further' : implementing ? 'Selected option: ' + issue.selected_option_label : 'No option selected');
    const indexButton = indexNodes.get(issue.id);
    const indexMarker = indexButton.querySelector('.index-marker');
    indexMarker.textContent = marker.textContent; indexMarker.dataset.state = marker.dataset.state;
    indexButton.setAttribute('aria-label', 'Issue ' + (manifest.issues.findIndex(item => item.id === issue.id) + 1) + ', ' + issue.title + '. ' + marker.getAttribute('aria-label'));
    node.querySelector('.discussion-radio').checked = discussing;
    node.querySelector('.discussion-option').classList.toggle('selected', discussing);
    node.querySelector('.discussion-details').hidden = !discussing;
    const legacyNote = node.querySelector('.legacy-decision-note');
    legacyNote.hidden = issue.decision !== 'skip';
    legacyNote.textContent = issue.decision === 'skip' ? 'This imported review was marked Skip; no revision is approved.' : '';
    const comment = node.querySelector('.issue-comment');
    if (comment.value !== issue.comment) comment.value = issue.comment;
    for (const option of node.querySelectorAll('[data-option-id]')) {
      const selected = issue.decision === 'implement' && issue.selected_option_id === option.dataset.optionId;
      option.classList.toggle('selected', selected);
      option.querySelector('.option-radio').checked = selected;
    }
    for (const proposalNode of node.querySelectorAll('[data-proposal-id]')) {
      const proposal = issue.proposals.find(item => item.id === proposalNode.dataset.proposalId);
      proposalNode.querySelector('.include-wording').checked = proposal.included;
      const editor = proposalNode.querySelector('.wording-editor');
      if (editor.value !== proposal.text) editor.value = proposal.text;
      const view = proposalNode.querySelector('.proposed-text');
      if (proposal.edited) {
        const addition = document.createElement('ins');
        addition.textContent = proposal.text;
        view.replaceChildren(addition);
      } else {
        // This markup was escaped by the renderer and captured before any user edits.
        view.innerHTML = originalMarkup.get(issue.id + '\n' + proposal.id);
      }
      proposalNode.querySelector('.wording-state').textContent = proposal.edited ? 'Edited' : '';
      proposalNode.querySelector('.restore-wording').hidden = !proposal.edited;
    }
    const conflicts = [];
    const included = issue.proposals.filter(proposal => proposal.included);
    const targets = new Set();
    for (const proposal of included) {
      if (proposal.quote_index !== null && targets.has(proposal.quote_index)) conflicts.push('Two included replacements target the same passage. Choose one or explain the combination in your comment.');
      targets.add(proposal.quote_index);
      if (issue.decision === 'implement' && proposal.option_ids.length && !proposal.option_ids.includes(issue.selected_option_id)) conflicts.push('Included wording belongs to a different option. Check your selection.');
      if (!proposal.text.trim()) conflicts.push('Included wording is empty. Clarify whether you intend to delete the passage.');
    }
    const meta = manifest.issues.find(item => item.id === issue.id);
    if (issue.decision === 'implement' && meta.options.length && !issue.selected_option_id) conflicts.push('Choose an implementation option or explain your preference in the comment.');
    if (issue.decision === 'implement' && !included.length) conflicts.push('No proposed wording is included. Mark the wording you want or describe the change in your comment.');
    const alert = node.querySelector('.issue-conflicts');
    alert.textContent = [...new Set(conflicts)].join(' ');
    alert.hidden = !conflicts.length;
    const printNote = node.querySelector('.review-print-note');
    const notes = [];
    if (issue.decision === 'discuss') notes.push('Selected option: Discuss Further');
    else if (issue.decision === 'skip') notes.push('Imported review: Skip; no revision approved.');
    else if (issue.decision === 'implement' && issue.selected_option_label) notes.push('Selected option: ' + issue.selected_option_label);
    if (issue.comment) notes.push('Comment: ' + issue.comment);
    if (conflicts.length) notes.push('Needs clarification: ' + [...new Set(conflicts)].join(' '));
    printNote.textContent = notes.join('\n');
    renderWordingFocus(issue);
  }

  function renderAll() {
    state.issues.forEach(renderIssue);
    renderProgress();
  }

  for (const [id, node] of issueNodes) {
    const current = () => state.issues.find(issue => issue.id === id);
    node.querySelector('.show-alternatives').addEventListener('click', () => {
      if (showAlternatives.has(id)) showAlternatives.delete(id); else showAlternatives.add(id);
      renderWordingFocus(current());
    });
    node.querySelector('.compare-wording').addEventListener('click', () => {
      if (comparisons.has(id)) comparisons.delete(id); else comparisons.add(id);
      renderWordingFocus(current());
    });
    node.querySelector('.discussion-radio').addEventListener('change', () => {
      const issue = current(); issue.decision = 'discuss';
      issue.selected_option_id = null; issue.selected_option_label = null;
      renderIssue(issue); save(); node.querySelector('.issue-comment').focus();
    });
    node.querySelector('.issue-comment').addEventListener('input', event => {
      const issue = current(); issue.comment = event.target.value; renderIssue(issue); save();
    });
    for (const optionNode of node.querySelectorAll('[data-option-id]')) {
      optionNode.querySelector('.option-radio').addEventListener('change', () => {
        const issue = current();
        issue.selected_option_id = optionNode.dataset.optionId;
        issue.selected_option_label = manifest.issues.find(item => item.id === id).options.find(option => option.id === issue.selected_option_id).label;
        issue.decision = 'implement';
        showAlternatives.delete(id);
        for (const proposal of issue.proposals) {
          if (proposal.option_ids.length) proposal.included = proposal.option_ids.includes(issue.selected_option_id);
        }
        renderIssue(issue); save();
      });
    }
    node.querySelector('.clear-option')?.addEventListener('click', () => {
      const issue = current(); issue.decision = 'undecided'; issue.selected_option_id = null; issue.selected_option_label = null;
      for (const proposal of issue.proposals) if (proposal.option_ids.length) proposal.included = false;
      renderIssue(issue); save();
    });
    for (const proposalNode of node.querySelectorAll('[data-proposal-id]')) {
      const change = () => current().proposals.find(item => item.id === proposalNode.dataset.proposalId);
      const editor = proposalNode.querySelector('.wording-editor');
      const view = proposalNode.querySelector('.proposed-text');
      const editButton = proposalNode.querySelector('.edit-wording');
      proposalNode.querySelector('.include-wording').addEventListener('change', event => {
        change().included = event.target.checked; renderIssue(current()); save();
      });
      editButton.addEventListener('click', () => {
        const opening = editor.hidden;
        editor.hidden = !opening; view.hidden = opening;
        editButton.textContent = opening ? 'Done editing' : 'Edit wording';
        editButton.setAttribute('aria-expanded', String(opening));
        if (opening) {editor.style.height = Math.max(90, editor.scrollHeight + 3) + 'px'; editor.focus();}
      });
      editor.addEventListener('input', () => {
        const proposal = change(); proposal.text = editor.value; proposal.edited = editor.value !== proposal.original_text;
        editor.style.height = 'auto'; editor.style.height = Math.max(90, editor.scrollHeight + 3) + 'px';
        renderIssue(current()); save();
      });
      proposalNode.querySelector('.restore-wording').addEventListener('click', () => {
        const proposal = change(); proposal.text = proposal.original_text; proposal.edited = false;
        renderIssue(current()); save();
      });
    }
  }
  nextUnreviewed.addEventListener('click', () => {
    const boundary = document.querySelector('.review-toolbar').getBoundingClientRect().bottom + 24;
    let currentIndex = -1;
    state.issues.forEach((issue, index) => {
      if (issueNodes.get(issue.id).getBoundingClientRect().top <= boundary) currentIndex = index;
    });
    for (let offset = 1; offset <= state.issues.length; offset++) {
      const index = (currentIndex + offset) % state.issues.length;
      if (state.issues[index].decision === 'undecided') {jumpToIssue(state.issues[index].id); break;}
    }
  });
  document.getElementById('export-choices').addEventListener('click', () => {
    state.exported_at = new Date().toISOString();
    const url = URL.createObjectURL(new Blob([JSON.stringify(state, null, 2) + '\n'], {type: 'application/json'}));
    const link = document.createElement('a');
    link.href = url; link.download = manifest.download_basename + '-choices.json';
    document.body.appendChild(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    announce('Choices exported. Send the JSON file with this report to Codex or Claude.');
  });
  const importFile = document.getElementById('import-file');
  document.getElementById('import-choices').addEventListener('click', () => importFile.click());
  importFile.addEventListener('change', async () => {
    const file = importFile.files[0];
    if (!file) return;
    try {
      const incoming = validate(JSON.parse(await file.text()));
      if (state.issues.some(issue => issue.comment || issue.decision !== 'undecided' || issue.selected_option_id || issue.proposals.some(proposal => proposal.edited || proposal.included !== proposal.default_included)) &&
          !window.confirm('Replace the choices, comments and wording currently shown with this imported review?')) return;
      state = incoming; renderAll(); save(); announce('Choices imported. You can continue reviewing or export them again.');
    } catch (error) {announce('Could not import choices: ' + error.message, true);}
    finally {importFile.value = '';}
  });
  document.getElementById('print-review').addEventListener('click', () => window.print());
  renderAll();
  document.documentElement.classList.add('review-ready');
})();
