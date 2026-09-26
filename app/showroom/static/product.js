const tabs = [...document.querySelectorAll('[role=tab]')];
let viewerLoading;
function startViewer() {
  if (viewerLoading) return;
  viewerLoading = import(document.querySelector('.basic-product').dataset.viewerScript).catch(() => {
    document.querySelector('#loading-title').textContent = 'Não foi possível iniciar o 3D';
    document.querySelector('#loading-text').textContent = 'Verifique sua conexão e tente novamente.';
    document.querySelector('#retry').hidden = false;
    viewerLoading = null;
  });
}
function selectPanel(tab, focus = false) {
  for (const item of tabs) {
    const active = item === tab;
    item.setAttribute('aria-selected', String(active));
    item.tabIndex = active ? 0 : -1;
    document.getElementById(item.getAttribute('aria-controls')).hidden = !active;
  }
  if (focus) tab.focus();
  if (tab.dataset.panel === 'model') startViewer();
  document.dispatchEvent(new CustomEvent('product-panel', { detail: tab.dataset.panel }));
}
for (const [index, tab] of tabs.entries()) {
  tab.addEventListener('click', () => selectPanel(tab));
  tab.addEventListener('keydown', event => {
    const destinations = { ArrowRight: (index + 1) % tabs.length, ArrowLeft: (index + tabs.length - 1) % tabs.length, Home: 0, End: tabs.length - 1 };
    if (event.key in destinations) { event.preventDefault(); selectPanel(tabs[destinations[event.key]], true); }
  });
}
document.querySelector('[data-open-model]').onclick = () => selectPanel(document.querySelector('#tab-model'), true);
// Warm the browser cache after the main image; never on metered/slow connections.
window.addEventListener('load', () => {
  const connection = navigator.connection;
  if (connection?.saveData || ['slow-2g', '2g', '3g'].includes(connection?.effectiveType)) return;
  const warm = () => {
    if (viewerLoading) return;
    const href = document.querySelector('[data-model-id="exterior"]').dataset.modelUrl;
    if (!href) return;
    const link = document.createElement('link');
    link.rel = 'prefetch'; link.as = 'fetch'; link.href = href; link.crossOrigin = 'anonymous';
    document.head.append(link);
  };
  if ('requestIdleCallback' in window) requestIdleCallback(warm, { timeout: 8000 });
  else setTimeout(warm, 3000);
});
