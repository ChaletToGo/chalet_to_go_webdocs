# Administração / QR Codes

Abra `/admin` ou `/admin/qrcodes`. Configure `ADMIN_USERNAME` e `ADMIN_PASSWORD` no ambiente: o navegador solicitará as credenciais via HTTP Basic. Sem configuração, o painel fica indisponível (503). Use HTTPS em produção. Feche a sessão do navegador para descartar as credenciais salvas; não há contas individuais ou botão de logout nesta versão.

Configure `QR_BASE_URL` com a origem pública definitiva (ex.: `https://www.chalettogo.com`). Cada código guarda seu endereço permanente no momento da criação. Alterar essa variável só afeta novos códigos: mantenha o domínio antigo funcionando para códigos já impressos. Na execução local, exporte as variáveis no shell ou use `uv run uvicorn app.main:app --env-file .env`; o Compose carrega `.env` automaticamente.

O painel permite criação, pesquisa por nome/campanha, filtro de status, edição de destino, pausa/reativação, expiração opcional, quatro cores, download PNG/SVG com assinatura da marca, cópia do link, exportação CSV e estatísticas diárias dos últimos 30 dias. O histórico diário completo é preservado no banco. Links pausados ou expirados retornam 410 sem contar acesso. Editar não altera o código nem seu histórico. Não há exclusão para evitar inutilizar material impresso por acidente.

`GET /q/{code}` incrementa a contagem e redireciona com 302 e `Cache-Control: no-store`. Totais são aberturas, incluindo repetições, pré-visualizações e robôs, não visitantes únicos nem reconhecimentos pela câmera. Não são guardados IPs, cookies ou identificadores pessoais. Datas agregadas usam UTC; o formulário de expiração usa o horário local do navegador.

TinyDB usa `ADMIN_DB_PATH` (padrão `data/admin.json`), bloqueio entre processos e substituição atômica. No Docker, `admin_data` persiste em `/app/data`, mesmo com o sistema de arquivos principal somente leitura. Faça backup desse volume com a aplicação parada e restaure no mesmo caminho. Não execute `docker compose down -v` se quiser preservar os dados. A solução é destinada a uma instância com disco local e volume moderado; para várias réplicas em servidores diferentes, migre para um banco servidor.

As gravações exigem autenticação e um cabeçalho de requisição do painel; CORS não é habilitado. CSV neutraliza prefixos de fórmulas. Destinos aceitam apenas HTTP/HTTPS e não são consultados pelo servidor. A assinatura fica fora da matriz para preservar a leitura: valide um exemplar impresso com o celular antes de produzir um lote.

Testes: `.venv/Scripts/python -m pytest tests/test_admin_pages.py` (Windows).
