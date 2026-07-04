/**
 * Carousel/Slider - Shared carousel functionality for landing page zones
 *
 * Usage:
 * 1. Single-slide carousel: Add data-carousel="slide" to container
 * 2. Multi-column carousel: Add data-carousel="scroll" to container
 * 3. Gallery slider: Add data-carousel="gallery" to container
 *
 * Required structure:
 * - [data-carousel-item] for slide items
 * - [data-carousel-prev] for previous button
 * - [data-carousel-next] for next button
 * - [data-carousel-slide-to="N"] for indicator dots (optional)
 * - [data-current-slide] for current slide display (optional)
 *
 * Data attributes:
 * - data-auto-slide="true|false" - Enable auto-sliding (default: true)
 * - data-slide-interval="5000" - Auto-slide interval in ms (default: 5000)
 */

(function() {
  'use strict';

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCarousels);
  } else {
    initCarousels();
  }

  function initCarousels() {
    // Single-slide carousels
    document.querySelectorAll('[data-carousel="slide"]').forEach(initSlideCarousel);

    // Multi-column scrollable carousels
    document.querySelectorAll('[data-carousel="scroll"]').forEach(initScrollCarousel);

    // Gallery sliders
    document.querySelectorAll('[data-carousel="gallery"]').forEach(initSlideCarousel);
  }

  function initSlideCarousel(carousel) {
    if (carousel.dataset.carouselInit) return;
    carousel.dataset.carouselInit = 'true';

    const items = carousel.querySelectorAll('[data-carousel-item]');
    const indicators = carousel.querySelectorAll('[data-carousel-slide-to]');
    const prevBtn = carousel.querySelector('[data-carousel-prev]');
    const nextBtn = carousel.querySelector('[data-carousel-next]');
    const currentSlideEl = carousel.querySelector('[data-current-slide]');

    if (items.length === 0) return;

    let currentIndex = 0;
    const autoSlideEnabled = carousel.dataset.autoSlide !== 'false';
    const interval = parseInt(carousel.dataset.slideInterval, 10) || 5000;
    let autoSlideTimer;

    function showSlide(index) {
      // Normalize index
      index = (index + items.length) % items.length;

      items.forEach(function(item, i) {
        item.classList.toggle('hidden', i !== index);
        item.setAttribute('data-carousel-item', i === index ? 'active' : '');
      });

      indicators.forEach(function(ind, i) {
        ind.setAttribute('aria-current', i === index ? 'true' : 'false');
        ind.classList.toggle('bg-white', i === index);
        ind.classList.toggle('bg-white/50', i !== index);
      });

      if (currentSlideEl) {
        currentSlideEl.textContent = index + 1;
      }

      currentIndex = index;
    }

    function nextSlide() {
      showSlide(currentIndex + 1);
    }

    function prevSlide() {
      showSlide(currentIndex - 1);
    }

    function startAutoSlide() {
      if (autoSlideEnabled && items.length > 1) {
        autoSlideTimer = setInterval(nextSlide, interval);
      }
    }

    function stopAutoSlide() {
      clearInterval(autoSlideTimer);
    }

    function resetAutoSlide() {
      stopAutoSlide();
      startAutoSlide();
    }

    // Event listeners
    if (prevBtn) {
      prevBtn.addEventListener('click', function(e) {
        e.preventDefault();
        prevSlide();
        resetAutoSlide();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', function(e) {
        e.preventDefault();
        nextSlide();
        resetAutoSlide();
      });
    }

    indicators.forEach(function(ind, i) {
      ind.addEventListener('click', function(e) {
        e.preventDefault();
        showSlide(i);
        resetAutoSlide();
      });
    });

    // Pause on hover
    carousel.addEventListener('mouseenter', stopAutoSlide);
    carousel.addEventListener('mouseleave', startAutoSlide);

    // Keyboard navigation
    carousel.addEventListener('keydown', function(e) {
      if (e.key === 'ArrowLeft') {
        prevSlide();
        resetAutoSlide();
      } else if (e.key === 'ArrowRight') {
        nextSlide();
        resetAutoSlide();
      }
    });

    // Initialize
    showSlide(0);
    startAutoSlide();
  }

  function initScrollCarousel(carousel) {
    if (carousel.dataset.carouselInit) return;
    carousel.dataset.carouselInit = 'true';

    const container = carousel.querySelector('.carousel-container, [data-carousel-container]');
    const prevBtn = carousel.querySelector('[data-carousel-prev]');
    const nextBtn = carousel.querySelector('[data-carousel-next]');

    if (!container) return;

    const autoSlideEnabled = carousel.dataset.autoSlide !== 'false';
    const interval = parseInt(carousel.dataset.slideInterval, 10) || 4000;
    let autoSlideTimer;

    function getScrollAmount() {
      const firstSlide = container.querySelector('.carousel-slide, [data-carousel-item]');
      return firstSlide ? firstSlide.offsetWidth + 16 : 300;
    }

    function scrollPrev() {
      container.scrollBy({ left: -getScrollAmount(), behavior: 'smooth' });
    }

    function scrollNext() {
      // Loop back to start if at end
      if (container.scrollLeft + container.clientWidth >= container.scrollWidth - 10) {
        container.scrollTo({ left: 0, behavior: 'smooth' });
      } else {
        container.scrollBy({ left: getScrollAmount(), behavior: 'smooth' });
      }
    }

    function startAutoSlide() {
      if (autoSlideEnabled) {
        autoSlideTimer = setInterval(scrollNext, interval);
      }
    }

    function stopAutoSlide() {
      clearInterval(autoSlideTimer);
    }

    // Event listeners
    if (prevBtn) {
      prevBtn.addEventListener('click', function(e) {
        e.preventDefault();
        scrollPrev();
        stopAutoSlide();
        startAutoSlide();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', function(e) {
        e.preventDefault();
        scrollNext();
        stopAutoSlide();
        startAutoSlide();
      });
    }

    // Pause on hover
    carousel.addEventListener('mouseenter', stopAutoSlide);
    carousel.addEventListener('mouseleave', startAutoSlide);

    // Initialize
    startAutoSlide();
  }

  // Expose for manual initialization
  window.PageCarousel = {
    init: initCarousels,
    initSlide: initSlideCarousel,
    initScroll: initScrollCarousel
  };
})();
