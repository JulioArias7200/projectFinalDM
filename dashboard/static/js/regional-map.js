/**
 * DM Lab - Interactive Regional Map & Universe Breakdown Controller
 * Manages layer switches (Salud s02, Educación s03, Empleo s04, Ingresos s05, Demografía s01)
 * and syncs SVG map selections with detailed department cards and table.
 */
(function () {
  'use strict';

  let regionData = null;
  let activeUniverse = 'politico';
  let selectedDeptId = 2; // Default: La Paz

  const DEPT_COLORS = {
    1: '#a78bfa', // Chuquisaca (Lila)
    2: '#e879f9', // La Paz (Rosa / Lila)
    3: '#fb923c', // Cochabamba (Naranja)
    4: '#38bdf8', // Oruro (Cian)
    5: '#a3e635', // Potosí (Lima)
    6: '#ea580c', // Tarija (Naranja intenso)
    7: '#84cc16', // Santa Cruz (Verde)
    8: '#f87171', // Beni (Coral/Rojo)
    9: '#ec4899'  // Pando (Fucsia)
  };


  const UNIVERSE_THEMES = {
    politico: {
      title: 'Mapa Departamental de Bolivia (División Oficial)',
      legendLabel: '9 Departamentos Oficiales',
      color: '#ec4899',
      isMultiColor: true,
      getValue: (d) => d.demografia.n_encuestados,
      getFormatted: (v) => `${v.toLocaleString()} personas`
    },
    demografia: {
      title: 'Mapa de Densidad: Demografía & Muestra (s01)',
      legendLabel: 'Muestra de Personas (n)',
      color: '#f59e0b',
      getValue: (d) => d.demografia.n_encuestados,
      getFormatted: (v) => `${v.toLocaleString()} personas`,
      minVal: 1900,
      maxVal: 9900
    },
    salud: {
      title: 'Mapa Temático: Universo Salud (s02) - Cobertura Seguro',
      legendLabel: 'Cobertura Seguro (%)',
      color: '#00d2ff',
      getValue: (d) => d.salud.valor,
      getFormatted: (v) => `${v}% cobertura`,
      minVal: 55,
      maxVal: 80
    },
    educacion: {
      title: 'Mapa Temático: Universo Educación (s03) - Alfabetismo',
      legendLabel: 'Tasa Alfabetismo (%)',
      color: '#8a5cf6',
      getValue: (d) => d.educacion.valor,
      getFormatted: (v) => `${v}% alfabetismo`,
      minVal: 85,
      maxVal: 100
    },
    empleo: {
      title: 'Mapa Temático: Universo Empleo (s04) - Tasa Ocupación',
      legendLabel: 'Tasa de Ocupación (%)',
      color: '#3b82f6',
      getValue: (d) => d.empleo.valor,
      getFormatted: (v) => `${v}% ocupados`,
      minVal: 55,
      maxVal: 75
    },
    ingresos: {
      title: 'Mapa Temático: Universo Ingresos (s05) - Pobreza Moderada',
      legendLabel: 'Incidencia Pobreza (%)',
      color: '#ff2453',
      getValue: (d) => d.ingresos.valor,
      getFormatted: (v) => `${v}% pobreza`,
      minVal: 20,
      maxVal: 50
    }
  };


  function initRegionalMap() {
    const jsonScript = document.getElementById('region-data-json');
    if (!jsonScript) return;

    try {
      regionData = JSON.parse(jsonScript.textContent);
    } catch (e) {
      console.error('[RegionalMap] Error parsing JSON payload:', e);
      return;
    }

    if (!regionData || !regionData.departamentos) return;

    // Check URL query parameters for pre-selected universe layer (e.g. ?universo=salud)
    const urlParams = new URLSearchParams(window.location.search);
    const qUniverse = urlParams.get('universo');
    if (qUniverse && UNIVERSE_THEMES[qUniverse]) {
      activeUniverse = qUniverse;
    }

    bindFilterButtons();
    bindMapInteractions();
    bindTableInteractions();
    syncInitialFilterButton();
    updateMapDisplay();
    updateDepartmentCard(selectedDeptId);
  }

  function syncInitialFilterButton() {
    const buttons = document.querySelectorAll('.universe-filter-btn');
    buttons.forEach((btn) => {
      const uniKey = btn.getAttribute('data-universe');
      if (uniKey === activeUniverse) {
        buttons.forEach((b) => {
          b.classList.remove('active', 'text-white', 'shadow-md');
          b.classList.add('bg-[var(--bg-card-subtle)]', 'text-[var(--text-muted)]');
          b.style.backgroundColor = '';
        });
        const theme = UNIVERSE_THEMES[activeUniverse];
        btn.classList.remove('bg-[var(--bg-card-subtle)]', 'text-[var(--text-muted)]');
        btn.classList.add('active', 'text-white', 'shadow-md');
        btn.style.backgroundColor = theme.color;
      }
    });
  }

  function bindFilterButtons() {
    const buttons = document.querySelectorAll('.universe-filter-btn');
    buttons.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const uniKey = btn.getAttribute('data-universe');
        if (uniKey && UNIVERSE_THEMES[uniKey]) {
          activeUniverse = uniKey;

          // Update Button styles
          buttons.forEach((b) => {
            b.classList.remove('active', 'text-white', 'shadow-md');
            b.classList.add('bg-[var(--bg-card-subtle)]', 'text-[var(--text-muted)]');
            b.style.backgroundColor = '';
          });

          const theme = UNIVERSE_THEMES[activeUniverse];
          btn.classList.remove('bg-[var(--bg-card-subtle)]', 'text-[var(--text-muted)]');
          btn.classList.add('active', 'text-white', 'shadow-md');
          btn.style.backgroundColor = theme.color;

          updateMapDisplay();
        }
      });
    });
  }

  function updateMapDisplay() {
    const theme = UNIVERSE_THEMES[activeUniverse];
    const mapTitle = document.getElementById('map-active-title');
    const legendLabel = document.getElementById('legend-label');
    const legendBar = document.getElementById('legend-bar');

    if (mapTitle) mapTitle.textContent = theme.title;
    if (legendLabel) legendLabel.textContent = theme.legendLabel;
    if (legendBar) {
      if (theme.isMultiColor) {
        legendBar.style.background = 'linear-gradient(to right, #ec4899, #f87171, #84cc16, #38bdf8, #fb923c, #ea580c)';
      } else {
        legendBar.style.background = `linear-gradient(to right, ${theme.color}33, ${theme.color}aa, ${theme.color})`;
      }
    }

    // Color each department polygon
    regionData.departamentos.forEach((dept) => {
      const poly = document.getElementById(`dept-poly-${dept.id}`);
      if (poly) {
        if (theme.isMultiColor) {
          const deptColor = DEPT_COLORS[dept.id] || '#84cc16';
          poly.setAttribute('fill', deptColor);
          poly.setAttribute('fill-opacity', '0.88');
        } else {
          const val = theme.getValue(dept);
          const norm = Math.max(0, Math.min(1, (val - theme.minVal) / (theme.maxVal - theme.minVal)));
          const opacity = (0.35 + norm * 0.6).toFixed(2);
          poly.setAttribute('fill', theme.color);
          poly.setAttribute('fill-opacity', opacity);
        }

        // Highlight selected
        if (dept.id === selectedDeptId) {
          poly.setAttribute('stroke', '#ffffff');
          poly.setAttribute('stroke-width', '3');
          poly.setAttribute('filter', 'url(#glow-filter)');
        } else {
          poly.setAttribute('stroke', 'var(--bg-card)');
          poly.setAttribute('stroke-width', '1.5');
          poly.removeAttribute('filter');
        }
      }
    });
  }


  function updateDepartmentCard(deptId) {
    const dept = regionData.departamentos.find((d) => d.id === parseInt(deptId, 10));
    if (!dept) return;

    selectedDeptId = dept.id;

    // Header
    const codeEl = document.getElementById('card-dept-code');
    const capitalEl = document.getElementById('card-dept-capital');
    const nameEl = document.getElementById('card-dept-name');
    const sampleEl = document.getElementById('card-dept-sample');

    if (codeEl) codeEl.textContent = dept.code;
    if (capitalEl) capitalEl.textContent = `Capital: ${dept.capital}`;
    if (nameEl) nameEl.textContent = dept.name;
    if (sampleEl) sampleEl.textContent = `${dept.demografia.n_encuestados.toLocaleString()} encuestados (${dept.demografia.pct_nacional}%)`;

    // 1. Demografia s01
    const popEl = document.getElementById('card-dem-pop');
    const urbEl = document.getElementById('card-dem-urb');
    const rurEl = document.getElementById('card-dem-rur');
    if (popEl) popEl.textContent = `${dept.demografia.poblacion_estimada.toLocaleString()} hab. proyectados`;
    if (urbEl) urbEl.textContent = `${dept.demografia.urbano_pct}%`;
    if (rurEl) rurEl.textContent = `${dept.demografia.rural_pct}%`;

    // 2. Salud s02
    const saludEl = document.getElementById('card-salud-val');
    if (saludEl) saludEl.textContent = `${dept.salud.valor}%`;

    // 3. Educacion s03
    const eduEl = document.getElementById('card-edu-val');
    if (eduEl) eduEl.textContent = `${dept.educacion.valor}%`;

    // 4. Empleo s04
    const empEl = document.getElementById('card-emp-val');
    if (empEl) empEl.textContent = `${dept.empleo.valor}%`;

    // 5. Ingresos s05
    const ingEl = document.getElementById('card-ing-val');
    if (ingEl) ingEl.textContent = `${dept.ingresos.valor}%`;

    // Highlight selected in Table
    document.querySelectorAll('.table-dept-row').forEach((row) => {
      const rId = parseInt(row.getAttribute('data-dept-id'), 10);
      if (rId === selectedDeptId) {
        row.classList.add('bg-amber-500/10');
      } else {
        row.classList.remove('bg-amber-500/10');
      }
    });

    updateMapDisplay();
  }

  function bindMapInteractions() {
    const paths = document.querySelectorAll('.dept-region-path');
    paths.forEach((path) => {
      path.addEventListener('click', () => {
        const deptId = path.getAttribute('data-dept-id');
        if (deptId) {
          updateDepartmentCard(deptId);
        }
      });

      path.addEventListener('mouseenter', () => {
        path.setAttribute('stroke', '#ffffff');
        path.setAttribute('stroke-width', '2.5');
      });

      path.addEventListener('mouseleave', () => {
        const deptId = parseInt(path.getAttribute('data-dept-id'), 10);
        if (deptId !== selectedDeptId) {
          path.setAttribute('stroke', 'var(--bg-card)');
          path.setAttribute('stroke-width', '1.5');
        }
      });
    });
  }

  function bindTableInteractions() {
    const rows = document.querySelectorAll('.table-dept-row');
    rows.forEach((row) => {
      row.addEventListener('click', () => {
        const deptId = row.getAttribute('data-dept-id');
        if (deptId) {
          updateDepartmentCard(deptId);
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRegionalMap);
  } else {
    initRegionalMap();
  }
})();
