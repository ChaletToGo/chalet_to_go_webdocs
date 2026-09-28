# Maquete interativa da Eco Villa

Landing integrada: `/eco-villa-natal`. Prévia independente: `/eco-villa-natal/maquete`.

O modelo é construído em Three.js, sem downloads de GLB ou dependência do Meshy. A geometria inclui seis chalés Basic com bases fixas em contato com o terreno, sem rodas, eixos ou chassis. A implantação foi ampliada lateralmente para receber duas unidades adicionais. A cena é conceitual e não representa um levantamento topográfico nem um projeto executivo do Basic.

## Referências da reconstrução

- `app/showroom/static/basic-exterior-960.webp` e `app/shared/static/images/plano_basic.png`: fachada equivalente à imagem enviada; tábuas horizontais, porta central, duas janelas frontais, telhado de duas águas com juntas metálicas, janelas superiores na água lateral e esquadrias escuras.
- `app/3d/chalé_basico/planta_chale_basico.jpg`: sala frontal, cozinha à esquerda, escada à direita, banheiro ao fundo e dormitório no mezanino.
- `app/3d/chalé_basico/interior_basico.jpg`: referência de materiais e organização interna.

As proporções adotadas (3,8 × 8 m por chalé, cumeeira de 5,15 m; terreno de estudo ampliado para 52 × 24 m) são hipóteses de modelagem visual. Não são medidas extraídas de uma planta cotada. A base contínua é uma representação, não um dimensionamento de fundação. Os decks preservam o conceito da implantação original.

“Ver interiores” remove a cobertura e a envoltória; “Ver térreo” oculta temporariamente o mezanino para revelar cozinha e banheiro. As seis unidades podem ser selecionadas tanto pelos botões quanto pela cena. A imagem alternativa sem WebGL também representa seis chalés.

## Integração e rolagem

A identidade da landing usa `shared/static/brand/brand.css`, a mesma fonte de cores e tipografia do website. `villa-brand.css` adapta o padrão editorial do site e da revista: brasão, fundo papel, títulos sem serifa, destaque madeira, divisórias finas e controles planos. O fundo diurno do canvas lê `--villa-scene-background` para acompanhar essa paleta.

A landing inclui `_maquete_viewer.html` diretamente na abertura, sem iframe. O palco ocupa `100dvh`, fica fixo durante a sequência de rolagem e desloca a câmera com o progresso. `villa-scroll.js` controla essa sequência e revela as seções seguintes com IntersectionObserver. A preferência por movimento reduzido desativa o percurso animado e as transições de entrada.

Por padrão, a rolagem e o gesto vertical permanecem livres sobre a maquete. “Explorar a maquete” habilita OrbitControls e a seleção das unidades; “Continuar a leitura” restaura os telhados, libera a rolagem e segue para o conceito. O visualizador independente mantém interação direta.

A prancha antiga foi removida da landing. Seus sete ambientes e especificações aparecem no conteúdo. As áreas de 720 m² e 160 m² estão explicitamente vinculadas ao estudo original de quatro cabanas. O print do mapa foi substituído por um link de busca no Google Maps pelo nome do sítio; o link não é um ponto confirmado do terreno.

## Incorporação em outras páginas

```html
<iframe
  src="/eco-villa-natal/maquete?embed=1"
  title="Explore a maquete interativa da Eco Villa"
  loading="lazy"
  allow="fullscreen"
  style="display:block;width:100%;height:720px;border:0;border-radius:12px"
></iframe>
```

O modo embed remove o cabeçalho e a introdução. Para celular, manter ao menos 600px de altura. O carregamento deve ocorrer próximo da área visível; o iframe lazy evita competir com a imagem principal da landing.

## Ajustes e dependências

- `static/maquete.js`: `LAYOUT` define terreno e centros das seis unidades; controla navegação, paisagismo, seleção e iluminação.
- `static/basic-chalet.js`: reconstrói cada Basic e seus grupos removíveis (envoltória, cobertura e mezanino). Reúne tábuas e esquadrias em `InstancedMesh` para reduzir chamadas de desenho. `BASIC` documenta as proporções conceituais; alterar dimensões exige compatibilizar o mobiliário e as aberturas.
- `static/implantacao-basic-seis.svg`: planta esquemática alternativa ao visualizador, sem escala.
- `static/maquete.css`: layout responsivo dos controles e painel.
- Three.js 0.180.0 e OrbitControls carregados do jsDelivr, na mesma versão usada no showroom. Internet e WebGL2 são necessários; em falha, permanece a planta de referência.
- Renderização por demanda, resolução limitada a 1,7x e suspensão fora da área visível ou com a aba oculta. Movimento reduzido respeitado nos deslocamentos de câmera.
- Botões acessíveis para seleção, vistas e zoom, além dos gestos de mouse e toque. Seleção comercial e disponibilidade não são inferidas.
- A página de prévia tem `noindex, nofollow`.

Antes de publicar: confirmar dimensões, compatibilizar a arquitetura com a unidade Basic definitiva, confirmar o link exato da localidade e validar em aparelhos móveis reais. A integração está no código local; esta entrega não publica o site.
