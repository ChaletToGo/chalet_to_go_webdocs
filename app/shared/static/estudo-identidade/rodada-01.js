// Crops frame the supplied raster studies; the filter simulates single-ink artwork.
const studies = {
  1: {file:'referencia-01.png', box:'105 145 760 800', name:'Ilustração 01'},
  2: {file:'referencia-02.png', box:'300 65 925 905', name:'Ilustrativa'},
  3: {file:'referencia-03.png', box:'300 65 925 905', name:'Plus'}
};
let instance = 0;
function renderLogo(element) {
  const study=studies[element.dataset.logo];
  const ink=element.dataset.ink === 'snow' ? '#f6f4f0' : '#0e2a20';
  const id=`ink-${++instance}`;
  element.innerHTML=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${study.box}" aria-hidden="true" focusable="false"><defs><filter id="${id}-mono" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.4 0 0 0 1.15" result="mask"/><feFlood flood-color="${ink}"/><feComposite in2="mask" operator="in"/></filter></defs><image href="${study.file}" width="1536" height="1024" filter="url(#${id}-mono)"/></svg>`;
}
document.querySelectorAll('[data-logo]').forEach(renderLogo);
document.querySelector('.grid-overlay').innerHTML='<i></i>'.repeat(12);
document.querySelector('#grid-button').addEventListener('click',event=>{
  const active=document.body.classList.toggle('show-grid');
  event.currentTarget.setAttribute('aria-pressed',String(active));
  event.currentTarget.innerHTML=`${active?'Ocultar':'Exibir'} grid <span aria-hidden="true">${active?'−':'＋'}</span>`;
});
document.querySelectorAll('[data-select]').forEach(button=>button.addEventListener('click',()=>{
  document.querySelectorAll('[data-select]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
  const number=button.dataset.select;
  document.querySelectorAll('[data-application]').forEach(element=>{
    element.dataset.logo=number;
    element.setAttribute('aria-label',`Proposta ${number}, ${studies[number].name}, uma cor sobre fundo ${element.closest('article').classList.contains('forest')?'verde':element.closest('article').classList.contains('wood')?'marrom':'claro'}`);
    element.closest('article').querySelector('.app-top span:last-child').textContent=`ESTUDO / 0${number}`;
    renderLogo(element);
  });
  document.querySelector('#selection-status').textContent=`Exibindo proposta 0${number} — ${studies[number].name}`;
}));

