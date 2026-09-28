from pathlib import Path

path=Path('app/shared/static/estudo-identidade/index.html')
html=path.read_text(encoding='utf-8-sig')
html=html.replace('Nove propostas','Doze propostas').replace('NOVE PROPOSTAS','DOZE PROPOSTAS').replace('nove propostas','doze propostas')
html=html.replace('Os seis conceitos A–F e os três modelos da primeira rodada, reunidos na mesma apresentação.','Os conceitos A–I e os três modelos da primeira rodada, reunidos na mesma apresentação. G, H e I exploram ilustração, ornamento e detalhe arquitetônico, com maior distância do minimalismo.')
html=html.replace('Os outros cinco caminhos têm liberdade formal.','Os demais conceitos têm liberdade formal.').replace('A–F','A–I')
concepts=[
('G','GRAVURA / EX-LIBRIS','Memória alpina','Uma vinheta de gravura reúne chalé, pinheiros e montanhas. O trabalho de madeira, os relevos e as massas de luz e sombra constroem uma marca de caráter narrativo.','A presença do desenho e a leitura das rodas entre os detalhes.'),
('H','ORNAMENTO / BRASÃO','Herança artesanal','Um emblema em losango, com composição simétrica e ornamentos alpinos. A arquitetura sobre rodas ocupa o centro de uma assinatura de caráter artesanal e decorativo.','A força do contorno e a abertura dos espaços entre os ornamentos.'),
('I','ARQUITETURA / ILUSTRAÇÃO','Arquitetura de ofício','Uma vista elevada revela volumes, encaixes, madeira e estrutura. O chalé se apresenta como objeto arquitetônico, com riqueza de construção e chassis aparente.','A legibilidade do conjunto e a separação de planos na redução.')
]
cards=''
for key,category,name,description,criterion in concepts:
    anchor=' id="novos-modelos"' if key=='G' else ''
    cards+=f'<article class="proposal"{anchor}><div class="proposal-title"><span>{key}</span><span>{category}</span></div><div class="logo-space" data-logo="{key}" data-ink="forest" role="img" aria-label="Conceito {key}: {name}"></div><h3>{name}</h3><p>{description}</p><div class="tradeoff"><b>Observar</b>{criterion}<a class="concept-original" href="/static/estudo-identidade/conceito-{key.lower()}.png" target="_blank" rel="noopener">Ver símbolo original ↗</a></div></article>'
html=html.replace('</article></div><div class="full-note">','</article>'+cards+'</div><div class="full-note">',1)
buttons=''.join(f'<button data-select="{key}" aria-pressed="false">{key} · {name}</button>' for key,_,name,_,_ in concepts)
html=html.replace('</div><p id="selection-status"',buttons+'</div><p id="selection-status"',1)
html=html.replace('versão 03','versão 04').replace('estudo.js?v=4','estudo.js?v=5')
path.write_text(html,encoding='utf-8')
