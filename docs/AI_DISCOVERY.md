# Descoberta da Chalet To GO — 09/09/2026

## Implementado

- Nome WebSite padronizado como Chalet To GO, alternativa Chalettogo.
- Endereço confirmado visível no rodapé e na página Sobre, também em Organization/PostalAddress.
- Informações empresariais e comerciais no índice experimental llms.txt.
- Perfis oficiais configuráveis por SITE_OFFICIAL_PROFILES, apresentados como links e sameAs; sem perfis inventados. O usuário informou que ainda não há redes sociais.
- Auditoria pública reproduzível: `python scripts/audit_discovery.py`.

## Protocolo de verificação

Registrar data, ferramenta, idioma, país/contexto, pergunta, uso de busca, URL citada e fatos corretos/incorretos.
Usar: “O que é a Chalet To GO?”, “Quais os modelos e preços da Chalet To GO?”, “Quais empresas fabricam chalés de madeira?”.
O último teste mede recomendação; os dois primeiros medem descoberta e precisão.
Não tratar uma resposta ou ausência isolada como resultado de todas as IAs.
Em 09/09, uma consulta na ferramenta de busca disponível por marca + domínio retornou zero resultados. Isso não contradiz a home encontrada no Google anteriormente.

## Cloudflare

Consultar eventos de segurança e logs de acesso ao domínio; buscar os rastreadores de busca desejados, caminho, status e regra acionada. Verificar identidade com IPs oficiais, não apenas User-Agent. Um teste HTTP comum ou com nome de bot não comprova acesso do rastreador real.
Preservar bloqueios de administração, autenticação e política de treinamento. OAI-SearchBot é distinto de GPTBot. Não desligar WAF ou proteção de bots de forma global.

## Materiais a produzir com a empresa

1. Fichas aprovadas dos três modelos: dimensões, plantas, itens incluídos, prazo e condições de entrega.
2. Fotos e vídeos reais da primeira unidade, com data, autoria e identificação de imagens conceituais.
3. Apresentação da equipe com nomes, funções e experiência autorizados.
4. Criar perfis oficiais com nome, domínio e contato consistentes; publicar descrição baseada na página Sobre.
5. Propor publicações a parceiros reais com informações verificáveis; não comprar menções nem inventar avaliações.

Texto base para perfis: “A Chalet To GO desenvolve chalés de madeira e tiny houses para moradia, lazer e hospedagem. Conheça os modelos Basic, Standard e Premium e solicite uma proposta em www.chalettogo.com.”

## Limites

Não há prazo ou garantia de inclusão. llms.txt não é cadastro nem requisito para Google AI. Uma marcação estruturada não substitui fatos verificáveis ou referências externas. Publicação na VPS e alterações em plataformas externas devem ser registradas separadamente da implementação local.

Fontes: https://developers.google.com/search/docs/appearance/ai-features e https://developers.openai.com/api/docs/bots
