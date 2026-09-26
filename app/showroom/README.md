# Produto Chalé Básico

`/chales/basic` apresenta foto principal, 3D, planta e interiores em quatro abas acessíveis por teclado. Descrição e contato permanecem visíveis no desktop. A aba inicial usa imagens WebP responsivas; a biblioteca e o renderizador 3D só são iniciados ao selecionar o modelo. Trocar de aba preserva a cena e pausa o tour. Ferramentas avançadas estão em um painel recolhível.

## Conteúdo e navegação

Catálogo explícito em `routes.py`: modelos e fotos de `app/3d/chalé_basico`. Foto principal derivada de `app/shared/static/images/plano_basic.png`, com versões WebP em `static/basic-exterior-*`. Para adicionar modelos de produto no futuro, criar entradas de catálogo e associar as respectivas mídias.

Página com canonical, dados de produto, sitemap e indexação apenas no domínio oficial quando SITE_INDEXABLE permite. A coleção aponta o Basic para esta página em todos os idiomas, com navegação, identidade visual, preços e metadados compartilhados com o site. `/experiencia-3d` redireciona permanentemente para `/chales/basic`, preservando os parâmetros. O HTML mantém `private, no-store` devido ao contato regional. Nenhuma publicação foi feita automaticamente.

## Cache

`cache.ModelFiles` mantém representações gzip em memória no servidor, preparadas na inicialização para os dois GLBs do Básico. Limite LRU de 160 MiB por processo; reinícios recriam o cache. Arquivos acima desse tamanho são servidos normalmente. Compressão é executada fora do event loop e reutilizada. Suporte a ETag/304 e Range/206 preservado.

URLs usam versão por mtime em nanossegundos e tamanho. Versão atual recebe `Cache-Control: public, max-age=31536000, immutable`; URLs sem versão ou antigas exigem revalidação. Ao substituir um arquivo, preserve um timestamp novo. Navegador e caches intermediários podem reutilizar os bytes. Não existe CDN provisionada por este código.

Após carregar a foto principal, prefetch de baixa prioridade antecipa o exterior quando o navegador permite. É omitido em conexões 2G/3G ou economia de dados. Estrutura continua sob demanda. O primeiro acesso ainda precisa transferir o arquivo, e cada nova página precisa decodificar e enviar a geometria à GPU; cache não garante abertura instantânea. O GLB exterior atual tem aproximadamente 82 MB, portanto simplificação de malha/texturas continua recomendável para conexões lentas.

## Executar

```powershell
.venv/Scripts/python.exe -m uvicorn app.main:app --env-file .env --host 127.0.0.1 --port 8084
```

O `.env` é necessário para os contatos comerciais regionais existentes. Three.js 0.180.0 via jsDelivr precisa de internet. Testes: `pytest tests/test_showroom.py tests/test_site.py tests/test_sitemap.py tests/test_proxy_urls.py -q`.

A iluminação 3D inicia em Noturno. Para simular a política brasileira em localhost, use `LOCAL_PREVIEW_COUNTRY=BR` no `.env`; a opção só se aplica a host e cliente loopback. Produção continua usando o país informado pelo proxy confiável, nunca o idioma.
