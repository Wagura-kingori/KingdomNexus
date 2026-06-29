/* ============================================================
   Scholaris — Timetable Setup JS
   Handles: add/remove rows, LPW controls, toggles,
            duration calc, AJAX teacher load, conflict detection,
            totals, toast notifications
   ============================================================ */

(function () {
  'use strict';

  /* ── Cached elements ──────────────────────────────────── */
  const breakTbody      = document.getElementById('break-tbody');
  const subjectTbody    = document.getElementById('subject-tbody');
  const breakTotalInput = document.getElementById('id_breaks-TOTAL_FORMS');
  const subjTotalInput  = document.getElementById('id_subject_configs-TOTAL_FORMS');

  /* ── Toast helper ─────────────────────────────────────── */
  function toast(message, type = 'success', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const icons = {
      success: '<svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>',
      error:   '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
      info:    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    };

    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.innerHTML = (icons[type] || '') + message;
    container.appendChild(el);
    setTimeout(() => el.remove(), duration);
  }

  /* ── Duration calculator ──────────────────────────────── */
  function calcDuration(start, end) {
    if (!start || !end) return '—';
    const [sh, sm] = start.split(':').map(Number);
    const [eh, em] = end.split(':').map(Number);
    if (isNaN(sh) || isNaN(eh)) return '—';
    const diff = (eh * 60 + em) - (sh * 60 + sm);
    if (diff <= 0) return 'Invalid';
    return `${diff} min`;
  }

  function refreshBreakDurations() {
    if (!breakTbody) return;
    breakTbody.querySelectorAll('tr.break-row').forEach(row => {
      const startInput = row.querySelector('input[name*="start_time"], input[name*="start"]');
      const endInput   = row.querySelector('input[name*="end_time"],   input[name*="end"]');
      const badge      = row.querySelector('.duration-badge');
      if (!badge || !startInput || !endInput) return;
      const d = calcDuration(startInput.value, endInput.value);
      badge.textContent = d;
      badge.classList.toggle('invalid', d === 'Invalid' || d === '—');
    });
  }

  /* ── Lessons per week controls ────────────────────────── */
  function bindLpwRow(row) {
    const dec    = row.querySelector('.lpw-btn.dec');
    const inc    = row.querySelector('.lpw-btn.inc');
    const valEl  = row.querySelector('.lpw-val');
    const hidden = row.querySelector('.lpw-hidden');
    if (!dec || !inc || !valEl || !hidden) return;

    function update(delta) {
      let v = parseInt(hidden.value) || 2;
      v = Math.min(10, Math.max(1, v + delta));
      hidden.value   = v;
      valEl.textContent = v;
      refreshTotals();
    }

    dec.addEventListener('click', () => update(-1));
    inc.addEventListener('click', () => update(+1));
  }

  /* ── Fixed toggle ─────────────────────────────────────── */
  function bindFixedToggle(row) {
    const chk    = row.querySelector('.is-fixed-chk');
    const lock   = row.querySelector('.lock-icon');
    const daySel = row.querySelector('select[name*="fixed_day"]');
    const timInp = row.querySelector('input[name*="fixed_start_time"]');
    if (!chk) return;

    function sync() {
      const on = chk.checked;
      if (lock) {
        lock.classList.toggle('locked',   on);
        lock.classList.toggle('unlocked', !on);
      }
      if (daySel) daySel.disabled = !on;
      if (timInp) timInp.disabled = !on;
    }

    chk.addEventListener('change', () => {
      sync();
      refreshTotals();
      detectConflicts();
    });

    sync();
  }

  /* ── Header chips & tfoot totals ──────────────────────── */
  function refreshTotals() {
    if (!subjectTbody) return;

    let totalLessons = 0;
    let fixedCount   = 0;
    let subjCount    = 0;
    let unassigned   = 0;

    subjectTbody.querySelectorAll('tr.subject-row').forEach(row => {
      const delChk = row.querySelector('input[type="checkbox"][name*="DELETE"]');
      if (delChk && delChk.checked) return;

      subjCount++;

      const hidden  = row.querySelector('.lpw-hidden');
      const fixChk  = row.querySelector('.is-fixed-chk');
      const subSel  = row.querySelector('select[name*="-subject"]');
      const tchSel  = row.querySelector('select[name*="teacher_assignment"]');

      if (hidden) totalLessons += parseInt(hidden.value) || 0;
      if (fixChk && fixChk.checked) fixedCount++;
      if (subSel && subSel.value && tchSel && !tchSel.value) unassigned++;
    });

    /* ─ tfoot ─ */
    const tfCount   = document.getElementById('tfoot-subj-count');
    const tfLessons = document.getElementById('tfoot-lessons');
    const tfFixed   = document.getElementById('tfoot-fixed');
    const tfFixedPl = document.getElementById('tfoot-fixed-pl');

    if (tfCount)   tfCount.textContent   = subjCount;
    if (tfLessons) tfLessons.textContent = totalLessons;
    if (tfFixed)   tfFixed.textContent   = fixedCount;
    if (tfFixedPl) tfFixedPl.textContent = fixedCount !== 1 ? 's' : '';

    /* ─ header chips ─ */
    const chipLessons   = document.getElementById('chip-lessons');
    const chipUnassign  = document.getElementById('chip-unassigned');
    const chipConflict  = document.getElementById('chip-conflicts');
    const subjCountEl   = document.getElementById('header-subj-count');

    if (chipLessons) chipLessons.textContent = `${totalLessons} lessons/week`;
    if (subjCountEl) subjCountEl.textContent =
      `${subjCount} subject${subjCount !== 1 ? 's' : ''} · ${totalLessons} lessons/week`;

    if (chipUnassign) {
      chipUnassign.style.display = unassigned > 0 ? 'flex' : 'none';
      const ua = chipUnassign.querySelector('span');
      if (ua) ua.textContent = `${unassigned} unassigned`;
    }
  }

  /* ── Conflict detection ───────────────────────────────── */
  function detectConflicts() {
    if (!subjectTbody) return;

    const map    = new Map();
    const issues = [];

    subjectTbody.querySelectorAll('tr.subject-row').forEach(row => {
      const delChk = row.querySelector('input[type="checkbox"][name*="DELETE"]');
      if (delChk && delChk.checked) return;

      const fixChk = row.querySelector('.is-fixed-chk');
      if (!fixChk || !fixChk.checked) return;

      const subSel = row.querySelector('select[name*="-subject"]');
      const daySel = row.querySelector('select[name*="fixed_day"]');
      const timInp = row.querySelector('input[name*="fixed_start_time"]');

      if (!daySel || !timInp || !daySel.value || !timInp.value) return;

      const key     = `${daySel.value}|${timInp.value}`;
      const subjTxt = subSel ? (subSel.options[subSel.selectedIndex]?.text || '?') : '?';

      if (map.has(key)) {
        issues.push(
          `Time conflict: "${map.get(key)}" and "${subjTxt}" both fixed on ${daySel.value} at ${timInp.value}`
        );
      } else {
        map.set(key, subjTxt);
      }
    });

    /* Update conflict banner */
    const banner   = document.getElementById('conflict-banner');
    const cbTitle  = document.getElementById('cb-title');
    const cbList   = document.getElementById('cb-list');
    const chipConf = document.getElementById('chip-conflicts');
    const genBtn   = document.getElementById('generate-btn');
    const saveHint = document.getElementById('save-conflict-hint');

    const hasConflicts = issues.length > 0;

    if (banner) {
      banner.style.display = hasConflicts ? 'flex' : 'none';
      if (hasConflicts && cbTitle) {
        cbTitle.textContent = `${issues.length} scheduling conflict${issues.length > 1 ? 's' : ''} detected`;
      }
      if (hasConflicts && cbList) {
        cbList.innerHTML = issues.map(c => `<div class="cb-item">· ${c}</div>`).join('');
      }
    }

    if (chipConf) {
      chipConf.style.display = hasConflicts ? 'flex' : 'none';
      const cs = chipConf.querySelector('span');
      if (cs) cs.textContent = `${issues.length} conflict${issues.length > 1 ? 's' : ''}`;
    }

    if (genBtn)   genBtn.disabled   = hasConflicts;
    if (saveHint) saveHint.style.display = hasConflicts ? 'flex' : 'none';
  }

  /* ── Sync break table visibility ─────────────────────── */
  function syncBreakVisibility() {
    if (!breakTbody) return;

    const visible = breakTbody.querySelectorAll('tr.break-row:not([style*="display: none"])').length;
    const emptyEl = document.getElementById('break-empty');
    const tableEl = document.getElementById('break-table-wrap');
    const footEl  = document.getElementById('break-table-footer');
    const countEl = document.getElementById('break-count');

    if (emptyEl)  emptyEl.style.display  = visible === 0 ? 'flex' : 'none';
    if (tableEl)  tableEl.style.display  = visible === 0 ? 'none' : '';
    if (footEl)   footEl.style.display   = visible === 0 ? 'none' : '';
    if (countEl)  countEl.textContent    = `${visible} break${visible !== 1 ? 's' : ''} configured`;
  }

  /* ── Sync subject table visibility ───────────────────── */
  function syncSubjectVisibility() {
    if (!subjectTbody) return;

    const visible = subjectTbody.querySelectorAll('tr.subject-row:not([style*="display: none"])').length;
    const emptyEl = document.getElementById('subject-empty');
    const tableEl = document.getElementById('subject-table-wrap');
    const footEl  = document.getElementById('subject-table-footer');

    if (emptyEl) emptyEl.style.display  = visible === 0 ? 'flex' : 'none';
    if (tableEl) tableEl.style.display  = visible === 0 ? 'none' : '';
    if (footEl)  footEl.style.display   = visible === 0 ? 'none' : '';
  }

  /* ── Add break row ────────────────────────────────────── */
  function addBreakRow() {
    if (!breakTotalInput || !breakTbody) return;

    const i  = parseInt(breakTotalInput.value);
    const tr = document.createElement('tr');
    tr.className = 'break-row';

    tr.innerHTML = `
      <td class="drag-handle" title="Drag to reorder">
        <svg viewBox="0 0 24 24" fill="none">
          <circle cx="9"  cy="7"  r="1.2" fill="currentColor"/>
          <circle cx="15" cy="7"  r="1.2" fill="currentColor"/>
          <circle cx="9"  cy="12" r="1.2" fill="currentColor"/>
          <circle cx="15" cy="12" r="1.2" fill="currentColor"/>
          <circle cx="9"  cy="17" r="1.2" fill="currentColor"/>
          <circle cx="15" cy="17" r="1.2" fill="currentColor"/>
        </svg>
      </td>
      <td>
        <input type="text" name="breaks-${i}-name" placeholder="e.g. Morning Break">
      </td>
      <td>
        <input type="time" name="breaks-${i}-start_time" class="time-start">
      </td>
      <td>
        <input type="time" name="breaks-${i}-end_time" class="time-end">
      </td>
      <td class="duration-cell">
        <span class="duration-badge">—</span>
      </td>
      <td class="center-cell">
        <input type="checkbox" name="breaks-${i}-DELETE" style="display:none">
        <button type="button" class="btn-icon del-break-btn" title="Remove break">
          <svg viewBox="0 0 24 24">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            <path d="M10 11v6"/><path d="M14 11v6"/>
          </svg>
        </button>
      </td>`;

    breakTbody.appendChild(tr);
    breakTotalInput.value = i + 1;

    /* Bind time → duration */
    tr.querySelector('.time-start').addEventListener('change', refreshBreakDurations);
    tr.querySelector('.time-end').addEventListener('change',   refreshBreakDurations);

    syncBreakVisibility();
    tr.querySelector('input[type="text"]').focus();
  }

  /* ── Delete break row ─────────────────────────────────── */
  function deleteBreakRow(row) {
    const delChk = row.querySelector('input[type="checkbox"][name*="DELETE"]');

    if (delChk && delChk.name.includes('breaks-')) {
      /* Django formset row → mark for deletion */
      delChk.checked = true;
    }

    row.style.transition = 'opacity .2s, max-height .2s';
    row.style.opacity    = '0';
    setTimeout(() => {
      row.style.display = 'none';
      syncBreakVisibility();
      refreshBreakDurations();
    }, 200);
  }

  /* ── Build subject options HTML ───────────────────────── */
  function buildSubjectOptions() {
    /* Grab from existing Django-rendered select in the formset */
    const existingSel = document.querySelector(
      'select[name*="subject_configs"][name$="-subject"]'
    );
    if (!existingSel) return '<option value="">— Select subject —</option>';

    let opts = '<option value="">— Select subject —</option>';
    Array.from(existingSel.options).forEach(o => {
      if (o.value) opts += `<option value="${o.value}">${o.text}</option>`;
    });
    return opts;
  }

  /* ── Add subject row ──────────────────────────────────── */
  function addSubjectRow() {
    if (!subjTotalInput || !subjectTbody) return;

    const i    = parseInt(subjTotalInput.value);
    const tr   = document.createElement('tr');
    tr.className = 'subject-row';

    const subjectOpts = buildSubjectOptions();

    tr.innerHTML = `
      <td class="drag-handle" title="Drag to reorder">
        <svg viewBox="0 0 24 24" fill="none">
          <circle cx="9"  cy="7"  r="1.2" fill="currentColor"/>
          <circle cx="15" cy="7"  r="1.2" fill="currentColor"/>
          <circle cx="9"  cy="12" r="1.2" fill="currentColor"/>
          <circle cx="15" cy="12" r="1.2" fill="currentColor"/>
          <circle cx="9"  cy="17" r="1.2" fill="currentColor"/>
          <circle cx="15" cy="17" r="1.2" fill="currentColor"/>
        </svg>
      </td>
      <td>
        <select name="subject_configs-${i}-subject">
          ${subjectOpts}
        </select>
      </td>
      <td>
        <select name="subject_configs-${i}-teacher_assignment" disabled>
          <option value="">Select subject first</option>
        </select>
      </td>
      <td>
        <div class="lpw">
          <button type="button" class="lpw-btn dec" tabindex="-1">−</button>
          <input type="hidden" name="subject_configs-${i}-lessons_per_week" value="2" class="lpw-hidden">
          <span class="lpw-val">2</span>
          <button type="button" class="lpw-btn inc" tabindex="-1">+</button>
        </div>
      </td>
      <td>
        <div class="toggle-cell">
          <svg class="lock-icon unlocked" viewBox="0 0 24 24" fill="none" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          <label class="toggle">
            <input type="checkbox"
                   name="subject_configs-${i}-is_fixed"
                   id="id_subject_configs-${i}-is_fixed"
                   class="is-fixed-chk">
            <span class="toggle-slider"></span>
          </label>
        </div>
      </td>
      <td>
        <select name="subject_configs-${i}-fixed_day" disabled>
          <option value="">— Any —</option>
          <option>Monday</option>
          <option>Tuesday</option>
          <option>Wednesday</option>
          <option>Thursday</option>
          <option>Friday</option>
        </select>
      </td>
      <td>
        <input type="time"
               name="subject_configs-${i}-fixed_start_time"
               disabled>
      </td>
      <td class="center-cell">
        <input type="checkbox" name="subject_configs-${i}-DELETE" style="display:none">
        <button type="button" class="btn-icon del-subject-btn" title="Remove subject">
          <svg viewBox="0 0 24 24">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            <path d="M10 11v6"/><path d="M14 11v6"/>
          </svg>
        </button>
      </td>`;

    subjectTbody.appendChild(tr);
    subjTotalInput.value = i + 1;

    bindLpwRow(tr);
    bindFixedToggle(tr);
    syncSubjectVisibility();
    refreshTotals();
  }

  /* ── Delete subject row ───────────────────────────────── */
  function deleteSubjectRow(row) {
    const delChk = row.querySelector('input[type="checkbox"][name*="DELETE"]');

    if (delChk && delChk.name.includes('subject_configs-')) {
      delChk.checked = true;
    }

    row.style.transition = 'opacity .2s';
    row.style.opacity    = '0';
    setTimeout(() => {
      row.style.display = 'none';
      syncSubjectVisibility();
      refreshTotals();
      detectConflicts();
    }, 200);
  }

  /* ── Subject → Teacher AJAX ───────────────────────────── */
  function loadTeachersForSubject(subjectId, teacherSel) {
    teacherSel.innerHTML = '<option>Loading…</option>';
    teacherSel.disabled  = true;

    fetch(`/timetable/ajax/teachers/?subject_id=${subjectId}`)
      .then(r => r.json())
      .then(data => {
        if (!data.length) {
          teacherSel.innerHTML = '<option value="">No teachers found</option>';
          teacherSel.disabled  = false;
          return;
        }
        teacherSel.innerHTML = '<option value="">— Assign teacher —</option>';
        data.forEach(t => {
          const o = document.createElement('option');
          o.value = t.id;
          o.textContent = t.name;
          teacherSel.appendChild(o);
        });
        teacherSel.disabled = false;
      })
      .catch(() => {
        teacherSel.innerHTML = '<option value="">Error loading</option>';
        teacherSel.disabled  = false;
      });
  }

  /* ── Event delegation ─────────────────────────────────── */

  /* Break tbody clicks */
  if (breakTbody) {
    breakTbody.addEventListener('click', e => {
      const btn = e.target.closest('.del-break-btn');
      if (btn) deleteBreakRow(btn.closest('tr'));
    });

    breakTbody.addEventListener('change', e => {
      const name = e.target.name || '';
      if (name.includes('start_time') || name.includes('end_time')) {
        refreshBreakDurations();
      }
    });
  }

  /* Subject tbody clicks & changes */
  if (subjectTbody) {
    subjectTbody.addEventListener('click', e => {
      const btn = e.target.closest('.del-subject-btn');
      if (btn) deleteSubjectRow(btn.closest('tr'));
    });

    subjectTbody.addEventListener('change', e => {
      const name = e.target.name || '';

      /* Subject select → reload teachers */
      if (e.target.tagName === 'SELECT' && /subject_configs-\d+-subject$/.test(name)) {
        const row        = e.target.closest('tr');
        const teacherSel = row.querySelector('select[name*="teacher_assignment"]');
        if (teacherSel && e.target.value) {
          loadTeachersForSubject(e.target.value, teacherSel);
        } else if (teacherSel) {
          teacherSel.innerHTML = '<option value="">Select subject first</option>';
          teacherSel.disabled  = true;
        }
      }

      /* Teacher change → refresh totals (unassigned chip) */
      if (name.includes('teacher_assignment')) {
        refreshTotals();
      }

      /* Fixed day / time change → re-detect conflicts */
      if (name.includes('fixed_day') || name.includes('fixed_start_time')) {
        detectConflicts();
      }
    });
  }

  /* Add break buttons */
  ['add-break-row', 'add-break-row-empty', 'add-break-row-footer'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', addBreakRow);
  });

  /* Also support class-based add-break buttons */
  document.querySelectorAll('.add-break-btn').forEach(btn =>
    btn.addEventListener('click', addBreakRow)
  );

  /* Add subject buttons */
  ['add-subject-row', 'add-subject-row-empty', 'add-subject-row-footer'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', addSubjectRow);
  });

  document.querySelectorAll('.add-subject-btn').forEach(btn =>
    btn.addEventListener('click', addSubjectRow)
  );

  /* ── Init existing rows ───────────────────────────────── */
  if (subjectTbody) {
    subjectTbody.querySelectorAll('tr.subject-row').forEach(row => {
      bindLpwRow(row);
      bindFixedToggle(row);
    });
  }

  /* Bind duration on existing break rows */
  if (breakTbody) {
    breakTbody.querySelectorAll('tr.break-row').forEach(row => {
      row.querySelectorAll('input[name*="start_time"], input[name*="end_time"]').forEach(inp =>
        inp.addEventListener('change', refreshBreakDurations)
      );
    });
    refreshBreakDurations();
  }

  /* ── Save badge update if Django reported success ───── */
  const saveBadge = document.getElementById('save-badge');
  const hasSaved  = document.body.dataset.saved === 'true';

  if (saveBadge && hasSaved) {
    saveBadge.className  = 'badge badge-saved';
    saveBadge.innerHTML  = '<svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg> Saved';
  }

  /* ── Save bar visibility ─────────────────────────────── */
  const saveBar = document.querySelector('.floating-save-bar');

  if (saveBar) {
    document.addEventListener('change', () => {
      saveBar.style.display = 'flex';
    }, { once: true });
  }

  /* ── Initial state ───────────────────────────────────── */
  refreshTotals();
  detectConflicts();
  syncBreakVisibility();
  syncSubjectVisibility();

})();
