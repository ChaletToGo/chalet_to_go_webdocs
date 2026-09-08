# Chalet to Go — site e revista

Aplicação FastAPI e Jinja com projetos separados para o site institucional, a revista digital e futuras landing pages.

## Executar localmente

```powershell
uv run hello.py
```

Abra o site em [http://127.0.0.1:3000/](http://127.0.0.1:3000/) e a revista em [http://127.0.0.1:3000/revista](http://127.0.0.1:3000/revista).

## Docker Compose

```sh
docker compose up -d --build
docker compose ps
docker compose logs -f web
```

Acesse http://localhost:8080/revista. A porta padrão é diferente do servidor de desenvolvimento (3000). Para alterar, copie `.env.example` para `.env` e ajuste `APP_PORT`. `BIND_ADDRESS=0.0.0.0` permite acesso por outras máquinas; o padrão publica apenas no localhost.

A imagem usa Python 3.14, dependências do `uv.lock`, usuário sem privilégios, sistema de arquivos somente leitura e verificação de saúde em `/healthz`. Textos, imagens e fontes do PDF acompanham a imagem. O PDF é gerado em memória; o painel administrativo usa TinyDB no volume persistente `admin_data`. Depois de alterar conteúdo ou código, execute novamente `docker compose up -d --build`.

Para parar: `docker compose down`. Não adicione `-v` se quiser preservar os dados administrativos.

O workflow `.github/workflows/deploy.yml` faz deploy automático na VPS após pushes na `main`, via SSH, build Docker e verificação de saúde. Configure os secrets e os pré-requisitos descritos em [docs/DEPLOY.md](docs/DEPLOY.md) antes de ativá-lo.

Atrás de um proxy HTTPS, defina `FORWARDED_ALLOW_IPS` com o IP ou CIDR do proxy para que URLs e cookies usem o protocolo correto. O Compose usa a rede externa `nginxproxymanager_default` e o alias `chalet-web`; essa rede precisa existir antes da subida. O Proxy Host do Nginx Proxy Manager deve apontar para `http://chalet-web:8000`. O IP `172.22.0.2` observado hoje é dinâmico e não deve ser fixado. Se o nome da rede for diferente na VPS, defina `PROXY_NETWORK` no `.env`.

Na primeira implantação na VPS, confirme a rede com `sudo docker network ls` e, se necessário, ajuste `PROXY_NETWORK`. O container NPM e `web` precisam aparecer em `docker network inspect nginxproxymanager_default`.

O build segue o fluxo de instalação em etapas da [documentação oficial do uv para Docker](https://docs.astral.sh/uv/guides/integration/docker/).

## Estrutura

```text
app/
├── main.py                 # registra os projetos e recursos estáticos
├── site/                   # / — site institucional
│   ├── routes.py
│   ├── content.py          # conteúdo institucional nos sete idiomas
│   ├── templates/
│   └── static/
├── revista/                # /revista e /revista.pdf
│   ├── routes.py
│   ├── i18n.py
│   ├── content.py          # conteúdo exclusivo da revista
│   ├── financials.py       # orçamento e projeções da revista
│   ├── pdf_export.py
│   ├── locales/
│   ├── templates/
│   └── static/
├── landing_pages/          # um pacote por futura campanha
└── shared/
    ├── i18n.py             # negociação de idioma e preferência
    └── static/
        ├── brand/         # paleta compartilhada
        └── images/        # logomarca e biblioteca visual
```

O leitor possui 13 capítulos, sumário, navegação por botões, setas esquerda/direita e gestos horizontais em telas de toque. A rolagem vertical permanece livre para leitura de capítulos longos. A posição e as preferências de tamanho do texto e aparência são salvas localmente no navegador. Links como `/revista#brasil` abrem capítulos específicos.

O capítulo `/revista#resultados` apresenta preços e custos confirmados, cenários por quantidade e um simulador anual com premissas obrigatórias. Os valores comerciais e o orçamento estão centralizados em `app/revista/financials.py`. A metodologia e os limites das fontes estão em `docs/EDITORIAL_SOURCES.md`. Testes do cálculo: `node --test tests/finance.test.mjs`.

O conteúdo da revista fica em `app/revista/locales/*.json`, nos sete idiomas. O site tem conteúdo independente em `app/site/content.py`. A raiz `/` exibe o site institucional. Os endereços `/revista`, `/revista.pdf` e `/static/images/...` foram preservados. Os estilos e scripts da revista usam `/static/revista/...`; URLs antigas `/static/css/...` e `/static/js/...` continuam disponíveis por compatibilidade. A identidade visual está documentada em `IDENTIDADE_VISUAL.md`.

## Download para impressão

As configurações comerciais, o WhatsApp, as imagens dos planos e a implementação de SEO do site estão documentados em [docs/SITE_SEO.md](docs/SITE_SEO.md).

O botão de download no cabeçalho abre um seletor com os sete idiomas, pré-selecionando o idioma da leitura. `/revista.pdf?lang=fr`, por exemplo, baixa a edição francesa sem modificar a preferência de idioma da revista. O PDF é A4, com fontes incorporadas, margens e paginação próprias; inclui o conteúdo editorial, orçamento, preços e cenários estáticos, mas exclui a calculadora e seus resultados.

A geração usa ReportLab em `app/revista/pdf_export.py`, sem navegador ou serviço externo. Os arquivos são gerados em memória e armazenados em cache por idioma até reiniciar o processo. Após alterações nos textos ou imagens, reinicie o servidor para renovar o cache. As dependências estão no `pyproject.toml`/`uv.lock`; `uv sync` prepara o ambiente. Os testes de desenvolvimento usam pypdf para validar os sete arquivos, o formato, o idioma e a ausência dos elementos interativos.

## Idioma e localização

O seletor de idioma mantém o capítulo atual e grava uma preferência no navegador por um ano. Links como `/revista?lang=fr#historia` abrem uma tradução específica. A opção de idioma automático remove a preferência gravada.

A escolha explícita e a preferência salva têm prioridade sobre a detecção. A política por país é Brasil → pt-BR, Suíça → inglês, Itália → italiano, França → francês, Alemanha → alemão e Portugal → pt-PT. Os visitantes suíços podem escolher inglês, romanche, alemão, italiano ou francês; as duas variantes de português também permanecem disponíveis.

Para detecção de país em produção, habilitar IP Geolocation no Cloudflare e definir `TRUST_COUNTRY_HEADER=true` na aplicação somente atrás do proxy controlado, que deve encaminhar o `CF-IPCountry` sobrescrito pelo Cloudflare. O acesso direto à origem deve estar restrito. Sem esse cabeçalho (inclusive em localhost), a aplicação usa `Accept-Language`; o idioma do navegador é uma alternativa, não prova de localização. Países detectados fora da política usam inglês por padrão. A aplicação não solicita GPS nem envia IPs a serviços externos.

Detalhes de manutenção em `app/revista/locales/README.md`. Testes: `.venv/Scripts/python.exe -m unittest discover -s tests -v` no Windows, ou `uv run python -m unittest discover -s tests -v`.
