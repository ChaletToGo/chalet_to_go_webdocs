# Estudo de identidade — Chalet To Go

## Versão 03 — nove propostas na apresentação principal

Os três PNGs `referencia-01.png`, `referencia-02.png` e `referencia-03.png` também estão na galeria principal, identificados como Modelo inicial 01/02/03, primeira rodada. São opções completas nos seletores e nas aplicações Snow/Forest/Wood, junto dos seis conceitos A–F. Seus desenhos e letras raster originais foram preservados, sem assinatura vetorial adicional. A marca SVG original e o arquivo histórico continuam disponíveis.

Verificação: os nove seletores foram acionados em desktop 1280 px e móvel 390 px, atualizando as três aplicações com os PNGs correspondentes; galeria com nove cartões, sem overflow horizontal em 390 px. JavaScript e CSS específicos usam versão de URL para evitar mistura com arquivos antigos do cache.

## Rodada 02 — seis conceitos distintos

A página principal agora mostra A Casa em linha, B Abrigo essencial, C Ofício alpino, D Arquitetura em viagem, E Destino aberto e F Forma em movimento. Apenas A é uma continuidade formal da marca existente. C e D usam a referência artesanal fornecida; B, E e F foram gerados livremente. As imagens são estudos, nenhuma alternativa aprovada. O conjunto de prompts está em `PROMPTS-RODADA-02.md`.

Arquivo canônico identificado e exibido sem alteração: `app/shared/static/images/logo.svg`, usado em `_header.html`, `base.html`, `revista.html`, `card.html`, administração e Eco Villa. `assinatura-original.svg` é uma derivação apenas dos grupos de contornos das letras, recoloridos em Forest; não foi reconstruída com fontes presumidas. O original continua com suas cores próprias. Os PNGs dos símbolos têm seus canais alpha preservados; um filtro de apresentação simula tinta única no navegador.

A rodada anterior foi preservada em `rodada-01.html` e `rodada-01.js`, com rótulos corrigidos para identificar as três alternativas como ilustrações. A referência artesanal foi copiada para `referencia-artesanal.png`.

Verificação da rodada 02: página e ativos respondem HTTP 200, comparação visual em 1280 px e 390 px, seis seletores atualizam as três aplicações correspondentes, sem imagens HTML quebradas ou overflow horizontal em 390 px. O arquivo de produção `logo.svg` não foi alterado. Publicação externa não realizada.

## Histórico da rodada 01

Apresentação independente: `/static/estudo-identidade/index.html`. Usa o servidor FastAPI existente, sem alterar rotas, templates ou logomarca de produção. Não publicada externamente.

Fontes de identidade: `IDENTIDADE_VISUAL.md` e `app/shared/static/brand/brand.css`. Cores compartilhadas por importação direta. Tipografia disponível: Arial, Helvetica Neue, Helvetica, sans-serif. Direção tipográfica documentada: Söhne Breit e Neue Haas Grotesk Text, sem arquivos/licenças fornecidos.

Referências 01 e 02 fornecidas na tarefa. Referência 03 produzida com a ferramenta integrada image_gen, usando a referência 02 e a marca oficial como entradas. Todos os PNGs foram copiados para este diretório. O recorte de exibição e a simulação monocromática são feitos por SVG no navegador; originais preservados. Não são vetores finais, provas de impressão ou comprovação de fonte exata. As alegações presentes nos mockups precisam de validação antes de uso comercial.

Prompt final da referência 03:

> Use case: logo-brand. Create reference 3 for Chalet To Go, a single centered full logo on a flat light cream background, landscape 1536x1024. Input 1 is reference 2, preserve the same chalet three-quarter perspective, two clear trailer wheels, pine at left and mountains behind, same proportions and brand family. Increase illustrative richness one controlled step: carefully drawn timber grain, architectural joints and window frames, slightly richer pine branch engraving, restrained mountain facet hatching. No extra objects, scenery, landscape, decorative frame, shadows or gradients. Professional confident one-color forest green #0e2a20 engraving and cream negative space, lines robust enough for monochrome. Input 2 is official brand for lettering reference only; use its widely tracked sans-serif lettering hierarchy, do not use its old house icon. Exact text: CHALET / TO GO / SWISS [cross in square] MADE / BUILT TO MOVE. MADE TO INSPIRE. Keep text correctly spelled and legible. This is a study, not a claim of exact font matching. Only one logo, generous clear margin, no mockup or layout panels.
