import {project} from './finance-model.mjs';
const form = document.querySelector('#finance-form');
const t = JSON.parse(document.querySelector('#finance-i18n').textContent);
const products = JSON.parse(document.querySelector('#finance-products').textContent);
const formatter = new Intl.NumberFormat(document.documentElement.lang, {maximumFractionDigits:0});
const number = n => formatter.format(n);
const status = document.querySelector('#finance-status');
const results = document.querySelector('#finance-results');
const clear = () => {results.hidden = true; status.textContent = t.unsupplied;};
form.addEventListener('input', clear);
form.addEventListener('reset', clear);
form.addEventListener('submit', event => {
  event.preventDefault();
  try {
    const data = new FormData(form);
    const product = products[Number(data.get('model'))];
    const forecast = project({price:product.price, variableCost:product.production + Number(data.get('extra')),
      monthlyCapacity:Number(data.get('capacity')), years:[1,2,3].map(year => ({units:Number(data.get(`units${year}`)), fixedCosts:Number(data.get(`fixed${year}`))}))});
    const tbody = document.querySelector('#finance-rows');
    tbody.replaceChildren();
    forecast.rows.forEach(row => {
      const tr = document.createElement('tr');
      [row.year,row.units,row.revenue,row.totalCosts,row.result,row.breakEven].forEach(value => {
        const td = document.createElement('td'); td.textContent = value === null ? t.no_breakeven : number(value); tr.append(td);
      }); tbody.append(tr);
    });
    const chart = document.querySelector('#finance-chart'); chart.replaceChildren();
    const title = document.createElement('h4'); title.textContent = `${t.chart_result} · CHF`; chart.append(title);
    const max = Math.max(1,...forecast.rows.map(row => Math.abs(row.result)));
    forecast.rows.forEach(row => {
      const line = document.createElement('div'); line.className = 'result-line';
      const label = document.createElement('span'); label.textContent = `${t.year} ${row.year} · CHF ${number(row.result)}`;
      const track = document.createElement('div'); track.className = 'result-track';
      const bar = document.createElement('i'); bar.style.width = `${Math.abs(row.result)/max*50}%`;
      bar.style.left = row.result < 0 ? `${50-Math.abs(row.result)/max*50}%` : '50%';
      if (row.result < 0) bar.className = 'negative'; track.append(bar); line.append(label,track); chart.append(line);
    });
    const scale = document.createElement('p'); scale.className = 'result-scale';
    for (const value of [-max,0,max]) {const span=document.createElement('span'); span.textContent=number(value); scale.append(span);} chart.append(scale);
    document.querySelector('#finance-total').textContent = `${t.cumulative}: CHF ${number(forecast.totalResult)}`;
    status.textContent = forecast.rows.some(row => row.breakEven !== null && row.breakEven > forecast.annualCapacity) ? t.capacity_warning : t.results_title;
    results.hidden = false;
  } catch {results.hidden = true; status.textContent = t.invalid;}
});
