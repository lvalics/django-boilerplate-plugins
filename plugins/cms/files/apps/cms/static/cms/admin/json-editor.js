/* Self-contained JSON editor for CMS admin JSONField textareas.
 *
 * Progressive enhancement: enhances every <textarea class="cms-json-editor">
 * with pretty-printing, a format/minify toolbar, and live syntax validation.
 * No external dependencies. Falls back to a plain textarea without JS.
 */
(function () {
  'use strict';

  function makeButton(label, title) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'cms-json-btn';
    b.textContent = label;
    b.title = title;
    return b;
  }

  function enhance(textarea) {
    if (textarea.dataset.cmsJsonReady) {
      return;
    }
    textarea.dataset.cmsJsonReady = '1';

    var wrap = document.createElement('div');
    wrap.className = 'cms-json-editor-wrap';
    textarea.parentNode.insertBefore(wrap, textarea);

    var bar = document.createElement('div');
    bar.className = 'cms-json-toolbar';

    var formatBtn = makeButton('Format', 'Pretty-print (2-space indent)');
    var minifyBtn = makeButton('Minify', 'Collapse to a single line');
    var status = document.createElement('span');
    status.className = 'cms-json-status';

    bar.appendChild(formatBtn);
    bar.appendChild(minifyBtn);
    bar.appendChild(status);

    wrap.appendChild(bar);
    wrap.appendChild(textarea);

    function setStatus(ok, message) {
      status.textContent = message;
      status.classList.toggle('is-valid', ok);
      status.classList.toggle('is-invalid', !ok);
      textarea.classList.toggle('cms-json-invalid', !ok);
    }

    function validate() {
      var raw = textarea.value.trim();
      if (raw === '') {
        setStatus(true, 'empty');
        return true;
      }
      try {
        JSON.parse(raw);
        setStatus(true, 'valid JSON');
        return true;
      } catch (err) {
        setStatus(false, String(err.message || err));
        return false;
      }
    }

    function reformat(indent) {
      var raw = textarea.value.trim();
      if (raw === '') {
        return;
      }
      try {
        var parsed = JSON.parse(raw);
        textarea.value = JSON.stringify(parsed, null, indent);
        validate();
      } catch (err) {
        validate();
      }
    }

    formatBtn.addEventListener('click', function () {
      reformat(2);
    });
    minifyBtn.addEventListener('click', function () {
      reformat(0);
    });
    textarea.addEventListener('input', validate);

    // Insert two spaces on Tab instead of leaving the field.
    textarea.addEventListener('keydown', function (e) {
      if (e.key === 'Tab' && !e.shiftKey) {
        e.preventDefault();
        var start = textarea.selectionStart;
        var end = textarea.selectionEnd;
        textarea.value = textarea.value.slice(0, start) + '  ' + textarea.value.slice(end);
        textarea.selectionStart = textarea.selectionEnd = start + 2;
      }
    });

    // Pretty-print valid JSON on first load, then report validity.
    reformat(2);

    // Block submitting invalid JSON so the editor catches typos before the
    // round-trip (server-side JSONField validation still runs regardless).
    var form = textarea.closest('form');
    if (form && !form.dataset.cmsJsonGuard) {
      form.dataset.cmsJsonGuard = '1';
      form.addEventListener('submit', function (e) {
        var bad = null;
        var fields = form.querySelectorAll('textarea.cms-json-editor');
        for (var i = 0; i < fields.length; i++) {
          var raw = fields[i].value.trim();
          if (raw === '') {
            continue;
          }
          try {
            JSON.parse(raw);
          } catch (err) {
            bad = fields[i];
            break;
          }
        }
        if (bad) {
          e.preventDefault();
          bad.classList.add('cms-json-invalid');
          bad.focus();
          bad.scrollIntoView({ block: 'center' });
        }
      });
    }
  }

  function init() {
    var fields = document.querySelectorAll('textarea.cms-json-editor');
    for (var i = 0; i < fields.length; i++) {
      enhance(fields[i]);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
