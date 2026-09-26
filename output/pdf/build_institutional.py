from pathlib import Path
import base64
from reportlab.graphics.barcode.qr import QrCodeWidget

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf'
def asset(path,mime):
    return f'data:{mime};base64,'+base64.b64encode(Path(path).read_bytes()).decode()
logo=asset(ROOT/'app/shared/static/images/logo.svg','image/svg+xml')
portrait=asset('C:/Users/rafae/AppData/Local/Temp/codex-clipboard-ce90fd61-b1fa-40f5-be7a-469b66c7a834.jpg','image/jpeg')
exterior=asset(ROOT/'app/site/static/images/exterior-1440.webp','image/webp')
interior=asset(ROOT/'app/site/static/images/interior-1-1440.webp','image/webp')
url='https://www.chalettogo.com/'
qr=QrCodeWidget(url,barLevel='M'); qr.qr.make(); n=qr.qr.getModuleCount()
paths=' '.join(f'M{x+4},{y+4}h1v1h-1z' for y in range(n) for x in range(n) if qr.qr.isDark(y,x))
qsvg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n+8} {n+8}" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="white"/><path d="{paths}" fill="#0e2a20"/></svg>'
(OUT/'chalet-to-go-qrcode.svg').write_text(qsvg,encoding='utf-8')
html='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Chalet to Go • Apresentação</title>
<style>
@page{size:A4;margin:0}*{box-sizing:border-box}html,body{margin:0}body{font-family:Arial,Helvetica,sans-serif;color:#0e2a20;background:#f6f4f0;-webkit-print-color-adjust:exact;print-color-adjust:exact}.page{width:210mm;height:297mm;padding:12mm 14mm 11mm;overflow:hidden;background:#f6f4f0}
header{height:31mm;display:flex;justify-content:space-between;align-items:center;border-bottom:.25mm solid #bdb7aa}.brand{position:relative;width:43mm;height:28mm;overflow:hidden}.brand img{position:absolute;width:49mm;height:49mm;left:-6mm;top:-6mm}.header-copy{text-align:right;font-size:8pt;line-height:1.65;letter-spacing:1.3px;text-transform:uppercase}.header-copy b{font-weight:normal;color:#8b5e34;font-size:7.4pt}
.hero{display:grid;grid-template-columns:119mm 57mm;gap:6mm;height:79mm;padding-top:7mm;padding-bottom:6mm}h1{font-size:31pt;line-height:.99;letter-spacing:-1.7px;margin:0 0 4mm;font-weight:700}h1 span{color:#8b5e34}.intro{font-size:10pt;line-height:1.42;margin:0;max-width:112mm}.portrait{width:57mm;height:66mm;object-fit:cover;object-position:center 34%;display:block}
.gallery{display:grid;grid-template-columns:92mm 86mm;gap:4mm;height:56mm}.gallery img{width:100%;height:56mm;object-fit:cover;display:block}.gallery img:first-child{object-position:center bottom}.gallery .inside{object-position:center 65%}.caption{font-size:6.5pt;color:#556b4e;margin:2mm 0 5mm;line-height:1.2}
.details{display:grid;grid-template-columns:1fr 1fr 1fr;gap:5mm;border-top:.25mm solid #bdb7aa;padding-top:4mm;height:43mm}.details article+article{border-left:.25mm solid #bdb7aa;padding-left:5mm}.num{font-size:7pt;color:#8b5e34;letter-spacing:1px}.details h2{font-size:11.2pt;line-height:1.15;margin:2mm 0 2mm;letter-spacing:-.25px}.details p{font-size:8.5pt;line-height:1.38;margin:0}
.cta{height:46mm;background:#0e2a20;color:#f6f4f0;display:grid;grid-template-columns:1fr 35mm;gap:5mm;padding:6mm}.cta .eyebrow{font-size:6.9pt;letter-spacing:1.5px;margin:0 0 2mm;color:#bdb7aa}.cta h2{font-size:18pt;line-height:1.02;letter-spacing:-.6px;margin:0 0 2mm}.cta p{font-size:8.5pt;line-height:1.35;margin:0;max-width:115mm}.cta a{display:block;color:#f6f4f0;text-decoration:none;font-size:10pt;font-weight:bold;margin-top:2.3mm}.qr svg{width:33mm;height:33mm;display:block}.qr{text-align:center}.qr span{font-size:6.6pt;display:block;margin-top:1.3mm;color:#f6f4f0}
.foot{font-size:6pt;color:#556b4e;line-height:1.2;margin-top:3mm}
</style><main class="page"><header><div class="brand"><img src="LOGO" alt="Chalet to Go"></div><div class="header-copy">Chalés de madeira · Tiny houses<br><b>Madeira · Design · Natureza</b></div></header>
<section class="hero"><div><h1>Uma nova<br>maneira de<br><span>habitar.</span></h1><p class="intro">A Chalet to Go desenvolve chalés de madeira para morar, aproveitar os fins de semana ou receber hóspedes. Combinamos construção em madeira, componentes padronizados e possibilidades de personalização para cada projeto.</p></div><img class="portrait" src="PORTRAIT" alt="Garoto-propaganda da Chalet to Go"></section>
<section class="gallery"><img src="EXTERIOR" alt="Chalé de madeira sobre rodas, da galeria Chalet to Go"><img class="inside" src="INTERIOR" alt="Interior com cozinha, mezanino e luz natural, da galeria Chalet to Go"></section><p class="caption">Acervo visual Chalet to Go · Imagens ilustrativas. Configurações e acabamentos são definidos em cada projeto.</p>
<section class="details"><article><span class="num">01 / MATÉRIA-PRIMA</span><h2>O cuidado começa<br>na madeira.</h2><p>Pinus seco em estufa e tratado, com foco na qualidade e na resistência da madeira.</p></article><article><span class="num">02 / SEU PROJETO</span><h2>Espaços para<br>morar e receber.</h2><p>Dimensões, equipamentos e acabamentos podem se adaptar ao uso pretendido.</p></article><article><span class="num">03 / ATENDIMENTO</span><h2>Da sua ideia<br>à proposta.</h2><p>Alinhe com a equipe o local de instalação, a configuração, os itens incluídos e as garantias.</p></article></section>
<section class="cta"><div><p class="eyebrow">CONHEÇA A CHALET TO GO</p><h2>Seu chalé começa<br>com uma conversa.</h2><p>Aponte a câmera para o QR code. Explore a galeria,<br>conheça a empresa e fale com nossa equipe.</p><a href="https://www.chalettogo.com/">chalettogo.com ↗</a></div><div class="qr">QR<span>ACESSE O SITE</span></div></section>
<div class="foot">CHALET TO GO / Feitos para mover. Criados para inspirar.</div></main></html>'''
for key,val in [('LOGO',logo),('PORTRAIT',portrait),('EXTERIOR',exterior),('INTERIOR',interior),('>QR<','>'+qsvg+'<')]:
    html=html.replace(key,val)
(OUT/'chalet-to-go-institucional-a4.html').write_text(html,encoding='utf-8')
print('HTML and QR generated:',url)

