# Ponte Local — contexto do projeto

Atualizado em: 2026-11-03

## O que é

Ponte Local: a IA (Claude, ChatGPT, Gemini) opera o PC do usuário pelo chat com
segurança. Três partes:

- **Relay** Next.js (roda na VM da sandbox, `http://127.0.0.1:3000`) — fila de
  comandos e resultados por lane; painel web em `relay/painel/`.
- **Agente** Node.js de 1 arquivo, zero dependências (Windows/Linux), roda no PC
  do usuário, faz poll no relay e executa ações com whitelist + trava
  anticatástrofe + lixeira com undo.
- **App desktop** (beta) — wrapper Go com o agente embutido, ícone de status e
  painel nativo; empacotado como AppImage (Linux) e exe (Windows) via GitHub
  Actions.

## Repos

| repo | acesso | conteúdo |
|---|---|---|
| `micsxnn/ponte-local` | público (estável) | SKILL.md, relay, `agente/agent.js`, docs |
| `micsxnn/ponte-local-beta` | privado (beta) | o mesmo relay + `desktop/` (app Go) + agente embutido |
| `micsxnn/cerebro` | privado (este repo) | memória persistente entre sandboxes |

Checkouts na sandbox (recriar com clone): `/home/z/my-project/ponte-local-public/`
(estável) e `/home/z/my-project/ponte-beta/` (beta). O remoto de ambos carrega o
token de push embutido na URL (padrão do projeto; PAT original foi revogado — o
token vivo está no remote do beta e na `.env` da sandbox).

## Estado verificado (2026-11-03)

### Estável
- Agente **v1.8.1** (commit `21021cc`, pushed), SKILL.md **3.1.1**.
- **Bug do spam "Skill atualizada" resolvido**: o `versaoDe()` recebia a versão
  pelada (`3.1.1`, retorno de `versaoSkillLocal()`) mas o regex só aceitava o
  marcador `skill-version: X.Y.Z` do arquivo baixado — a comparação nunca casava
  e o agente regravava a SKILL.md e logava "Skill atualizada v3.1.1 → v3.1.1" a
  cada 60 s. Fix: `versaoDe()` aceita também versão pelada (`v?X.Y.Z` sozinha).
  Igual = silêncio; só loga quando `versaoMaisNova(remota, local)` é verdade.

### Beta
- Release **v0.1.0-beta.6** no ar (commit `ccd38ff`, CI verde, AppImage + exe).
- beta.6 = mesmo fix do spam sincronizado em `agente/agent.js` e
  `desktop/embedded/agent.js` + `appVersion = "0.1.0-beta.6"`.
- beta.5 (anterior) trouxe: agente sempre loga falha de conexão (antes ficava
  mudo na primeira falha), mensagens próprias para HTTP 410, e botão "Testar
  conexão" no painel (`/api/test`: 401 = relay no ar, 410 = preview expirada).

## Aprendizados que valem ouro

- **URL de preview da plataforma expira**: quando a sessão recicla, a URL
  `*.space-z.ai` antiga responde HTTP 410 e a nova só aparece na interface do
  chat. O usuário precisa copiar a URL nova + token e recolar no painel/agente.
- Estado do agente no app Go é detectado escaneando linhas do log: "Conectado à
  ponte" / "Conexão caiu" / "Relay inacessível" (pipes em `desktop/agent.go`).
- Repo estável tinha indentação mista (tabs/espaços) → `gofmt -w *.go` já
  normalizado; manter diffs limpos.
- Scanner de emoji próprio: `/home/z/my-project/scripts/varre_emoji.py`
  (ranges unicode; setas → são tipografia, não emoji — ranges 2190–21FF e
  2B00–2BFF ficam de fora).

## Como restaurar o ambiente numa sandbox nova

1. Clonar os repos (token no remote do beta; para o estável usar o mesmo
   token — ver `.env` da sandbox):
   `git clone https://TOKEN@github.com/micsxnn/ponte-local.git ponte-local-public`
   e idem para `ponte-local-beta` em `ponte-beta`.
2. Segredos: `PONTE_ADMIN_TOKEN` do relay em `/home/z/my-project/.env` (não
   copiar valor para cá). Token da lane do usuário em `.env` também.
3. Relay: instalar deps do `ponte-beta/relay/` (Next.js) e rodar dev server;
   status: `curl "http://127.0.0.1:3000/api/ponte/status?admin=$ADMIN"`.
4. Build do desktop (se precisar): Go SDK em `$HOME/go-sdk/go/bin` (go1.23.4),
   `CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -trimpath -ldflags "-s -w"`,
   AppImage via `scripts/monta_appimage.sh`.
5. CI: tag `v*` dispara GitHub Actions (AppImage + exe). Commit direto na main.

## Pendências

- **Usuário**: baixar a beta.6 (ou copiar `agente/agent.js` v1.8.1 do estável
  para `~/ponte-agent/agent.js` e religar com `--server URL --token TOKEN
  --save`) para receber o fix do spam nas máquinas dele.
- **Usuário**: colar a URL nova do preview + token no painel da beta e validar
  com "Testar conexão".
- PAT do GitHub foi revogado; o token vivo atual está no remote do beta (padrão
  já documentado acima).
- Roadmap beta: janela nativa de setup, lixeira/undo no painel, toggle modo deus,
  notificação no Windows.

## Regras permanentes do projeto

- Zero emojis em código, docs, commits e releases (emoji só no chat).
- PT-BR informal com o usuário (mano/KKKKK/pô).
- Nunca afirmar ação não executada; nunca inventar estado, token ou URL.
- Commits direto na main, mensagem sem emoji, descrevendo causa e fix.
