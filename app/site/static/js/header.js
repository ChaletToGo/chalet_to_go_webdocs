(() => {
  const header = document.querySelector('.site-header');
  const toggle = header.querySelector('.menu-toggle');
  const panel = header.querySelector('.navigation-panel');
  const languages = header.querySelector('.languages');
  const mobile = matchMedia('(max-width: 1100px)');
  header.classList.add('menu-ready');
  const close = (restore = false) => {
    toggle.setAttribute('aria-expanded', 'false');
    header.classList.remove('menu-open');
    languages.open = false;
    if (restore) toggle.focus();
  };
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    header.classList.toggle('menu-open', open);
  });
  panel.querySelectorAll('a').forEach(link => link.addEventListener('click', () => close(mobile.matches)));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') close(mobile.matches && header.classList.contains('menu-open'));
  });
  document.addEventListener('click', event => { if (!header.contains(event.target)) close(); });
  header.addEventListener('focusout', event => { if (!header.contains(event.relatedTarget)) close(); });
  mobile.addEventListener('change', () => close());
})();
