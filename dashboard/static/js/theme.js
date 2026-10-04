/**
 * ML Lab - Theme Manager (Day / Night Mode)
 * Pure vanilla JS module with localStorage persistence and system color scheme detection.
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'mllab_theme';

  function getSavedTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark' || saved === 'light') {
      return saved;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    const isDark = theme === 'dark';
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem(STORAGE_KEY, theme);
    updateToggleButtons(isDark);
  }

  function toggleTheme() {
    const currentIsDark = document.documentElement.classList.contains('dark');
    applyTheme(currentIsDark ? 'light' : 'dark');
  }

  function updateToggleButtons(isDark) {
    const buttons = document.querySelectorAll('[data-action="toggle-theme"]');
    buttons.forEach((btn) => {
      const sunIcon = btn.querySelector('.theme-icon-sun');
      const moonIcon = btn.querySelector('.theme-icon-moon');
      const label = btn.querySelector('.theme-label');

      if (sunIcon && moonIcon) {
        if (isDark) {
          sunIcon.classList.remove('hidden');
          moonIcon.classList.add('hidden');
        } else {
          sunIcon.classList.add('hidden');
          moonIcon.classList.remove('hidden');
        }
      }
      if (label) {
        label.textContent = isDark ? 'Modo Día' : 'Modo Noche';
      }
      btn.setAttribute('aria-label', isDark ? 'Cambiar a Modo Día' : 'Cambiar a Modo Noche');
      btn.setAttribute('title', isDark ? 'Cambiar a Modo Día' : 'Cambiar a Modo Noche');
    });
  }

  // Bind click events on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', () => {
    const initialTheme = getSavedTheme();
    applyTheme(initialTheme);

    const toggleButtons = document.querySelectorAll('[data-action="toggle-theme"]');
    toggleButtons.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTheme();
      });
    });

    // Listen for OS color scheme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(STORAGE_KEY)) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  });

  // Expose to window namespace
  window.MLTheme = {
    toggle: toggleTheme,
    set: applyTheme,
    get: getSavedTheme
  };
})();
