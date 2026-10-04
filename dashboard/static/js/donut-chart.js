/**
 * ML Lab - Donut Chart Module
 * Interactive segment highlight and smooth radius animations.
 */
(function () {
  'use strict';

  function initDonutChart() {
    const segments = document.querySelectorAll('.donut-circle');
    segments.forEach((seg) => {
      seg.addEventListener('mouseenter', () => {
        seg.style.strokeWidth = '14';
      });
      seg.addEventListener('mouseleave', () => {
        seg.style.strokeWidth = '12';
      });
    });
  }

  document.addEventListener('DOMContentLoaded', initDonutChart);
})();
