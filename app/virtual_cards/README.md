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
