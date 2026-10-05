/**
 * ML Lab - Comparative Chart Module (5 Universos & 11 Vistas Temáticas)
 * Dynamically switches curves and displays true elegibility vs raw apparent completeness.
 * All bezier curves use strictly bounded Cubic Bezier (C) coordinates to prevent graph clipping.
 */
(function () {
  'use strict';

  const UNIVERSE_DATA = {
    todos: {
      desc: '100% Columnas Preservadas en Master Limpio (275 vars · 11 Vistas)',
      rawPathArea: 'M 0,14 C 100,16 150,22 250,88 C 320,135 380,30 460,25 C 530,22 580,50 630,45 C 700,38 730,130 810,125 C 850,120 870,20 900,15 L 900,180 L 0,180 Z',
      rawPathLine: 'M 0,14 C 100,16 150,22 250,88 C 320,135 380,30 460,25 C 530,22 580,50 630,45 C 700,38 730,130 810,125 C 850,120 870,20 900,15',
      cleanPathArea: 'M 0,10 C 150,12 300,15 450,12 C 600,14 750,10 900,11 L 900,180 L 0,180 Z',
      cleanPathLine: 'M 0,10 C 150,12 300,15 450,12 C 600,14 750,10 900,11',
      markerX: 460,
      markerY: 12,
      completeness: '98.2% Completitud en Universo Elegible',
      code: 'Master Limpio + 11 Vistas',
      title: '39,497 registros · 275 variables'
    },
    demografia: {
      desc: 'Demografía & Hogar: 39,497 personas en 12,718 hogares únicos',
      rawPathArea: 'M 0,10 C 200,12 450,14 650,12 C 780,10 850,12 900,10 L 900,180 L 0,180 Z',
      rawPathLine: 'M 0,10 C 200,12 450,14 650,12 C 780,10 850,12 900,10',
      cleanPathArea: 'M 0,8 C 200,8 450,9 650,8 C 780,8 850,8 900,8 L 900,180 L 0,180 Z',
      cleanPathLine: 'M 0,8 C 200,8 450,9 650,8 C 780,8 850,8 900,8',
      markerX: 200,
      markerY: 8,
      completeness: '99.8% Completitud en Demografía y Hogar',
      code: 's01 / Clave (folio, nro)',
      title: '33 cols demografía · 18 cols hogar'
    },
    salud: {
      desc: 'Salud: 4 Sub-vistas (General 39k, Fecundidad 11.3k, Menores <6: 3.4k, Bono <5: 2.7k)',
      rawPathArea: 'M 0,18 C 150,20 250,125 450,130 C 600,135 750,25 900,20 L 900,180 L 0,180 Z',
      rawPathLine: 'M 0,18 C 150,20 250,125 450,130 C 600,135 750,25 900,20',
      cleanPathArea: 'M 0,12 C 180,15 360,18 540,16 C 720,14 850,12 900,12 L 900,180 L 0,180 Z',
      cleanPathLine: 'M 0,12 C 180,15 360,18 540,16 C 720,14 850,12 900,12',
      markerX: 450,
      markerY: 16,
      completeness: '97.4% Efectiva en Sub-universos de Salud',
      code: 's02 / Salud 4 Vistas',
      title: '11,328 mujeres 13-50 · 3,434 niños <6'
    },
    educacion: {
      desc: 'Educación: 37,354 personas de 4 años o más (43 columnas)',
      rawPathArea: 'M 0,15 C 200,32 400,30 600,28 C 750,25 850,18 900,15 L 900,180 L 0,180 Z',
      rawPathLine: 'M 0,15 C 200,32 400,30 600,28 C 750,25 850,18 900,15',
      cleanPathArea: 'M 0,10 C 200,12 400,11 600,12 C 750,10 850,10 900,10 L 900,180 L 0,180 Z',
      cleanPathLine: 'M 0,10 C 200,12 400,11 600,12 C 750,10 850,10 900,10',
      markerX: 450,
      markerY: 11,
      completeness: '98.9% Efectiva en Población ≥ 4 años',
      code: 's03 / Educación',
      title: '37,354 personas elegibles · 43 vars'
    },
    empleo: {
      desc: 'Empleo: PET 35,366 personas ≥ 7 años (121 cols) + 1,357 casos ocupación secundaria (45 cols)',
      rawPathArea: 'M 0,20 C 150,25 300,120 500,125 C 680,130 800,35 900,25 L 900,180 L 0,180 Z',
      rawPathLine: 'M 0,20 C 150,25 300,120 500,125 C 680,130 800,35 900,25',
      cleanPathArea: 'M 0,14 C 200,16 400,18 600,16 C 800,14 850,12 900,13 L 900,180 L 0,180 Z',
      cleanPathLine: 'M 0,14 C 200,16 400,18 600,16 C 800,14 850,12 900,13',
      markerX: 500,
      markerY: 16,
      completeness: '96.8% Efectiva en PET (≥ 7 años)',
      code: 's04 / PET + Secundario',
      title: '35,366 PET · Regla S-01 (≤168h)'
    },
    ingresos: {
      desc: 'Ingresos & Pobreza: 2 Vistas (No laborales 48 cols + Pobreza 25 cols) + 12,718 Hogares',
      rawPathArea: 'M 0,18 C 180,45 350,90 550,95 C 700,100 820,30 900,20 L 900,180 L 0,180 Z',
      rawPathLine: 'M 0,18 C 180,45 350,90 550,95 C 700,100 820,30 900,20',
      cleanPathArea: 'M 0,12 C 200,14 400,15 600,13 C 800,12 850,11 900,12 L 900,180 L 0,180 Z',
      cleanPathLine: 'M 0,12 C 200,14 400,15 600,13 C 800,12 850,11 900,12',
      markerX: 550,
      markerY: 13,
      completeness: '97.9% Efectiva en Hogares e Ingresos',
      code: 's05 / Ingresos & Pobreza',
      title: '48 cols no lab. · 25 cols pobreza'
    }
  };

  function initComparativeChart() {
    const tabs = document.querySelectorAll('.chart-tab-btn');
    const descEl = document.getElementById('active-tab-desc');
    const rawArea = document.getElementById('curve-area-raw');
    const rawLine = document.getElementById('curve-line-raw');
    const cleanArea = document.getElementById('curve-area-clean');
    const cleanLine = document.getElementById('curve-line-clean');
    const marker = document.getElementById('chart-marker');
    const tooltipCompleteness = document.getElementById('tooltip-completeness');
    const tooltipCode = document.getElementById('tooltip-code');
    const tooltipTitle = document.getElementById('tooltip-title');
    const tooltipBadge = document.getElementById('chart-tooltip-badge');

    if (!tabs || tabs.length === 0) return;

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const universeKey = tab.dataset.universe || 'todos';
        const data = UNIVERSE_DATA[universeKey];
        if (!data) return;

        // Toggle active styling
        tabs.forEach(t => {
          t.classList.remove('active', 'bg-[#3b82f6]/20', 'border-[#3b82f6]', 'text-[#3b82f6]');
          t.classList.add('bg-[var(--bg-card-subtle)]', 'border-[var(--border-card)]', 'text-[var(--text-secondary)]');
        });
        tab.classList.add('active', 'bg-[#3b82f6]/20', 'border-[#3b82f6]', 'text-[#3b82f6]');
        tab.classList.remove('bg-[var(--bg-card-subtle)]', 'text-[var(--text-secondary)]');

        // Update Text and Metadata
        if (descEl) descEl.textContent = data.desc;
        if (tooltipCompleteness) tooltipCompleteness.textContent = data.completeness;
        if (tooltipCode) tooltipCode.textContent = data.code;
        if (tooltipTitle) tooltipTitle.textContent = data.title;

        // Update bounded SVG curves
        if (rawArea) rawArea.setAttribute('d', data.rawPathArea);
        if (rawLine) rawLine.setAttribute('d', data.rawPathLine);
        if (cleanArea) cleanArea.setAttribute('d', data.cleanPathArea);
        if (cleanLine) cleanLine.setAttribute('d', data.cleanPathLine);

        // Update marker and badge position
        if (marker) {
          marker.setAttribute('cx', data.markerX);
          marker.setAttribute('cy', data.markerY);
        }
        if (tooltipBadge) {
          const percentX = (data.markerX / 900) * 100;
          tooltipBadge.style.left = `${percentX}%`;
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', initComparativeChart);
})();
