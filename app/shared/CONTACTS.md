# Contatos comerciais por país

Edite `contact_numbers.json`. As chaves são códigos de país: BR (Brasil), CH (Suíça), DE (Alemanha), IT (Itália), PT (Portugal) e FR (França).

- `number`: número com código internacional, por exemplo `"+41 79 191 46 38"`.
- `env`: nome da variável do `.env` que fornece o número, em vez de `number`.
- `name`: identificação para facilitar a edição; não interfere na seleção.
- `default`: contato usado para países não cadastrados ou localização indisponível.

Use apenas uma fonte (`number` ou `env`) por entrada. Brasil e o padrão usam `WHATSAPP_NUMBER`, atualmente `5531984748754`. Para adicionar um país, acrescente uma entrada em `countries`. Publique a alteração para atualizar o arquivo dentro do container; não é necessário alterar o banco de dados.

A seleção usa `CF-IPCountry` somente quando `TRUST_COUNTRY_HEADER=true`, seguindo a política de localização existente. O proxy controlado deve fornecer/sobrescrever esse cabeçalho com o país real e impedir que clientes o forjem. Sem essa infraestrutura, mantenha a confiança desativada: o contato padrão será usado. Não inferimos localização a partir do idioma escolhido, do cookie de idioma ou da língua do navegador.

A política vale para CTAs comerciais da home, páginas institucionais e de produtos, contato, showroom, Eco Villa e telefone nos metadados. Os cartões pessoais e os links dos leads mantêm os números dos respectivos contatos. As páginas variam por país e não devem ser armazenadas em cache compartilhado.
