/**
 * ML Lab - Inference Simulation Module
 * Simulates real-time voting ensemble predictions and latency evaluation.
 */
(function () {
  'use strict';

  function initSimulator() {
    const btn = document.getElementById('btn-simulate');
    if (!btn) return;

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      triggerSimulate(btn);
    });
  }

  function triggerSimulate(btn) {
    const originalContent = btn.innerHTML;
    const latencyEl = document.getElementById('inference-latency');

    btn.innerHTML = `<span class="inline-block animate-spin mr-1">⟳</span> Evaluando 100 Árboles...`;
    btn.disabled = true;

    // Simulate variable latency (10-18ms)
    const randomLatency = (10 + Math.random() * 8).toFixed(1);

    setTimeout(() => {
      btn.innerHTML = `<span class="text-emerald-300 font-bold">✓ Voto Unánime: Isquemia</span>`;
      if (latencyEl) {
        latencyEl.textContent = `${randomLatency} ms`;
      }

      setTimeout(() => {
        btn.innerHTML = originalContent;
        btn.disabled = false;
      }, 2000);
    }, 650);
  }

  document.addEventListener('DOMContentLoaded', initSimulator);

  window.MLSimulator = {
    trigger: triggerSimulate
  };
})();
