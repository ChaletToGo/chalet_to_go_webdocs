# Revista — leitor web

Protótipo de um leitor editorial responsivo, feito com FastAPI e Jinja.

## Executar localmente

```powershell
uv run hello.py
```

Abra [http://127.0.0.1:3000/revista](http://127.0.0.1:3000/revista).

## Docker Compose

```sh
docker compose up -d --build
docker compose ps
docker compose logs -f web
```

Acesse http://localhost:8080/revista. A porta padrão é diferente do servidor de desenvolvimento (3000). Para alterar, copie `.env.example` para `.env` e ajuste `APP_PORT`. `BIND_ADDRESS=0.0.0.0` permite acesso por outras máquinas; o padrão publica apenas no localhost.

A imagem usa Python 3.14, dependências do `uv.lock`, usuário sem privilégios, sistema de arquivos somente leitura e verificação de saúde em `/healthz`. Textos, imagens e fontes do PDF acompanham a imagem. Não há banco de dados ou volume persistente: o PDF é gerado em memória. Depois de alterar conteúdo ou código, execute novamente `docker compose up -d --build`.

Para parar: `docker compose down`. O Compose não executa deploy nem altera o GitHub Actions.

Atrás de um proxy HTTPS, defina `FORWARDED_ALLOW_IPS` com o IP ou CIDR do proxy para que URLs e cookies usem o protocolo correto. Para Cloudflare, veja a seção de localização abaixo. Se o Nginx Proxy Manager também estiver em Docker, conecte os serviços a uma rede Docker compartilhada e use `web:8000` como destino; `127.0.0.1` dentro do proxy aponta para o próprio container.

O build segue o fluxo de instalação em etapas da [documentação oficial do uv para Docker](https://docs.astral.sh/uv/guides/integration/docker/).

## Estrutura

```text
app/
├── main.py                 # aplicação e rota /revista
├── templates/              # páginas Jinja
│   └── revista.html
└── static/
    ├── css/main.css        # layout responsivo do leitor
    └── js/reader.js        # paginação e interações
```

O leitor possui 13 capítulos, sumário, navegação por botões, setas esquerda/direita e gestos horizontais em telas de toque. A rolagem vertical permanece livre para leitura de capítulos longos. A posição e as preferências de tamanho do texto e aparência são salvas localmente no navegador. Links como `/revista#brasil` abrem capítulos específicos.

O capítulo `/revista#resultados` apresenta preços e custos confirmados, cenários por quantidade e um simulador anual com premissas obrigatórias. Os valores comerciais e o orçamento estão centralizados em `app/financials.py`. A metodologia e os limites das fontes estão em `docs/EDITORIAL_SOURCES.md`. Testes do cálculo: `node --test tests/finance.test.mjs`.

O conteúdo editorial e os textos da interface ficam em `app/locales/*.json`, com versões completas em português brasileiro, português de Portugal, inglês, alemão, francês, italiano e romanche (Rumantsch Grischun). A identidade visual está documentada em `IDENTIDADE_VISUAL.md`; as fontes usadas nesta versão são alternativas locais, sem dependência de serviços externos. A rota `/` redireciona para a revista. Sem JavaScript, todos os capítulos são apresentados em leitura contínua e os links de idioma continuam disponíveis.

## Download para impressão

O botão de download no cabeçalho abre um seletor com os sete idiomas, pré-selecionando o idioma da leitura. `/revista.pdf?lang=fr`, por exemplo, baixa a edição francesa sem modificar a preferência de idioma da revista. O PDF é A4, com fontes incorporadas, margens e paginação próprias; inclui o conteúdo editorial, orçamento, preços e cenários estáticos, mas exclui a calculadora e seus resultados.

A geração usa ReportLab em `app/pdf_export.py`, sem navegador ou serviço externo. Os arquivos são gerados em memória e armazenados em cache por idioma até reiniciar o processo. Após alterações nos textos ou imagens, reinicie o servidor para renovar o cache. As dependências estão no `pyproject.toml`/`uv.lock`; `uv sync` prepara o ambiente. Os testes de desenvolvimento usam pypdf para validar os sete arquivos, o formato, o idioma e a ausência dos elementos interativos.

## Idioma e localização

O seletor de idioma mantém o capítulo atual e grava uma preferência no navegador por um ano. Links como `/revista?lang=fr#historia` abrem uma tradução específica. A opção de idioma automático remove a preferência gravada.

A escolha explícita e a preferência salva têm prioridade sobre a detecção. A política por país é Brasil → pt-BR, Suíça → inglês, Itália → italiano, França → francês, Alemanha → alemão e Portugal → pt-PT. Os visitantes suíços podem escolher inglês, romanche, alemão, italiano ou francês; as duas variantes de português também permanecem disponíveis.

Para detecção de país em produção, habilitar IP Geolocation no Cloudflare e definir `TRUST_COUNTRY_HEADER=true` na aplicação somente atrás do proxy controlado, que deve encaminhar o `CF-IPCountry` sobrescrito pelo Cloudflare. O acesso direto à origem deve estar restrito. Sem esse cabeçalho (inclusive em localhost), a aplicação usa `Accept-Language`; o idioma do navegador é uma alternativa, não prova de localização. Países detectados fora da política usam inglês por padrão. A aplicação não solicita GPS nem envia IPs a serviços externos.

Detalhes de manutenção em `app/locales/README.md`. Testes: `.venv/Scripts/python.exe -m unittest discover -s tests -v` no Windows, ou `uv run python -m unittest discover -s tests -v`.
