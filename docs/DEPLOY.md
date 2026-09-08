# Deploy automático para a VPS

O workflow `.github/workflows/deploy.yml` roda em pushes na `main` e manualmente em **Actions → Deploy production → Run workflow** (selecione `main`). Ele usa SSH nativo do runner, sem Actions de terceiros, e serializa os deploys. Não publica nada apenas por existir localmente: é necessário enviar o workflow ao GitHub e configurar as credenciais.

## Configuração no GitHub

Em **Settings → Environments**, crie o ambiente `production`. Para deploy automático sem confirmação por execução, não configure revisores obrigatórios. Limite as branches de implantação a `main`.

Adicione os seguintes **Environment secrets** (Repository secrets com os mesmos nomes também funcionam):

| Secret | Conteúdo |
| --- | --- |
| `DEPLOY_HOST` | IP público ou hostname SSH da VPS, sem protocolo. Use o endereço direto da VPS, não um domínio com proxy HTTP do Cloudflare. |
| `DEPLOY_USER` | Usuário SSH, por exemplo `rafael`. |
| `DEPLOY_SSH_KEY` | Chave privada SSH completa dedicada ao deploy, sem passphrase, incluindo cabeçalho e rodapé. A chave pública correspondente deve estar em `~/.ssh/authorized_keys` desse usuário na VPS. |
| `DEPLOY_KNOWN_HOSTS` | Linha de `known_hosts` da VPS com chave de host verificada. Para porta personalizada, use `[host]:porta` no campo do host. |

Variáveis opcionais (**Environment variables**):

| Variável | Padrão |
| --- | --- |
| `DEPLOY_PORT` | `22` |
| `DEPLOY_PATH` | `/home/rafael/chalet_to_go_webdocs` |

O caminho precisa ser absoluto, sem espaços. Nenhuma senha de administrador da aplicação vai para o workflow: o `.env` já existente na VPS é utilizado pelo Compose.

Para obter a chave pública de host e conferir a impressão digital, use uma sessão confiável na VPS:

```bash
sudo cat /etc/ssh/ssh_host_ed25519_key.pub
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Monte `DEPLOY_KNOWN_HOSTS` com o host usado em `DEPLOY_HOST`, seguido do tipo e da chave pública exibidos (não copie o comentário final):

```text
IP_DA_VPS ssh-ed25519 CHAVE_PUBLICA_DO_HOST
```

Essa é a chave do **servidor SSH**, diferente da chave de acesso do usuário em `DEPLOY_SSH_KEY`. O workflow exige a verificação da identidade do servidor.

## Pré-requisitos na VPS

- Git, Bash, `flock`, Docker e Compose v2 com suporte a `--wait` e `--wait-timeout`.
- Repositório clonado no caminho configurado, na branch `main`, com `origin` apontando para este projeto e sem arquivos locais modificados ou não rastreados. `.env` e `data/` são ignorados e preservados.
- O usuário SSH precisa conseguir executar `git fetch origin main` sem interação. Para repositório privado, configure uma deploy key de leitura do GitHub na VPS e um remote SSH, com a chave de host do GitHub verificada. As credenciais SSH do runner para a VPS não concedem acesso da VPS ao GitHub.
- O usuário precisa ter acesso ao Docker diretamente ou via `sudo -n docker` sem solicitação de senha. O workflow testa ambos. Acesso ao Docker concede controle privilegiado sobre o servidor; use uma conta de deploy confiável.
- `.env` configurado, incluindo credenciais administrativas, domínio público e porta disponível.
- Rede externa do Compose existente e compartilhada com o Nginx Proxy Manager. O workflow não recria nem reconfigura o proxy ou seus certificados.

Você pode conferir os pré-requisitos dentro da pasta do projeto:

```bash
git branch --show-current
git status --short
git fetch origin main
sudo -n docker compose config --quiet
sudo -n docker compose version
```

Se cartões virtuais ou outros arquivos rastreados foram editados diretamente na VPS, preserve e incorpore essas alterações no repositório antes do primeiro deploy. O workflow para em vez de sobrescrevê-las.

## Comportamento e diagnóstico

O deploy verifica o SHA do push e só atualiza por fast-forward. Execuções antigas são ignoradas quando `main` já avançou. Um bloqueio local adicional impede dois workflows de atualizar o checkout simultaneamente.

A imagem é construída antes da substituição do contêiner. O workflow executa `compose up -d --no-build --wait --wait-timeout 120 web` e confirma `/healthz` dentro do contêiner. Não executa `down`, limpeza de volumes, `git reset` ou `git clean`. O volume `admin_data` e o `.env` são preservados. Arquivos rastreados, incluindo os cartões montados por bind mount, acompanham a atualização do checkout.

Esta primeira versão valida build e saúde da aplicação; não executa a suíte completa de testes nem testa o SSL público do Cloudflare/Nginx. Não há rollback automático: se a nova imagem não ficar saudável, a execução falha e pode ser necessário corrigir a versão. Para reverter código, faça um commit de reversão na `main`, disparando um novo deploy. Mantenha backups separados do banco antes de mudanças de formato de dados.

Logs de diagnóstico são consultados na VPS, evitando publicá-los automaticamente no GitHub:

```bash
sudo docker compose ps
sudo docker compose logs --tail 100 web
```

Referências: [deploys e concorrência no GitHub Actions](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments) e [opções de docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/).
