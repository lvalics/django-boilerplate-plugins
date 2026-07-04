/**
 * File Upload Component with Dropzone and Image Cropping
 * Uses Cropper.js for image cropping functionality
 * Supports i18n via data-i18n attribute on container
 */

(function() {
  'use strict';

  // Default translations (can be overridden via data-i18n attribute)
  const defaultI18n = {
    maxFilesAllowed: 'Maximum {count} files allowed',
    fileTypeNotAllowed: 'File type not allowed: {name}',
    fileTooLarge: 'File too large: {name}. Maximum size is {size}MB',
    cropImage: 'Crop Image',
    cancel: 'Cancel',
    applyCrop: 'Apply Crop',
    crop: 'Crop',
    remove: 'Remove'
  };

  // Get translations from container or use defaults
  function getI18n(container) {
    try {
      const i18nAttr = container.dataset.i18n;
      if (i18nAttr) {
        return { ...defaultI18n, ...JSON.parse(i18nAttr) };
      }
    } catch (e) {
      console.warn('Failed to parse i18n data:', e);
    }
    return defaultI18n;
  }

  // Load Cropper.js CSS dynamically if cropping is enabled
  function loadCropperCSS() {
    if (!document.querySelector('link[href*="cropper"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.css';
      document.head.appendChild(link);
    }
  }

  // Load Cropper.js dynamically
  function loadCropperJS() {
    return new Promise((resolve, reject) => {
      if (window.Cropper) {
        resolve(window.Cropper);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.js';
      script.onload = () => resolve(window.Cropper);
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  // Initialize dropzone functionality
  function initDropzone(container) {
    const input = container.querySelector('input[type="file"]');
    const dropzone = container.querySelector('.dropzone-area');
    const preview = container.querySelector('.dropzone-preview');
    const placeholder = container.querySelector('.dropzone-placeholder');

    if (!dropzone || !input) return;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, preventDefaults, false);
      document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    // Highlight drop zone when dragging over
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, () => {
        dropzone.classList.add('border-primary', 'bg-primary/5');
        dropzone.classList.remove('border-base-300');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, () => {
        dropzone.classList.remove('border-primary', 'bg-primary/5');
        dropzone.classList.add('border-base-300');
      }, false);
    });

    // Handle dropped files
    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      handleFiles(files, container);
    }, false);

    // Handle file input change
    input.addEventListener('change', () => {
      handleFiles(input.files, container);
    });

    // Click to upload
    dropzone.addEventListener('click', (e) => {
      if (e.target.closest('.remove-file')) return;
      input.click();
    });
  }

  // Handle selected files
  function handleFiles(files, container) {
    const input = container.querySelector('input[type="file"]');
    const preview = container.querySelector('.dropzone-preview');
    const placeholder = container.querySelector('.dropzone-placeholder');
    const config = JSON.parse(container.dataset.config || '{}');
    const i18n = getI18n(container);
    const isMultiple = input.hasAttribute('multiple');
    const maxFiles = parseInt(input.dataset.maxFiles) || 10;

    if (!files.length) return;

    // Check max files
    if (isMultiple && files.length > maxFiles) {
      alert(i18n.maxFilesAllowed.replace('{count}', maxFiles));
      return;
    }

    // Clear preview if single file
    if (!isMultiple) {
      preview.innerHTML = '';
    }

    // Process each file
    Array.from(files).forEach((file, index) => {
      // Check file type
      const accept = input.getAttribute('accept');
      if (accept && !matchFileType(file, accept)) {
        alert(i18n.fileTypeNotAllowed.replace('{name}', file.name));
        return;
      }

      // Check file size
      const maxSize = parseInt(input.dataset.maxSize) || 10; // MB
      if (file.size > maxSize * 1024 * 1024) {
        alert(i18n.fileTooLarge.replace('{name}', file.name).replace('{size}', maxSize));
        return;
      }

      // Create preview
      createFilePreview(file, preview, container, config);
    });

    // Show/hide placeholder
    if (preview.children.length > 0) {
      placeholder.classList.add('hidden');
      preview.classList.remove('hidden');
    }
  }

  // Match file against accept pattern
  function matchFileType(file, accept) {
    const patterns = accept.split(',').map(p => p.trim());
    return patterns.some(pattern => {
      if (pattern.startsWith('.')) {
        return file.name.toLowerCase().endsWith(pattern.toLowerCase());
      }
      if (pattern.endsWith('/*')) {
        return file.type.startsWith(pattern.replace('/*', '/'));
      }
      return file.type === pattern;
    });
  }

  // Create file preview element
  function createFilePreview(file, previewContainer, container, config) {
    const previewItem = document.createElement('div');
    previewItem.className = 'relative group inline-block m-1';
    const i18n = getI18n(container);

    const isImage = file.type.startsWith('image/');

    if (isImage) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewItem.innerHTML = `
          <div class="relative w-24 h-24 rounded-lg overflow-hidden border border-base-300">
            <img src="${e.target.result}" class="w-full h-full object-cover preview-image" data-original="${e.target.result}">
            <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
              ${config.enableCrop ? '<button type="button" class="btn btn-xs btn-circle btn-ghost text-white crop-btn" title="' + i18n.crop + '"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h18M4 3v18m17-1H4m17 0V4m0 0l-7 7"></path></svg></button>' : ''}
              <button type="button" class="btn btn-xs btn-circle btn-ghost text-white remove-file" title="${i18n.remove}"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
            </div>
          </div>
          <p class="text-xs text-center mt-1 truncate w-24">${file.name}</p>
        `;

        // Store file reference
        previewItem.fileData = file;
        previewItem.originalDataUrl = e.target.result;

        // Add crop handler if enabled
        if (config.enableCrop) {
          const cropBtn = previewItem.querySelector('.crop-btn');
          cropBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openCropModal(previewItem, config);
          });

          // Auto-open crop modal on upload
          setTimeout(() => {
            openCropModal(previewItem, config);
          }, 100);
        }
      };
      reader.readAsDataURL(file);
    } else {
      // Non-image file preview
      previewItem.innerHTML = `
        <div class="relative w-24 h-24 rounded-lg overflow-hidden border border-base-300 bg-base-200 flex items-center justify-center">
          <svg class="w-8 h-8 text-base-content/50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          <button type="button" class="absolute top-1 right-1 btn btn-xs btn-circle btn-ghost remove-file"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
        </div>
        <p class="text-xs text-center mt-1 truncate w-24">${file.name}</p>
      `;
      previewItem.fileData = file;
    }

    // Remove handler
    previewItem.addEventListener('click', (e) => {
      if (e.target.closest('.remove-file')) {
        e.stopPropagation();
        previewItem.remove();
        updateFileInput(container);

        const placeholder = container.querySelector('.dropzone-placeholder');
        const preview = container.querySelector('.dropzone-preview');
        if (preview.children.length === 0) {
          placeholder.classList.remove('hidden');
          preview.classList.add('hidden');
        }
      }
    });

    previewContainer.appendChild(previewItem);
    updateFileInput(container);
  }

  // Update the hidden file input with current files
  function updateFileInput(container) {
    const preview = container.querySelector('.dropzone-preview');
    const hiddenInput = container.querySelector('input[name$="_data"]');

    if (!hiddenInput) return;

    const filesData = [];
    preview.querySelectorAll('[data-original]').forEach(img => {
      filesData.push({
        name: img.closest('.relative').querySelector('p').textContent,
        data: img.src
      });
    });

    hiddenInput.value = JSON.stringify(filesData);
  }

  // Open crop modal
  async function openCropModal(previewItem, config) {
    loadCropperCSS();
    const Cropper = await loadCropperJS();

    const img = previewItem.querySelector('.preview-image');
    const originalSrc = previewItem.originalDataUrl || img.dataset.original || img.src;
    const container = previewItem.closest('.file-upload-container');
    const i18n = container ? getI18n(container) : defaultI18n;

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70';
    modal.innerHTML = `
      <div class="bg-base-100 rounded-xl shadow-2xl max-w-2xl w-full mx-4 overflow-hidden">
        <div class="p-4 border-b border-base-300 flex justify-between items-center">
          <h3 class="font-semibold text-lg">${i18n.cropImage}</h3>
          <button type="button" class="btn btn-sm btn-ghost btn-circle close-modal">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        <div class="p-4">
          <div class="max-h-96 overflow-hidden">
            <img src="${originalSrc}" class="crop-image max-w-full">
          </div>
        </div>
        <div class="p-4 border-t border-base-300 flex justify-end gap-2">
          <button type="button" class="btn btn-ghost close-modal">${i18n.cancel}</button>
          <button type="button" class="btn btn-primary apply-crop">${i18n.applyCrop}</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    document.body.classList.add('overflow-hidden');

    // Initialize Cropper
    const cropImage = modal.querySelector('.crop-image');
    const cropper = new Cropper(cropImage, {
      aspectRatio: config.cropAspectRatio || NaN,
      viewMode: 1,
      autoCropArea: 0.8,
      responsive: true,
      restore: false,
      guides: true,
      center: true,
      highlight: true,
      cropBoxMovable: true,
      cropBoxResizable: true,
      toggleDragModeOnDblclick: false,
      minCropBoxWidth: config.cropMinWidth || 50,
      minCropBoxHeight: config.cropMinHeight || 50,
    });

    // Close modal handlers
    modal.querySelectorAll('.close-modal').forEach(btn => {
      btn.addEventListener('click', () => {
        cropper.destroy();
        modal.remove();
        document.body.classList.remove('overflow-hidden');
      });
    });

    // Apply crop
    modal.querySelector('.apply-crop').addEventListener('click', () => {
      const canvas = cropper.getCroppedCanvas({
        minWidth: config.cropMinWidth || 100,
        minHeight: config.cropMinHeight || 100,
        maxWidth: 2048,
        maxHeight: 2048,
      });

      if (canvas) {
        const croppedDataUrl = canvas.toDataURL('image/jpeg', 0.9);
        img.src = croppedDataUrl;

        // Convert to blob for form submission
        canvas.toBlob((blob) => {
          const fileName = previewItem.fileData?.name || 'cropped-image.jpg';
          previewItem.croppedFile = new File([blob], fileName, { type: 'image/jpeg' });

          // Update container
          const container = previewItem.closest('.file-upload-container');
          if (container) updateFileInput(container);
        }, 'image/jpeg', 0.9);
      }

      cropper.destroy();
      modal.remove();
      document.body.classList.remove('overflow-hidden');
    });

    // Close on backdrop click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        cropper.destroy();
        modal.remove();
        document.body.classList.remove('overflow-hidden');
      }
    });
  }

  // Initialize all file upload containers
  function initFileUploads() {
    document.querySelectorAll('.file-upload-container').forEach(container => {
      if (container.dataset.initialized) return;
      container.dataset.initialized = 'true';

      const config = JSON.parse(container.dataset.config || '{}');

      if (config.enableDropzone !== false) {
        initDropzone(container);
      }
    });
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFileUploads);
  } else {
    initFileUploads();
  }

  // Export for manual initialization
  window.FileUploadComponent = {
    init: initFileUploads,
    initDropzone: initDropzone
  };

})();
