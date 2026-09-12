# Cartões virtuais

Cada colaborador possui um JSON diretamente nesta pasta. `rafael_lima.json` é renderizado em `/card/rafael_lima`. Basta adicionar ou editar o arquivo: a leitura acontece a cada acesso, sem novas rotas ou reinício do Python.

Copie `rafael_lima.json`, renomeie usando letras minúsculas sem acentos, números, `_` ou `-`, e preencha os dados. JSON usa aspas duplas e não aceita comentários. `nome` e `cargo` são obrigatórios. `empresa` tem como padrão Chalet to Go. Os demais campos são opcionais e podem ser omitidos ou deixados como `""`; as ações correspondentes ficam ocultas.

- `telefone` e `whatsapp`: inclua código do país e DDD (por exemplo, `+55 (11) 99999-9999`). WhatsApp é configurado separadamente.
- `email`: endereço de e-mail.
- `site`, `instagram`, `linkedin`: URLs completas iniciadas por `https://`.
- `localizacao`: cidade/região exibida no cabeçalho.
- `sobre`: apresentação curta, em uma linha de texto.

O exemplo de Rafael não contém telefone ou e-mail reais. Preencha antes de distribuir o cartão. Os dados cadastrados são públicos: não inclua dados internos. Os JSONs não são servidos como arquivos estáticos.

O botão **Salvar contato** baixa `/card/rafael_lima/contact.vcf`, compatível com agendas. **Compartilhar cartão** abre o compartilhamento nativo quando disponível, com alternativa para copiar o link. Cartões inexistentes retornam 404; arquivos inválidos retornam um erro genérico 500 e registram detalhes no log do servidor.

## Docker

O Compose monta esta pasta como somente leitura dentro do contêiner. Depois de recriar o serviço com a nova configuração, adicionar/editar JSONs no host atualiza os cartões no próximo acesso. Em deploys que usam apenas a imagem, sem esse volume, é necessário reconstruir e publicar a imagem para incluir novos arquivos.
# Mapas e idiomas

Quando `localizacao` contém um endereço, o cartão exibe “Abrir no mapa”. O link HTTPS do Google Maps pesquisa o endereço e pode abrir o aplicativo instalado, conforme as configurações do dispositivo; caso contrário, abre a versão web. O endereço também é incluído no arquivo de contato `.vcf`.

A interface suporta `pt-BR`, `pt-PT`, `en`, `de`, `fr`, `it` e `rm`. A prioridade é: parâmetro `?lang=`, preferência salva, país informado pelo proxy confiável e idioma do navegador. O seletor permite mudar de idioma ou voltar a Automático. Links compartilhados não fixam o idioma, permitindo que cada destinatário receba sua própria versão.

Para usar localização por país, habilite IP Geolocation no Cloudflare e `TRUST_COUNTRY_HEADER=true` no `.env` da VPS, apenas quando o proxy controlar o cabeçalho `CF-IPCountry`. Sem isso, o idioma do navegador é utilizado; não há solicitação de GPS. Recrie o contêiner após alterar variáveis de ambiente.

Textos pessoais podem ser traduzidos pelo campo opcional `traducoes` em cada JSON:

```json
"traducoes": {
  "en": {"cargo": "Sales manager", "sobre": "Contact our team."},
  "fr": {"cargo": "Responsable commercial", "sobre": "Contactez notre équipe."}
}
```

Os campos `cargo` e `sobre` originais são o fallback para traduções ausentes. Nome, empresa, endereço e dados de contato são preservados. O `.vcf` usa o cargo e a apresentação do idioma selecionado. JSONs existentes continuam funcionando sem alterações.
## Foto opcional

Adicione ao JSON do cartão o campo `"foto": "static/images/rafael.jpg"` e coloque a imagem em `app/virtual_cards/static/images/rafael.jpg`.
Use o caminho do **arquivo**, incluindo sua extensão. Também são aceitos `images/rafael.jpg`, `/static/cards/images/rafael.jpg` e `app/virtual_cards/static/images/rafael.jpg`.

A foto aparece circular, acima do nome. São aceitos JPG, JPEG, PNG, WebP, AVIF e GIF. O arquivo deve estar dentro de `app/virtual_cards/static`; links externos não são aceitos. Prefira caminhos relativos para funcionar tanto no Windows quanto na VPS e no Docker.

Sem o campo, com `"foto": ""` ou com arquivo inexistente, o cartão mantém a apresentação sem foto. O volume Docker existente inclui essa pasta.
