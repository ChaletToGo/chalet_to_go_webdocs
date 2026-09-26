const studies = {
 A:{file:'conceito-a.png',box:'120 160 780 650',name:'Casa em linha'},
 B:{file:'conceito-b.png',box:'60 60 904 904',name:'Abrigo essencial'},
 C:{file:'conceito-c.png',box:'60 60 904 904',name:'Ofício alpino'},
 D:{file:'conceito-d.png',box:'0 300 1024 400',name:'Arquitetura em viagem'},
 E:{file:'conceito-e.png',box:'60 60 904 904',name:'Destino aberto'},
 F:{file:'conceito-f.png',box:'60 60 904 904',name:'Forma em movimento'},
 '01':{file:'referencia-01.png',box:'105 145 760 800',name:'Modelo inicial 01',full:true},
 '02':{file:'referencia-02.png',box:'300 65 925 905',name:'Modelo inicial 02',full:true},
 '03':{file:'referencia-03.png',box:'300 65 925 905',name:'Modelo inicial 03',full:true}
};
let instance=0;
function renderLogo(element){
 const study=studies[element.dataset.logo];
 const ink=element.dataset.ink==='snow'?'#f6f4f0':'#0e2a20';
 const id=`concept-${++instance}`;
 element.classList.toggle('complete-logo',Boolean(study.full));
 element.innerHTML=`<svg class="concept-symbol" xmlns="http://www.w3.org/2000/svg" viewBox="${study.box}" aria-hidden="true" focusable="false"><defs><filter id="${id}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.4 0 0 0 1.15" /><feComposite in2="SourceGraphic" operator="in" result="mask"/><feFlood flood-color="${ink}"/><feComposite in2="mask" operator="in"/></filter></defs><image href="/static/estudo-identidade/${study.file}" width="${study.full?1536:1024}" height="1024" filter="url(#${id})"/></svg>${study.full?'':'<img class="original-wordmark" src="/static/estudo-identidade/assinatura-original.svg" alt="">'}`;
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
 const letter=button.dataset.select;
 document.querySelectorAll('[data-application]').forEach(element=>{
  element.dataset.logo=letter;
  const surface=element.closest('article');
  element.setAttribute('aria-label',`${studies[letter].name}, uma cor sobre fundo ${surface.classList.contains('forest')?'verde':surface.classList.contains('wood')?'marrom':'claro'}`);
  surface.querySelector('.app-top span:last-child').textContent=`${studies[letter].full?'RODADA 01':'CONCEITO'} / ${letter}`;
  renderLogo(element);
 });
 document.querySelector('#selection-status').textContent=`Exibindo ${studies[letter].full?'primeira rodada':'conceito '+letter} — ${studies[letter].name}`;
}));

