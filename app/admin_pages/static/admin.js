const $ = (selector) => document.querySelector(selector);
let rows = [], editing = null;
const labels = {active:'Ativo', paused:'Pausado', expired:'Expirado'};
const number = value => new Intl.NumberFormat('pt-BR').format(value);
const date = value => value ? new Date(value).toLocaleString('pt-BR') : 'Nenhum acesso';
function el(tag, text, cls) { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (cls) node.className = cls; return node; }
function notify(text) { $('#message').textContent = text; }
async function api(path, options = {}) {
  const response = await fetch(path, {...options, headers:{'Content-Type':'application/json','X-Admin-Request':'1',...options.headers}});
  if (!response.ok) { const data = await response.json().catch(()=>({})); throw new Error(typeof data.detail === 'string' ? data.detail : data.detail?.map(item=>item.msg).join(' · ') || 'Não foi possível concluir. Tente novamente.'); }
  return response.json();
}
function downloadLink(row, format) { const a = el('a',format.toUpperCase(),'button secondary'); a.href = `/admin/api/qrcodes/${row.code}/download?format=${format}`; a.setAttribute('aria-label',`Baixar ${row.name} em ${format.toUpperCase()}`); return a; }
function action(text, handler) { const b = el('button',text,'secondary'); b.onclick = handler; return b; }
function render() {
  $('#count').textContent = number(rows.length);
  $('#active').textContent = number(rows.filter(r=>r.status==='active').length);
  $('#total').textContent = number(rows.reduce((n,r)=>n+r.total,0));
  $('#today').textContent = number(rows.reduce((n,r)=>n+(r.daily[new Date().toISOString().slice(0,10)]||0),0));
  const term = $('#search').value.toLocaleLowerCase();
  const filtered = rows.filter(r=>(r.name+' '+r.campaign).toLocaleLowerCase().includes(term) && (!$('#status').value || r.status===$('#status').value));
  const list = $('#list'); list.replaceChildren();
  if (!filtered.length) {const empty = el('div',undefined,'empty'); empty.append(el('h3',rows.length?'Nenhum resultado':'Seu próximo destino começa aqui.'),el('p',rows.length?'Experimente outro nome, campanha ou status.':'Crie seu primeiro QR Code e acompanhe as conexões com a Chalet to Go.'));list.append(empty);}
  for (const row of filtered.sort((a,b)=>b.created_at.localeCompare(a.created_at))) {
    const article = el('article',undefined,'qr-row'); const img = el('img'); img.src = `/admin/api/qrcodes/${row.code}/download?format=png`; img.alt = `QR Code de ${row.name}`; img.loading='lazy';
    const info = el('div'); info.append(el('h3',row.name),el('p',row.campaign || 'Sem campanha'),el('p',row.destination));
    const count = el('div',undefined,'access'); count.append(el('strong',number(row.total)),el('span','acessos'));
    const actions = el('div',undefined,'actions');
    actions.append(action('Editar',()=>openEditor(row)),action('Estatísticas',()=>details(row)),action(row.active?'Pausar':'Ativar',async()=>{try{await api(`/admin/api/qrcodes/${row.code}`,{method:'PUT',body:JSON.stringify({...payloadFrom(row),active:!row.active})}); await load();notify('Status atualizado.');}catch(e){notify(e.message);}}),action('Copiar link',async()=>{try{await navigator.clipboard.writeText(row.url);notify('Link copiado.');}catch{notify('Copie o link: '+row.url);}}),downloadLink(row,'png'),downloadLink(row,'svg'));
    article.append(img,info,el('span',labels[row.status],'badge '+row.status),count,actions); list.append(article);
  }
}
function payloadFrom(row){return {name:row.name,destination:row.destination,campaign:row.campaign,color:row.color,expires_at:row.expires_at,active:row.active};}
async function load(){try{rows=await api('/admin/api/qrcodes');render();}catch(e){notify(e.message);$('#list').replaceChildren(el('p','Não foi possível carregar a coleção. Clique em Atualizar para tentar novamente.'));}}
function openEditor(row=null){editing=row;$('#form').reset();$('#form-error').textContent='';$('#editor-title').textContent=row?'Editar QR Code':'Criar QR Code';if(row){for(const key of ['name','destination','campaign','color'])$('#form').elements[key].value=row[key];$('#form').elements.active.checked=row.active;if(row.expires_at){const d=new Date(row.expires_at);d.setMinutes(d.getMinutes()-d.getTimezoneOffset());$('#form').elements.expires_at.value=d.toISOString().slice(0,16);}}$('#editor').showModal();}
$('#form').onsubmit=async event=>{event.preventDefault();const f=event.currentTarget.elements;$('#save').disabled=true;$('#form-error').textContent='';try{const payload={name:f.name.value,destination:f.destination.value,campaign:f.campaign.value,color:f.color.value,active:f.active.checked,expires_at:f.expires_at.value?new Date(f.expires_at.value).toISOString():null};await api('/admin/api/qrcodes'+(editing?'/'+editing.code:''),{method:editing?'PUT':'POST',body:JSON.stringify(payload)});$('#editor').close();await load();notify(editing?'QR Code atualizado. O link impresso continua válido.':'QR Code criado. Baixe o arquivo em PNG ou SVG.');}catch(e){$('#form-error').textContent=e.message;}finally{$('#save').disabled=false;}};
function details(row){$('#detail-title').textContent=row.name;const content=$('#detail-content');content.replaceChildren(el('p',`${number(row.total)} acessos totais · Criado em ${date(row.created_at)}`),el('p','Último acesso: '+date(row.last_access)),el('p','Link permanente: '+row.url,'detail-link'));
  const days=Array.from({length:30},(_,i)=>{const d=new Date();d.setUTCDate(d.getUTCDate()-29+i);return d.toISOString().slice(0,10);});const max=Math.max(1,...days.map(d=>row.daily[d]||0));const chart=el('div',undefined,'chart');chart.setAttribute('aria-label','Acessos nos últimos 30 dias, detalhados na tabela abaixo');for(const day of days){const bar=el('div',undefined,'bar');bar.style.height=`${(row.daily[day]||0)/max*100}%`;bar.title=`${day}: ${row.daily[day]||0} acessos`;chart.append(bar);}const axis=el('div',undefined,'chart-labels');axis.append(el('span',days[0]),el('span',days[29]));content.append(el('h3','Últimos 30 dias · UTC'),chart,axis);
  const table=el('table');const head=el('tr');head.append(el('th','Data (UTC)'),el('th','Acessos'));table.append(head);for(const day of [...days].reverse()){const tr=el('tr');tr.append(el('td',day),el('td',number(row.daily[day]||0)));table.append(tr);}content.append(table);$('#details').showModal();}
$('#new').onclick=()=>openEditor();$('#refresh').onclick=()=>load();$('#search').oninput=render;$('#status').onchange=render;document.querySelectorAll('.close').forEach(button=>button.onclick=()=>button.closest('dialog').close());load();
