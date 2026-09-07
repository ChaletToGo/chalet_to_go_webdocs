(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (!reduced.matches && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.remove('reveal-pending'); observer.unobserve(entry.target); }
    }), {threshold: 0.05});
    document.querySelectorAll('[data-reveal]').forEach(section => {
      if (section.getBoundingClientRect().top > innerHeight) { section.classList.add('reveal-pending'); observer.observe(section); }
    });
    reduced.addEventListener('change', () => {
      if (reduced.matches) { document.querySelectorAll('.reveal-pending').forEach(el => el.classList.remove('reveal-pending')); observer.disconnect(); }
    });
  }
  const dialog = document.querySelector('.gallery-dialog');
  if (!dialog || !dialog.showModal) return;
  const image = dialog.querySelector('img');
  let opener;
  document.querySelectorAll('.gallery-open').forEach(link => link.addEventListener('click', event => {
    event.preventDefault(); opener = link;
    image.src = link.href; image.alt = link.querySelector('img').alt;
    dialog.querySelector('p').textContent = image.alt;
    dialog.showModal(); document.body.classList.add('gallery-active');
  }));
  dialog.querySelector('button').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => { document.body.classList.remove('gallery-active'); opener?.focus(); });
})();
