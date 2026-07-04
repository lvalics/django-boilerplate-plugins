/**
 * Zone Animations - Shared IntersectionObserver animations for landing page zones
 *
 * Usage: Add data-zone-animate="true" to the section element
 *
 * Supported element classes:
 * - .zone-header: Header elements (title, subtitle) - fadeInUp
 * - .zone-item: Grid items with staggered animation (use style="--delay: Xms") - fadeInUp
 * - .zone-cta: Call-to-action elements - fadeInUp
 * - .zone-stats: Statistics/metrics elements - fadeInUp
 * - .zone-quote: Quote/testimonial elements - fadeIn
 * - .zone-logos: Logo grid elements - fadeIn
 * - .zone-trust: Trust badge elements - fadeIn
 * - .zone-image: Background/hero images - scaleIn (uses data-initial-scale)
 * - .zone-title: Title with scale animation - scaleIn with opacity
 * - .zone-specs: Specs/stats row - slideInUp with delay
 */

(function() {
  'use strict';

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initZoneAnimations);
  } else {
    initZoneAnimations();
  }

  function initZoneAnimations() {
    const sections = document.querySelectorAll('[data-zone-animate="true"]');

    sections.forEach(function(section) {
      setupSectionAnimation(section);
    });
  }

  function setupSectionAnimation(section) {
    const header = section.querySelector('.zone-header');
    const items = section.querySelectorAll('.zone-item');
    const cta = section.querySelector('.zone-cta');
    const stats = section.querySelector('.zone-stats');
    const quote = section.querySelector('.zone-quote');
    const logos = section.querySelector('.zone-logos');
    const trust = section.querySelector('.zone-trust');
    const image = section.querySelector('.zone-image');
    const title = section.querySelector('.zone-title');
    const specs = section.querySelector('.zone-specs');

    // Collect all animated elements
    const animatedElements = [];

    // Image scale animation (for showcase/hero sections)
    if (image) {
      const initialScale = image.dataset.initialScale || '0.9';
      image.style.transform = 'scale(' + initialScale + ')';
      animatedElements.push({ el: image, type: 'image', initialScale: initialScale });
    }

    if (header) {
      header.classList.add('zone-animate-hidden');
      header.style.transform = 'translateY(20px)';
      animatedElements.push({ el: header, type: 'header' });
    }

    // Title with scale animation (for showcase sections)
    if (title) {
      title.classList.add('zone-animate-hidden');
      title.style.transform = 'scale(0.95)';
      animatedElements.push({ el: title, type: 'title' });
    }

    items.forEach(function(item, index) {
      item.classList.add('zone-animate-hidden');
      item.style.transform = 'translateY(30px)';
      // Use CSS custom property for delay or calculate from index
      const delay = item.style.getPropertyValue('--delay') || (index * 100) + 'ms';
      item.style.transitionDelay = delay;
      animatedElements.push({ el: item, type: 'item', delay: delay });
    });

    if (stats) {
      stats.classList.add('zone-animate-hidden');
      stats.style.transform = 'translateY(20px)';
      animatedElements.push({ el: stats, type: 'stats' });
    }

    // Specs row animation (for showcase sections)
    if (specs) {
      specs.classList.add('zone-animate-hidden');
      specs.style.transform = 'translateY(20px)';
      animatedElements.push({ el: specs, type: 'specs' });
    }

    if (quote) {
      quote.classList.add('zone-animate-hidden');
      animatedElements.push({ el: quote, type: 'quote' });
    }

    if (logos) {
      logos.classList.add('zone-animate-hidden');
      animatedElements.push({ el: logos, type: 'logos' });
    }

    if (cta) {
      cta.classList.add('zone-animate-hidden');
      cta.style.transform = 'translateY(10px)';
      animatedElements.push({ el: cta, type: 'cta' });
    }

    if (trust) {
      trust.classList.add('zone-animate-hidden');
      animatedElements.push({ el: trust, type: 'trust' });
    }

    // Skip if no elements to animate
    if (animatedElements.length === 0) return;

    // Create observer
    const observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          animateSection(animatedElements);
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    observer.observe(section);
  }

  function animateSection(elements) {
    let baseDelay = 0;

    elements.forEach(function(item) {
      const el = item.el;
      const type = item.type;

      setTimeout(function() {
        el.style.transition = getTransition(type);

        // Handle different transform types
        if (type === 'image') {
          el.style.transform = 'scale(1)';
        } else if (type === 'title') {
          el.style.transform = 'scale(1)';
          el.classList.remove('zone-animate-hidden');
        } else {
          el.style.transform = 'translateY(0)';
          el.classList.remove('zone-animate-hidden');
        }
      }, baseDelay);

      // Stagger delays based on element type
      if (type === 'image') {
        // Image animates first, no delay added
      } else if (type === 'header') {
        baseDelay += 100;
      } else if (type === 'title') {
        baseDelay += 200;
      } else if (type === 'item') {
        // Items use their own delay via CSS
      } else if (type === 'stats') {
        baseDelay += 200;
      } else if (type === 'specs') {
        baseDelay += 200;
      } else if (type === 'quote') {
        baseDelay += 300;
      } else if (type === 'logos') {
        baseDelay += 200;
      } else if (type === 'cta') {
        baseDelay += 400;
      } else if (type === 'trust') {
        baseDelay += 200;
      }
    });
  }

  function getTransition(type) {
    switch (type) {
      case 'image':
        return 'transform 1s ease-out';
      case 'header':
        return 'opacity 0.6s ease-out, transform 0.6s ease-out';
      case 'title':
        return 'opacity 0.7s ease-out, transform 0.7s ease-out';
      case 'item':
        return 'opacity 0.5s ease-out, transform 0.5s ease-out';
      case 'stats':
        return 'opacity 0.6s ease-out, transform 0.6s ease-out';
      case 'specs':
        return 'opacity 0.7s ease-out, transform 0.7s ease-out';
      case 'quote':
        return 'opacity 0.6s ease-out';
      case 'logos':
        return 'opacity 0.6s ease-out';
      case 'cta':
        return 'opacity 0.5s ease-out, transform 0.5s ease-out';
      case 'trust':
        return 'opacity 0.5s ease-out';
      default:
        return 'opacity 0.5s ease-out, transform 0.5s ease-out';
    }
  }

  // Expose for manual initialization if needed
  window.PageAnimations = {
    init: initZoneAnimations,
    setupSection: setupSectionAnimation
  };
})();
