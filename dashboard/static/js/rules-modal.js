/**
 * ML Lab - Data Cleaning Rules Modal Controller
 * Displays detailed information modal for each cleaning rule (L-01 to L-80).
 * Dynamically parses backend data directly from DOM payload or fallback store.
 */
(function () {
  'use strict';

  function getRulesData() {
    const jsonScript = document.getElementById('rules-data-json');
    if (jsonScript) {
      try {
        const rawData = JSON.parse(jsonScript.textContent);
        if (Array.isArray(rawData)) {
          const map = {};
          rawData.forEach((item) => {
            map[item.id] = {
              id: item.id,
              name: item.name,
              category: item.category,
              badgeColor: item.badge_color || item.badgeColor || '#00d2ff',
              courseRef: item.course_ref || item.courseRef,
              columns: item.columns,
              universe: item.universe,
              condition: item.condition,
              action: item.action,
              beforeAfter: item.before_after || item.beforeAfter,
              impact: item.impact,
              evidence: item.evidence
            };
          });
          return map;
        }
      } catch (e) {
        console.warn('[RulesModal] Could not parse dynamic rules payload:', e);
      }
    }
    return {};
  }

  function initRuleModals() {
    const modal = document.getElementById('rule-detail-modal');
    const modalBackdrop = document.getElementById('rule-modal-backdrop');
    const modalCloseBtn = document.getElementById('rule-modal-close');
    const ruleTriggers = document.querySelectorAll('[data-rule-trigger]');

    if (!modal) return;

    const dynamicRules = getRulesData();

    function openModal(ruleId) {
      const data = dynamicRules[ruleId];
      if (!data) return;

      // Populate Modal Fields
      const idEl = document.getElementById('modal-rule-id');
      if (idEl) {
        idEl.textContent = data.id;
        idEl.style.color = data.badgeColor;
      }
      
      const nameEl = document.getElementById('modal-rule-name');
      if (nameEl) nameEl.textContent = data.name;

      const catEl = document.getElementById('modal-rule-category');
      if (catEl) catEl.textContent = data.category;

      const courseEl = document.getElementById('modal-rule-course');
      if (courseEl) courseEl.textContent = data.courseRef;

      const colEl = document.getElementById('modal-rule-columns');
      if (colEl) colEl.textContent = data.columns;

      const uniEl = document.getElementById('modal-rule-universe');
      if (uniEl) uniEl.textContent = data.universe;

      const condEl = document.getElementById('modal-rule-condition');
      if (condEl) condEl.textContent = data.condition;

      const actEl = document.getElementById('modal-rule-action');
      if (actEl) actEl.textContent = data.action;

      const baEl = document.getElementById('modal-rule-beforeafter');
      if (baEl) baEl.textContent = data.beforeAfter;

      const impEl = document.getElementById('modal-rule-impact');
      if (impEl) impEl.textContent = data.impact;

      const evEl = document.getElementById('modal-rule-evidence');
      if (evEl) evEl.textContent = data.evidence;

      // Show modal
      modal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
    }

    function closeModal() {
      modal.classList.add('hidden');
      document.body.style.overflow = '';
    }

    // Bind click listener directly to each entire table row (<tr>)
    ruleTriggers.forEach((row) => {
      row.addEventListener('click', (e) => {
        e.preventDefault();
        const ruleId = row.getAttribute('data-rule-trigger');
        if (ruleId) {
          openModal(ruleId);
        }
      });
    });

    if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);
    if (modalBackdrop) modalBackdrop.addEventListener('click', closeModal);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeModal();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRuleModals);
  } else {
    initRuleModals();
  }
})();

