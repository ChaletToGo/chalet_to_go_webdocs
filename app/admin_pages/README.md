# Administração e ferramentas

Abra `/admin` para a visão geral. A área **Ferramentas** reúne QR Codes (`/admin/qrcodes`), Leads (`/admin/leads`) e Métricas do site (`/admin/metrics`). Configure `ADMIN_USERNAME` e `ADMIN_PASSWORD` no ambiente: o navegador solicitará as credenciais via HTTP Basic. Sem configuração, o painel fica indisponível (503). Use HTTPS em produção. Feche a sessão do navegador para descartar as credenciais salvas; não há contas individuais ou botão de logout nesta versão.

Configure `QR_BASE_URL` com a origem pública definitiva (ex.: `https://www.chalettogo.com`). Cada código guarda seu endereço permanente no momento da criação. Alterar essa variável só afeta novos códigos: mantenha o domínio antigo funcionando para códigos já impressos. Na execução local, exporte as variáveis no shell ou use `uv run uvicorn app.main:app --env-file .env`; o Compose carrega `.env` automaticamente.

O painel permite criação, pesquisa por nome/campanha, filtro de status, edição de destino, pausa/reativação, expiração opcional, quatro cores, download PNG/SVG com assinatura da marca, cópia do link, exportação CSV e estatísticas diárias dos últimos 30 dias. O histórico diário completo é preservado no banco. Links pausados ou expirados retornam 410 sem contar acesso. Editar não altera o código nem seu histórico. Não há exclusão para evitar inutilizar material impresso por acidente.

`GET /q/{code}` incrementa a contagem e redireciona com 302 e `Cache-Control: no-store`. Totais são aberturas, incluindo repetições, pré-visualizações e robôs, não visitantes únicos nem reconhecimentos pela câmera. Não são guardados IPs, cookies ou identificadores pessoais. Datas agregadas usam UTC; o formulário de expiração usa o horário local do navegador.

TinyDB usa `ADMIN_DB_PATH` (padrão `data/admin.json`), bloqueio entre processos e substituição atômica. No Docker, `admin_data` persiste em `/app/data`, mesmo com o sistema de arquivos principal somente leitura. Faça backup desse volume com a aplicação parada e restaure no mesmo caminho. Não execute `docker compose down -v` se quiser preservar os dados. A solução é destinada a uma instância com disco local e volume moderado; para várias réplicas em servidores diferentes, migre para um banco servidor.

As gravações administrativas exigem autenticação e um cabeçalho de requisição do painel; CORS não é habilitado. CSV neutraliza prefixos de fórmulas. Destinos aceitam apenas HTTP/HTTPS e não são consultados pelo servidor. A assinatura fica fora da matriz para preservar a leitura: valide um exemplar impresso com o celular antes de produzir um lote.

Testes: `.venv/Scripts/python -m pytest tests/test_admin_pages.py` (Windows).


## Fila de espera e leads

A página pública `/contato` segue a negociação de idioma compartilhada (seleção explícita, preferência salva, país confiável e navegador), nos sete idiomas do site. É acessível pelo menu e pelos links do rodapé e consta no sitemap. O formulário solicita nome e WhatsApp com código do país; e-mail é opcional. O formulário inscreve o contato na fila de espera; a equipe atende pelo WhatsApp assim que possível, sem reserva automática de agenda ou envio de mensagens. A home inclui uma versão compacta do mesmo formulário antes do rodapé. Os registros identificam a origem como `/` ou `/contato`.

`POST /api/contact?lang=...` recebe JSON, valida os campos e grava na tabela `leads` do mesmo `ADMIN_DB_PATH`, preservando `qrcodes`. Cada registro contém nome, telefone normalizado, e-mail, idioma, origem, data UTC e identificador de envio. Repetir o mesmo identificador não duplica o lead. Há limite de tamanho de requisição, verificação de origem e campo invisível contra bots simples; isso não substitui limites de tráfego no proxy para abuso em grande escala. O formulário depende de JavaScript; o contato direto por WhatsApp continua disponível na página.

Em Leads, os contatos aparecem do mais recente ao mais antigo, com pesquisa por nome, telefone ou e-mail e links para WhatsApp/e-mail. A leitura exige a mesma autenticação do admin e não permite cache. Inclua os dados pessoais dos leads na política de acesso e backup do volume. O relatório JSON anterior em `/admin/site-metrics` continua disponível, além da nova interface.

Testes do fluxo: `.venv/Scripts/python -m pytest tests/test_contact.py tests/test_admin_pages.py`.
