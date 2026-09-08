(() => {
  if (navigator.doNotTrack === '1' || navigator.globalPrivacyControl) return;
  let lastClick = 0;
  document.addEventListener('click', event => {
    const link = event.target.closest?.('a[href]');
    if (!link || new URL(link.href).hostname !== 'wa.me') return;
    const now = Date.now();
    if (now - lastClick < 1500) return;
    lastClick = now;
    const product = link.closest('article[id]')?.id || location.pathname.split('/')[2];
    const payload = JSON.stringify({page:location.pathname,lang:document.documentElement.lang,
      model:['basic','standard','premium'].includes(product) ? product : 'general'});
    navigator.sendBeacon?.('/api/site-metrics', new Blob([payload], {type:'application/json'}));
  });
})();
