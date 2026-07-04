/**
 * Lightbox/Modal - Shared lightbox functionality for landing page zones
 *
 * Usage:
 * 1. Add data-lightbox="groupId" to clickable images/elements
 * 2. Add data-lightbox-index="N" for the index in the group
 * 3. Modal will be auto-created or use existing [data-lightbox-modal="groupId"]
 *
 * For video support:
 * - Add data-lightbox-video="url" for video content
 * - Add data-lightbox-poster="url" for video poster
 *
 * Data attributes on trigger elements:
 * - data-lightbox="groupId" - Group identifier
 * - data-lightbox-index="0" - Index in the group
 * - data-lightbox-src="url" - Image/video source (defaults to img src or href)
 * - data-lightbox-alt="text" - Alt text for image
 * - data-lightbox-title="text" - Title for caption
 * - data-lightbox-description="text" - Description for caption
 * - data-lightbox-video="url" - Video URL (for video content)
 * - data-lightbox-poster="url" - Video poster URL
 */

(function() {
  'use strict';

  // Store for lightbox groups
  const lightboxGroups = {};

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLightboxes);
  } else {
    initLightboxes();
  }

  function initLightboxes() {
    // Find all lightbox triggers and group them
    const triggers = document.querySelectorAll('[data-lightbox]');

    triggers.forEach(function(trigger) {
      const groupId = trigger.dataset.lightbox;

      if (!lightboxGroups[groupId]) {
        lightboxGroups[groupId] = {
          triggers: [],
          items: [],
          modal: null,
          currentIndex: 0
        };
      }

      const group = lightboxGroups[groupId];
      const index = group.triggers.length;

      // Store trigger reference
      group.triggers.push(trigger);

      // Extract item data
      const item = {
        src: trigger.dataset.lightboxSrc || trigger.src || trigger.href || '',
        alt: trigger.dataset.lightboxAlt || trigger.alt || '',
        title: trigger.dataset.lightboxTitle || '',
        description: trigger.dataset.lightboxDescription || '',
        video: trigger.dataset.lightboxVideo || '',
        poster: trigger.dataset.lightboxPoster || ''
      };
      group.items.push(item);

      // Set up click handler
      trigger.style.cursor = 'pointer';
      trigger.addEventListener('click', function(e) {
        e.preventDefault();
        openLightbox(groupId, index);
      });
    });

    // Create modals for each group
    Object.keys(lightboxGroups).forEach(function(groupId) {
      createModal(groupId);
    });

    // Global keyboard handler
    document.addEventListener('keydown', handleKeyboard);
  }

  function createModal(groupId) {
    const group = lightboxGroups[groupId];

    // Check for existing modal
    let modal = document.querySelector('[data-lightbox-modal="' + groupId + '"]');

    if (!modal) {
      // Create modal element
      modal = document.createElement('div');
      modal.className = 'fixed inset-0 z-50 hidden items-center justify-center bg-black/90 p-4';
      modal.setAttribute('data-lightbox-modal', groupId);
      modal.innerHTML = `
        <button type="button" data-lightbox-close
                class="absolute top-4 right-4 z-10 w-10 h-10 rounded-full bg-white/20 hover:bg-white/40 flex items-center justify-center transition-colors">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>

        <button type="button" data-lightbox-prev
                class="absolute left-4 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full bg-white/20 hover:bg-white/40 flex items-center justify-center transition-colors">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 6 10">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 1 1 5l4 4"/>
          </svg>
        </button>

        <button type="button" data-lightbox-next
                class="absolute right-4 top-1/2 -translate-y-1/2 z-10 w-12 h-12 rounded-full bg-white/20 hover:bg-white/40 flex items-center justify-center transition-colors">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 6 10">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 9 4-4-4-4"/>
          </svg>
        </button>

        <div class="lightbox-content max-w-5xl max-h-[90vh] flex items-center justify-center">
          <!-- Content injected here -->
        </div>

        <div class="lightbox-caption absolute bottom-4 left-1/2 -translate-x-1/2 text-center text-white max-w-2xl px-4" style="display: none;">
          <h4 class="lightbox-title text-xl font-bold mb-1"></h4>
          <p class="lightbox-description text-white/80"></p>
        </div>
      `;

      document.body.appendChild(modal);
    }

    group.modal = modal;

    // Set up modal event handlers
    const closeBtn = modal.querySelector('[data-lightbox-close]');
    const prevBtn = modal.querySelector('[data-lightbox-prev]');
    const nextBtn = modal.querySelector('[data-lightbox-next]');

    closeBtn.addEventListener('click', function() {
      closeLightbox(groupId);
    });

    prevBtn.addEventListener('click', function() {
      showPrev(groupId);
    });

    nextBtn.addEventListener('click', function() {
      showNext(groupId);
    });

    // Close on backdrop click
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeLightbox(groupId);
      }
    });

    // Hide nav buttons if only one item
    if (group.items.length <= 1) {
      prevBtn.style.display = 'none';
      nextBtn.style.display = 'none';
    }
  }

  function openLightbox(groupId, index) {
    const group = lightboxGroups[groupId];
    if (!group || !group.modal) return;

    showItem(groupId, index);
    group.modal.classList.remove('hidden');
    group.modal.classList.add('flex');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox(groupId) {
    const group = lightboxGroups[groupId];
    if (!group || !group.modal) return;

    group.modal.classList.add('hidden');
    group.modal.classList.remove('flex');
    document.body.style.overflow = '';

    // Stop any playing video
    const video = group.modal.querySelector('video');
    if (video) video.pause();
  }

  function showItem(groupId, index) {
    const group = lightboxGroups[groupId];
    if (!group) return;

    // Normalize index
    index = (index + group.items.length) % group.items.length;
    group.currentIndex = index;

    const item = group.items[index];
    const contentEl = group.modal.querySelector('.lightbox-content');
    const captionEl = group.modal.querySelector('.lightbox-caption');
    const titleEl = group.modal.querySelector('.lightbox-title');
    const descEl = group.modal.querySelector('.lightbox-description');

    // Clear previous content
    contentEl.innerHTML = '';

    if (item.video) {
      // Video content
      const video = document.createElement('video');
      video.className = 'max-w-full max-h-[80vh] rounded-lg';
      video.controls = true;
      video.autoplay = true;
      if (item.poster) video.poster = item.poster;

      const source = document.createElement('source');
      source.src = item.video;
      source.type = 'video/mp4';
      video.appendChild(source);
      contentEl.appendChild(video);
    } else if (item.src) {
      // Image content
      const img = document.createElement('img');
      img.src = item.src;
      img.alt = item.alt || 'Lightbox image';
      img.className = 'max-w-full max-h-[85vh] object-contain rounded-lg';
      contentEl.appendChild(img);
    }

    // Update caption
    if (item.title || item.description) {
      titleEl.textContent = item.title || '';
      descEl.textContent = item.description || '';
      captionEl.style.display = 'block';
    } else {
      captionEl.style.display = 'none';
    }
  }

  function showNext(groupId) {
    const group = lightboxGroups[groupId];
    if (!group) return;
    showItem(groupId, group.currentIndex + 1);
  }

  function showPrev(groupId) {
    const group = lightboxGroups[groupId];
    if (!group) return;
    showItem(groupId, group.currentIndex - 1);
  }

  function handleKeyboard(e) {
    // Find active lightbox
    let activeGroupId = null;
    Object.keys(lightboxGroups).forEach(function(groupId) {
      const group = lightboxGroups[groupId];
      if (group.modal && !group.modal.classList.contains('hidden')) {
        activeGroupId = groupId;
      }
    });

    if (!activeGroupId) return;

    if (e.key === 'Escape') {
      closeLightbox(activeGroupId);
    } else if (e.key === 'ArrowLeft') {
      showPrev(activeGroupId);
    } else if (e.key === 'ArrowRight') {
      showNext(activeGroupId);
    }
  }

  // Expose for manual control
  window.PageLightbox = {
    init: initLightboxes,
    open: openLightbox,
    close: closeLightbox,
    next: showNext,
    prev: showPrev
  };
})();
