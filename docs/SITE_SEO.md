# Site institucional

O site mantém textos, preços e descrições em `app/site/content.py`, sem importar o conteúdo ou as finanças da revista. As páginas `/chales/basic`, `/chales/standard` e `/chales/premium` apresentam os produtos individualmente. Todos os botões comerciais abrem o WhatsApp com mensagem no idioma selecionado; não enviam mensagens automaticamente.

Configuração no Compose: `SITE_URL=https://www.chalettogo.com`, `SITE_INDEXABLE=true` e `WHATSAPP_NUMBER=5538998840910`. Use apenas dígitos com código do país no telefone. O domínio público deve corresponder ao domínio atendido pelo proxy. Hosts locais recebem `noindex` e robots bloqueado; ambientes de homologação podem definir `SITE_INDEXABLE=false`.

Cada página tem título, descrição, canonical, alternates hreflang, Open Graph e dados estruturados. O sitemap contém 49 URLs: sete páginas em sete idiomas. Os dados Product/Offer reproduzem os preços exibidos em CHF, sem inventar estoque, avaliações ou certificações. Após publicar, cadastrar o domínio e enviar `/sitemap.xml` no Google Search Console; esse envio não foi realizado pelo projeto. Indexação e posição dependem do Google e não são garantidas.

Referências: [Guia de SEO do Google](https://developers.google.com/search/docs/fundamentals/seo-starter-guide), [sites multilíngues](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites) e [dados estruturados de produtos](https://developers.google.com/search/docs/appearance/structured-data/product-snippet).

As imagens responsivas WebP são geradas com `python scripts/optimize_site_images.py` a partir da biblioteca original, preservada. Reexecutar ao trocar imagens. O selo fornecido foi aplicado sobre cada imagem de plano por solicitação do responsável; isso não constitui validação documental da certificação. O site oficial de [Suisse Garantie](https://www.suissegarantie.ch/) descreve uma marca de produtos agrícolas; a autorização para este uso ainda precisa ser documentada pelo responsável. Não foi adicionada uma declaração textual de certificação.

As garantias reproduzem os dados fornecidos pelo responsável: madeira suíça, cobertura opcional Generali de até 20 anos com valor adicional; madeira brasileira, seis meses. Países, condições e documento da seguradora não foram fornecidos. Os textos orientam a consultar condições e disponibilidade na proposta.
