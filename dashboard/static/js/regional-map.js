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
    const hogEl = document.getElementById('card-dept-hogares');

    if (codeEl) codeEl.textContent = dept.code;
    if (capitalEl) capitalEl.textContent = `Capital: ${dept.capital}`;
    if (nameEl) nameEl.textContent = dept.name;
    if (sampleEl) sampleEl.textContent = `${dept.demografia.n_encuestados.toLocaleString()} personas`;
    if (hogEl) hogEl.textContent = `${dept.demografia.n_hogares.toLocaleString()} hogares (${dept.demografia.pct_nacional}% nac.)`;

    // 1. Demografia s01
    const popEl = document.getElementById('card-dem-pop');
    const urbEl = document.getElementById('card-dem-urb');
    const rurEl = document.getElementById('card-dem-rur');
    const sexEl = document.getElementById('card-dem-sex');
    const edadEl = document.getElementById('card-dem-edad');

    if (popEl) popEl.textContent = `${dept.demografia.poblacion_estimada.toLocaleString()} hab. proyectados`;
    if (urbEl) urbEl.textContent = `${dept.demografia.n_urbano.toLocaleString()} (${dept.demografia.urbano_pct}%)`;
    if (rurEl) rurEl.textContent = `${dept.demografia.n_rural.toLocaleString()} (${dept.demografia.rural_pct}%)`;
    if (sexEl) sexEl.textContent = `${dept.demografia.n_hombres.toLocaleString()} H / ${dept.demografia.n_mujeres.toLocaleString()} M`;
    if (edadEl) edadEl.textContent = `${dept.demografia.edad_promedio} años`;

    // 2. Salud s02
    const saludEl = document.getElementById('card-salud-val');
    const saludMef = document.getElementById('card-salud-mef');
    const saludN6 = document.getElementById('card-salud-n6');
    const saludN5 = document.getElementById('card-salud-n5');

    if (saludEl) saludEl.textContent = `${dept.salud.n_con_seguro.toLocaleString()} con seguro (${dept.salud.valor}%)`;
    if (saludMef) saludMef.textContent = dept.salud.n_mef_13_50.toLocaleString();
    if (saludN6) saludN6.textContent = dept.salud.n_ninos_menor_6.toLocaleString();
    if (saludN5) saludN5.textContent = dept.salud.n_ninos_menor_5.toLocaleString();

    // 3. Educacion s03
    const eduEl = document.getElementById('card-edu-val');
    const eduEleg = document.getElementById('card-edu-eleg');
    const eduPob15 = document.getElementById('card-edu-pob15');

    if (eduEl) eduEl.textContent = `${dept.educacion.n_alfabetizados.toLocaleString()} alfabetizados (${dept.educacion.valor}%)`;
    if (eduEleg) eduEleg.textContent = `${dept.educacion.n_elegibles_4mas.toLocaleString()} (${dept.educacion.pct_elegibles_4mas}%)`;
    if (eduPob15) eduPob15.textContent = `${dept.educacion.n_pob_15mas.toLocaleString()} evaluados`;

    // 4. Empleo s04
    const empEl = document.getElementById('card-emp-val');
    const empPet = document.getElementById('card-emp-pet');
    const empSec = document.getElementById('card-emp-sec');

    if (empEl) empEl.textContent = `${dept.empleo.n_ocupados.toLocaleString()} ocupados (${dept.empleo.valor}%)`;
    if (empPet) empPet.textContent = `${dept.empleo.n_pet_7mas.toLocaleString()} (${dept.empleo.pct_pet_7mas}%)`;
    if (empSec) empSec.textContent = `${dept.empleo.n_ocupacion_secundaria.toLocaleString()} casos`;

    // 5. Ingresos s05
    const ingEl = document.getElementById('card-ing-val');
    const ingConlab = document.getElementById('card-ing-conlab');
    const ingMed = document.getElementById('card-ing-med');

    if (ingEl) ingEl.textContent = `${dept.ingresos.n_pobreza_moderada.toLocaleString()} en pobreza (${dept.ingresos.valor}%)`;
    if (ingConlab) ingConlab.textContent = `${dept.ingresos.n_con_ingreso_laboral.toLocaleString()} personas`;
    if (ingMed) ingMed.textContent = `Bs ${dept.ingresos.mediana_ingreso_laboral.toLocaleString()} / mes`;

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
