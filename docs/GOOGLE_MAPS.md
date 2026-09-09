# Mapa da home

Endereço autorizado em 09/09/2026: Rte de Porrentruy 8, 2800 Delémont, Suíça.

A home incorpora Google Maps Embed API, com iframe responsivo, carregamento lazy,
link externo para o endereço e rótulos nos sete idiomas. O romanche usa inglês
nos controles internos do Google. O mapa não aparece sem chave configurada.

Defina `GOOGLE_MAPS_API_KEY` no `.env` da VPS e recrie o serviço Docker.
`GOOGLE_MAPS_ADDRESS` permite substituir o endereço. Não versionar a chave.
A chave usada no navegador é visível no HTML; no Google Cloud, habilite Maps
Embed API e restrinja a chave a essa API e aos referenciadores autorizados:
`https://www.chalettogo.com/*` e `https://chalettogo.com/*`.
Para testes locais, autorize separadamente o endereço localhost utilizado.

O arquivo recebido era um exemplo de Locator Plus com restaurantes em San
Francisco. Esses dados foram descartados; uma única localização usa a
incorporação oficial mais simples, sem o localizador de múltiplas lojas.

Documentação: https://developers.google.com/maps/documentation/embed/embedding-map
