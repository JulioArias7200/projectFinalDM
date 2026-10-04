/**
 * ML Lab - Comparative Learning Chart Module
 * Interactive wave graph tooltips, time-range filtering, and point hover effects.
 */
(function () {
  'use strict';

  function initComparativeChart() {
    const timeFilter = document.getElementById('chart-time-filter');
    const tooltipMarker = document.getElementById('chart-marker');
    const tooltipBadge = document.getElementById('chart-tooltip-badge');

    if (timeFilter) {
      timeFilter.addEventListener('click', () => {
        // Toggle time filters demo (e.g. 10 Folds vs 5 Folds vs Anual)
        const currentText = timeFilter.querySelector('.filter-label');
        if (!currentText) return;

        if (currentText.textContent.includes('10 Folds')) {
          currentText.textContent = '5 Folds (Semestral)';
        } else if (currentText.textContent.includes('5 Folds')) {
          currentText.textContent = 'K-Fold CV (Completo)';
        } else {
          currentText.textContent = 'Anual (10 Folds)';
        }
      });
    }
  }

  document.addEventListener('DOMContentLoaded', initComparativeChart);
})();
