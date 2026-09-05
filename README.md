# Revista — leitor web

Protótipo de um leitor editorial responsivo, feito com FastAPI e Jinja.

## Executar localmente

```powershell
uv run hello.py
```

Abra [http://127.0.0.1:3000/revista](http://127.0.0.1:3000/revista).

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

O leitor possui 10 capítulos, sumário, navegação por botões, setas esquerda/direita e gestos horizontais em telas de toque. A rolagem vertical permanece livre para leitura de capítulos longos. A posição e as preferências de tamanho do texto e aparência são salvas localmente no navegador. Links como `/revista#brasil` abrem capítulos específicos.

O conteúdo editorial fica em `app/content.py`. A identidade visual está documentada em `IDENTIDADE_VISUAL.md`; as fontes usadas nesta versão são alternativas locais, sem dependência de serviços externos. A rota `/` redireciona para a revista. Sem JavaScript, todos os capítulos são apresentados em leitura contínua.
