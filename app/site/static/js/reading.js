(() => {
  const dialog = document.querySelector('#site-reading');
  const launch = document.querySelector('.reading-launch');
  const options = {size:['normal','large','larger'],theme:['paper','night']};
  function apply(name, value) {
    if (!options[name].includes(value)) value = options[name][0];
    document.body.dataset['reading'+name[0].toUpperCase()+name.slice(1)] = value;
    dialog.querySelectorAll(`[data-reading-${name}]`).forEach(button => {
      button.setAttribute('aria-pressed', String(button.getAttribute(`data-reading-${name}`) === value));
    });
  }
  for (const name of Object.keys(options)) {
    let saved;
    try { saved = localStorage.getItem('chalet-site-reading-'+name); } catch {}
    apply(name, saved);
    dialog.querySelectorAll(`[data-reading-${name}]`).forEach(button => button.addEventListener('click', () => {
      const value = button.getAttribute(`data-reading-${name}`);
      apply(name, value);
      try { localStorage.setItem('chalet-site-reading-'+name, value); } catch {}
    }));
  }
  launch.addEventListener('click', () => dialog.showModal());
  dialog.querySelector('.reading-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => launch.focus());
})();
