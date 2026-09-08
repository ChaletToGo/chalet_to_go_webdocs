# Busca, descoberta por IA e medição

## Estado e configuração

Implementação no repositório; publicação e ativação das contas são etapas separadas. Não há garantia de posição, indexação, citação em IA ou prazo de resultado.

Na consulta pública de 08/09/2026, o domínio sem www devolvia `noindex, nofollow`; www devolvia `index, follow`. O robots público tinha regras adicionais do Cloudflare. O código agora redireciona o hostname alternativo das páginas institucionais e dos arquivos de descoberta com 308, preservando caminho e query. O domínio principal é `SITE_URL=https://www.chalettogo.com`. Não altere para o domínio sem www sem atualizar redirecionamentos e cadastro nos buscadores. Localhost continua sem indexação.

Publicação: atualizar os arquivos na VPS e executar `sudo docker compose up -d --build --wait`. Confirmar o certificado dos dois hosts e eliminar regras antigas de cache de HTML/robots no CDN. O site já versiona CSS e JS pelo conteúdo. Validar com `python scripts/audit_seo.py https://www.chalettogo.com`. A auditoria é somente leitura.

## Conteúdo e palavras-chave

As 49 URLs do sitemap correspondem a sete páginas em sete idiomas. Todas as versões têm canonical próprio e oito alternates, incluindo x-default. A seleção de idioma continua explícita e não exige geolocalização. HTML é entregue pelo servidor, com navegação e conteúdo compreensíveis sem executar JavaScript.

Mapa inicial de intenção (hipóteses, sem volume de busca inventado):

| Página | Intenção principal | Próxima evolução com dados confirmados |
|---|---|---|
| / | chalés de madeira, fabricante de tiny house | Fotos próprias da primeira unidade e fabricação |
| /chales/basic | tiny house compacta, chalé compacto preço | Planta, medidas, ocupação e itens incluídos |
| /chales/standard | chalé modular familiar ou turístico | Especificações e opções reais |
| /chales/premium | chalé personalizado de madeira | Exemplos reais de personalização |
| /perguntas-frequentes | quanto custa um chalé, madeira e garantias | Prazos e condições confirmadas |
| /chales-para-hospedagem | chalés para pousadas e hospedagem | Casos reais; nenhuma promessa de retorno |
| /sobre | Chalet To GO, Chalettogo | Razão social/endereço documentados e perfis oficiais |

O nome empresarial informado é Chalet To GO. Endereço completo, documentos de garantia e certificação, plantas e prazos ainda não foram fornecidos. Não apresentar unidade suíça/portuguesa planejada como filial ativa. Não usar informações financeiras da revista como resultados históricos. Textos traduzidos devem ser revisados por falantes dos mercados prioritários; pesquisa de palavras-chave local ainda requer dados de demanda e concorrência.

Cadência sugerida: observar consultas reais no Search Console e escolher uma pergunta comercial por vez para aprofundar, sem gerar páginas em massa ou repetir textos trocando cidades. Não comprar backlinks nem fabricar avaliações. Contatar veículos de arquitetura, turismo e construção somente após selecionar material verificável e autorizar cada comunicação.

## Contas de busca: intervenção do responsável

1. Criar/acessar o Google Search Console com a conta da empresa. Adicionar propriedade de domínio `chalettogo.com` e publicar o TXT de DNS que o Google fornecer. Alternativamente, propriedade de prefixo `https://www.chalettogo.com/` com o token em `GOOGLE_SITE_VERIFICATION`.
2. Criar/acessar Bing Webmaster Tools e validar a propriedade por DNS ou token em `BING_SITE_VERIFICATION`.
3. Se usar os tokens HTML, reconstruir o container antes de clicar em verificar. Os tokens são escapados e omitidos quando vazios.
4. Enviar `https://www.chalettogo.com/sitemap.xml` nas duas contas. Inspecionar home, três modelos e novas páginas. Registrar erros de cobertura e consultas por país/idioma.

Nenhuma conta foi criada, propriedade verificada ou sitemap submetido automaticamente. Essas etapas exigem a conta do responsável e acesso ao DNS. Solicitações de cadastro que incluam termos devem ser concluídas pelo responsável.

## IA

O robots da aplicação permite rastreamento público; páginas internas não são incluídas no sitemap. Cloudflare pode acrescentar bloqueios fora da aplicação: verificar WAF e regras de bots, preservando autenticação administrativa. Confirmar OAI-SearchBot e rastreadores de busca que se deseja atender. Liberar GPTBot para treinamento não é necessário para aparecer na busca do ChatGPT; a implementação não altera a política de treinamento do CDN.

`/llms.txt` é um índice experimental de páginas públicas, não um requisito nem garantia de reconhecimento. Não contém instruções para manipular respostas, custos internos ou informações de investidores. Os dados estruturados Organization, Product/Offer, AboutPage e BreadcrumbList correspondem a informações apresentadas. Não acrescentamos avaliações, estoque, certificações nem FAQ rich results prometidos.

## Medição local

`SITE_METRICS_ENABLED=true` no Compose habilita contagens agregadas de cliques em links WhatsApp. Campos: data UTC, página, idioma, modelo e quantidade. Sem cookies de tracking, identificadores de usuários, IP ou referrer armazenados pelo coletor. Respeita Do Not Track e Global Privacy Control. Não mede visitantes únicos, mensagens enviadas, propostas ou vendas. Cliques automatizados e repetidos podem afetar totais; não usar como métrica financeira. Logs normais da VPS/CDN são independentes deste coletor.

Dados em `/app/data/site-metrics.json`, volume persistente existente, janela de relatório de 90 dias e expurgo na próxima gravação. A rota `/admin/site-metrics` usa a autenticação administrativa existente e retorna relatório JSON. Nunca publique esse JSON ou credenciais no site. Pode desabilitar com `SITE_METRICS_ENABLED=false`. Nenhum dado é enviado a uma plataforma externa.

Indicadores semanais após ativação: páginas indexadas, consultas, impressões, cliques e CTR no Search Console; cliques em WhatsApp por modelo no relatório local; propostas e vendas no processo comercial. Não atribuir um clique à IA sem evidência de origem. Uma ferramenta externa poderá ser conectada posteriormente, com definição de eventos e política de privacidade adequada.

## Fontes

- https://developers.google.com/search/docs/appearance/ai-features
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/appearance/structured-data/product-snippet
- https://developers.openai.com/api/docs/bots
