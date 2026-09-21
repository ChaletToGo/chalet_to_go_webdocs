# Preços iniciais por país

Edite `prices.json`. Cada plano (`basic`, `standard`, `premium`) tem três preços independentes: `BRL`, `EUR` e `CHF`. Não há conversão cambial automática.

Os valores iniciais foram mantidos em 40000, 65000 e 100000 nas três moedas, conforme solicitado. Altere cada valor para o preço comercial desejado. Use números sem separadores de milhar; para centavos, use ponto, por exemplo `42500.50`. Valores devem ser positivos, com no máximo duas casas decimais. Opcionalmente, `null` exibe “Sob consulta” e omite a oferta numérica dos metadados.

- Brasil (`BR`): real (`BRL`).
- Suíça (`CH`): franco suíço (`CHF`).
- Todos os demais países, incluindo localização desconhecida: euro (`EUR`).

O país vem da política existente: cabeçalho `CF-IPCountry` de proxy confiável com `TRUST_COUNTRY_HEADER=true`. O idioma, inclusive quando escolhido manualmente, altera os textos e a formatação, mas não determina a moeda. Sem localização confiável, o padrão é EUR.

Home, páginas dos planos e tabelas institucionais mostram “A partir de”, traduzido nos sete idiomas. Os metadados indicam o preço inicial (`lowPrice`), e `llms.txt` lista os valores configurados nas três moedas. O valor final e os itens incluídos são definidos na proposta. A revista e campanhas com condições próprias não usam esta tabela do site principal.

Publique o arquivo atualizado para alterar os preços no container. Nenhuma alteração de banco de dados é necessária.

O Compose de produção ativa a leitura do país explicitamente. Verifique `X-Site-Country` e `X-Price-Currency` na resposta HTTP para diagnosticar a origem da moeda, sem depender do idioma. Veja `docs/DEPLOY.md` para os requisitos de encaminhamento no Cloudflare/Nginx.
