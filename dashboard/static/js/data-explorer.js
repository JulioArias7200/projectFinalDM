/**
 * ML Lab - Data Explorer Module
 * Client-side search, type filtering, universe filtering for data dictionary.
 */
(function () {
  'use strict';

  function initDataExplorer() {
    const searchInput = document.getElementById('var-search-input');
    const typeFilter = document.getElementById('var-type-filter');
    const universeFilter = document.getElementById('universe-filter');
    const varRows = document.querySelectorAll('.var-row');

    if (!searchInput || varRows.length === 0) return;

    function applyFilter() {
      const term = searchInput.value.toLowerCase().trim();
      const selectedType = typeFilter ? typeFilter.value.toLowerCase() : 'all';
      const selectedUniverse = universeFilter ? universeFilter.value.toLowerCase() : 'all';
      let visibleCount = 0;

      varRows.forEach((row) => {
        const varName = (row.getAttribute('data-var-name') || '').toLowerCase();
        const varLabel = (row.getAttribute('data-var-label') || '').toLowerCase();
        const varType = (row.getAttribute('data-var-type') || '').toLowerCase();

        const matchesTerm = !term || varName.includes(term) || varLabel.includes(term);
        const matchesType = selectedType === 'all' || varType === selectedType;
        
        // Universe prefix match (s01, s02, s03, s04, s05 or other keys)
        let matchesUniverse = true;
        if (selectedUniverse !== 'all') {
          if (selectedUniverse === 's01') {
            matchesUniverse = varName.startsWith('s01') || varName.startsWith('folio') || varName.startsWith('nro') || varName.startsWith('depto') || varName.startsWith('area') || varName.startsWith('upm') || varName.startsWith('estrato') || varName.startsWith('factor') || varName.startsWith('totper');
          } else if (selectedUniverse === 's02') {
            matchesUniverse = varName.startsWith('s02');
          } else if (selectedUniverse === 's03') {
            matchesUniverse = varName.startsWith('s03') || varName === 'aestudio';
          } else if (selectedUniverse === 's04') {
            matchesUniverse = varName.startsWith('s04') || varName.startsWith('condact') || varName.startsWith('p04') || varName.startsWith('phrs') || varName.startsWith('tothrs') || varName.startsWith('pea') || varName.startsWith('pet');
          } else if (selectedUniverse === 's05') {
            matchesUniverse = varName.startsWith('s05') || varName.startsWith('y') || varName.startsWith('p0') || varName.startsWith('pext') || varName.startsWith('lp') || varName.startsWith('li');
          } else {
            matchesUniverse = varName.startsWith(selectedUniverse);
          }
        }

        if (matchesTerm && matchesType && matchesUniverse) {
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
    if (universeFilter) {
      universeFilter.addEventListener('change', applyFilter);
    }
  }

  document.addEventListener('DOMContentLoaded', initDataExplorer);
})();
