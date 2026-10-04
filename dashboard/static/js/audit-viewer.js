/**
 * ML Lab - Audit Log Viewer Module
 * Client-side event filtering and timeline interaction.
 */
(function () {
  'use strict';

  function initAuditViewer() {
    const actionFilter = document.getElementById('audit-action-filter');
    const searchInput = document.getElementById('audit-search-input');
    const eventCards = document.querySelectorAll('.audit-event-card');

    if (!eventCards.length) return;

    function filterAuditLogs() {
      const term = searchInput ? searchInput.value.toLowerCase().trim() : '';
      const action = actionFilter ? actionFilter.value.toLowerCase() : 'all';

      eventCards.forEach((card) => {
        const cardAction = (card.getAttribute('data-action-type') || '').toLowerCase();
        const cardText = card.textContent.toLowerCase();

        const matchesTerm = !term || cardText.includes(term);
        const matchesAction = action === 'all' || cardAction === action;

        if (matchesTerm && matchesAction) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    }

    if (actionFilter) actionFilter.addEventListener('change', filterAuditLogs);
    if (searchInput) searchInput.addEventListener('input', filterAuditLogs);
  }

  document.addEventListener('DOMContentLoaded', initAuditViewer);
})();
