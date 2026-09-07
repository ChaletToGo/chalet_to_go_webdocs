(() => {
  'use strict';
  const messages = JSON.parse(document.querySelector('#reader-i18n').textContent);
  const chapters = [...document.querySelectorAll('.chapter')];
  const reading = document.querySelector('#reading');
  const previous = document.querySelector('#previous');
  const next = document.querySelector('#next');
  const storage = {
    get(key) { try { return localStorage.getItem(`chalet-reader-${key}`); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(`chalet-reader-${key}`, value); } catch { /* Reading remains available without storage. */ } }
  };
  let current = 0;
  const pad = value => String(value).padStart(2, '0');
  function show(index, { updateHash = true, focus = true } = {}) {
    if (index < 0 || index >= chapters.length) return;
    current = index;
    chapters.forEach((chapter, i) => { chapter.hidden = i !== index; });
    reading.scrollTop = 0;
    const chapter = chapters[index];
    previous.disabled = index === 0;
    next.disabled = index === chapters.length - 1;
    document.querySelector('#chapter-number').textContent = pad(index);
    document.querySelector('#chapter-name').textContent = chapter.dataset.title;
    document.querySelector('#page-counter').innerHTML = `${pad(index + 1)} <span>/ ${pad(chapters.length)}</span>`;
    document.querySelector('#progress-label').textContent = `${index + 1} / ${chapters.length}`;
    document.querySelector('#progress-fill').style.width = `${((index + 1) / chapters.length) * 100}%`;
    document.querySelector('.progress-track').setAttribute('aria-valuenow', index + 1);
    document.querySelectorAll('#contents [data-goto]').forEach(link => {
      if (link.dataset.goto === chapter.id) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    document.title = `${chapter.dataset.title} — Chalet to Go`;
    storage.set('chapter', chapter.id);
    if (updateHash && location.hash !== `#${chapter.id}`) history.pushState(null, '', `#${chapter.id}`);
    if (focus) {
      const heading = chapter.querySelector('h1, h2');
      heading.tabIndex = -1;
      heading.focus({ preventScroll: true });
      document.querySelector('#announcement').textContent = messages.announcement
        .replace('{title}', chapter.dataset.title).replace('{current}', index + 1).replace('{total}', chapters.length);
    }
  }
  const fromId = id => chapters.findIndex(chapter => chapter.id === id);
  function hashId() { try { return decodeURIComponent(location.hash.slice(1)); } catch { return ''; } }
  const initialId = location.hash ? hashId() : storage.get('chapter');
  show(Math.max(0, fromId(initialId)), { updateHash: false, focus: false });
  previous.addEventListener('click', () => show(current - 1));
  next.addEventListener('click', () => show(current + 1));
  document.querySelectorAll('[data-next]').forEach(button => button.addEventListener('click', () => show(current + 1)));
  document.querySelectorAll('[data-goto]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    document.querySelectorAll('dialog[open]').forEach(dialog => dialog.close());
    show(fromId(link.dataset.goto));
  }));
  document.querySelector('.brand').addEventListener('click', event => { event.preventDefault(); show(0); });
  window.addEventListener('hashchange', () => {
    const id = hashId();
    if (id === 'reading') return;
    show(Math.max(0, fromId(id)), { updateHash: false });
  });
  document.addEventListener('keydown', event => {
    if (document.querySelector('dialog[open]') || event.altKey || event.ctrlKey || event.metaKey || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) return;
    if (event.key === 'ArrowRight') { event.preventDefault(); show(current + 1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); show(current - 1); }
  });
  let touchStart;
  reading.addEventListener('touchstart', event => {
    if (event.touches.length !== 1 || event.target.closest('button,a,input,select,textarea,.table-scroll')) { touchStart = null; return; }
    touchStart = { x: event.touches[0].clientX, y: event.touches[0].clientY };
  }, { passive: true });
  reading.addEventListener('touchend', event => {
    if (!touchStart || event.changedTouches.length !== 1) return;
    const dx = event.changedTouches[0].clientX - touchStart.x;
    const dy = event.changedTouches[0].clientY - touchStart.y;
    if (Math.abs(dx) > 85 && Math.abs(dx) > Math.abs(dy) * 2 && !window.getSelection()?.toString()) show(current + (dx < 0 ? 1 : -1));
    touchStart = null;
  }, { passive: true });
  reading.addEventListener('touchcancel', () => { touchStart = null; }, { passive: true });
  document.querySelectorAll('[data-dialog]').forEach(button => button.addEventListener('click', () => document.getElementById(button.dataset.dialog).showModal()));
  document.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
  document.querySelectorAll('[data-language]').forEach(link => link.addEventListener('click', () => {
    const destination = new URL(link.href);
    destination.hash = chapters[current].id;
    link.href = destination.href;
  }));
  document.querySelectorAll('dialog').forEach(dialog => dialog.addEventListener('click', event => {
    const rect = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
  }));
  function setPreference(name, value) {
    const allowed = name === 'size' ? ['normal', 'large', 'larger'] : ['paper', 'night'];
    if (!allowed.includes(value)) value = allowed[0];
    document.body.dataset[name] = value;
    document.querySelectorAll(`[data-${name}]`).forEach(button => {
      if (button.tagName === 'BUTTON') button.setAttribute('aria-pressed', String(button.dataset[name] === value));
    });
    storage.set(name, value);
  }
  for (const name of ['size', 'theme']) {
    setPreference(name, storage.get(name));
    document.querySelectorAll(`button[data-${name}]`).forEach(button => button.addEventListener('click', () => setPreference(name, button.dataset[name])));
  }
  const fullscreen = document.querySelector('#fullscreen');
  if (!document.fullscreenEnabled) fullscreen.hidden = true;
  fullscreen.addEventListener('click', async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch { document.querySelector('#announcement').textContent = messages.fullscreen_unavailable; }
  });
  document.addEventListener('fullscreenchange', () => fullscreen.setAttribute('aria-label', document.fullscreenElement ? messages.fullscreen_exit : messages.fullscreen_enter));
})();
