/**
 * ML Lab - Data Explorer Module
 * Client-side search, type filtering, and pagination for data dictionary and candidate dataset.
 */
(function () {
  'use strict';

  function initDataExplorer() {
    const searchInput = document.getElementById('var-search-input');
    const typeFilter = document.getElementById('var-type-filter');
    const varRows = document.querySelectorAll('.var-row');

    if (!searchInput || varRows.length === 0) return;

    function applyFilter() {
      const term = searchInput.value.toLowerCase().trim();
      const selectedType = typeFilter ? typeFilter.value.toLowerCase() : 'all';
      let visibleCount = 0;

      varRows.forEach((row) => {
        const varName = (row.getAttribute('data-var-name') || '').toLowerCase();
        const varLabel = (row.getAttribute('data-var-label') || '').toLowerCase();
        const varType = (row.getAttribute('data-var-type') || '').toLowerCase();

        const matchesTerm = !term || varName.includes(term) || varLabel.includes(term);
        const matchesType = selectedType === 'all' || varType === selectedType;

        if (matchesTerm && matchesType) {
          row.style.display = '';
          visibleCount++;
        } else {
          row.style.display = 'none';
        }
      });

      const countBadge = document.getElementById('visible-var-count');
      if (countBadge) {
        countBadge.textContent = `${visibleCount} variables mostradas`;
      }
    }

    searchInput.addEventListener('input', applyFilter);
    if (typeFilter) {
      typeFilter.addEventListener('change', applyFilter);
    }
  }

  document.addEventListener('DOMContentLoaded', initDataExplorer);
})();
