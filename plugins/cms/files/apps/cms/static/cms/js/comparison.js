/**
 * Comparison Slider - Before/After image comparison with draggable slider
 *
 * Usage: Add the .comparison-slider class to a container with:
 * - .comparison-before: Element containing the "before" image (clipped)
 * - .comparison-handle: The draggable slider handle
 * - .comparison-range: Hidden range input for accessibility
 * - data-initial: Initial position (0-100, default 50)
 */

(function() {
  'use strict';

  function initComparisonSliders() {
    document.querySelectorAll('.comparison-slider').forEach(function(slider) {
      if (slider.dataset.initialized) return;
      slider.dataset.initialized = 'true';

      const beforeEl = slider.querySelector('.comparison-before');
      const handleEl = slider.querySelector('.comparison-handle');
      const rangeEl = slider.querySelector('.comparison-range');

      if (!beforeEl || !handleEl) return;

      let isDragging = false;

      function updatePosition(percentage) {
        percentage = Math.max(0, Math.min(100, percentage));
        beforeEl.style.clipPath = 'inset(0 ' + (100 - percentage) + '% 0 0)';
        handleEl.style.left = percentage + '%';
        if (rangeEl) rangeEl.value = percentage;
      }

      function getPercentage(e) {
        const rect = slider.getBoundingClientRect();
        const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
        return (x / rect.width) * 100;
      }

      // Mouse events
      slider.addEventListener('mousedown', function(e) {
        isDragging = true;
        updatePosition(getPercentage(e));
      });

      document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        e.preventDefault();
        updatePosition(getPercentage(e));
      });

      document.addEventListener('mouseup', function() {
        isDragging = false;
      });

      // Touch events
      slider.addEventListener('touchstart', function(e) {
        isDragging = true;
        updatePosition(getPercentage(e));
      });

      slider.addEventListener('touchmove', function(e) {
        if (!isDragging) return;
        e.preventDefault();
        updatePosition(getPercentage(e));
      });

      slider.addEventListener('touchend', function() {
        isDragging = false;
      });

      // Range input for accessibility
      if (rangeEl) {
        rangeEl.addEventListener('input', function() {
          updatePosition(parseFloat(this.value));
        });
      }

      // Set initial position
      var initial = parseFloat(slider.dataset.initial) || 50;
      updatePosition(initial);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initComparisonSliders);
  } else {
    initComparisonSliders();
  }

  // Expose for manual initialization if needed
  window.ComparisonSlider = {
    init: initComparisonSliders
  };
})();
