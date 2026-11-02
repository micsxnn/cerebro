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
- Agente **v1.10.1** (commit `8abd538`, pushed), SKILL.md **3.5.0**.
- Releases hoje: **v2.6.0** (acumulado desde v2.5.2), **v2.7.0** (relatório
  obrigatório + logo), **v2.7.1** (Termux + lane celular).
- **v1.10.0 — RELATÓRIO OBRIGATÓRIO** (causa raiz do "relatório nunca sai":
  sem task_done o lote ficava aberto para sempre e fecharRelatorioAnterior
  nunca mais rodava):
  - pausa longa (padrão 5 min, env `PONTE_TAREFA_GAP_MS`, min 1 s) + comando
    novo = `garantirTarefaPara()` fecha a tarefa anterior SOZINHO via
    `fecharTarefa(null, true)` — relatório com resumo FACTUAL por tipo de
    operação (`resumoAutomatico` + `rotuloAcao`, rótulos PT-BR por ação);
  - Ctrl+C/SIGTERM com tarefa pendente gera relatório ANTES de sair
    (`desligarComRelatorio`, trava `desligando`, exit após 1,5 s Linux /
    2,5 s Windows);
  - relatório anterior fecha na tela e txt é apagado quando a tarefa nova
    começa; open falhou = txt PRESERVADO (única cópia);
  - **fix de corrida crítico**: pkill/Stop-Process da janela anterior matava
    o xdg-open do relatório NOVO → contador `matancaEditor`, open novo só
    nasce com kill zerado;
  - gravação do relatório atômica; Windows ganhou notepad.exe como fallback.
- **v1.10.0 — LOGO PONTE AGENTE no boot**: 7 linhas █/░ byte-a-byte da arte
  do usuário (referência `scripts/logo-referencia.txt`).
  `terminalSuportaLogo()`: win32 TTY + release >= 10 → arte; Win7/8, sem TTY
  (win), locale não-UTF, terminal < 65 colunas → ASCII.
- **v1.10.1 — Termux/Android**: `executaraComando` usava `/bin/bash` fixo —
  o Android NÃO tem /bin. Agora constante `BASH` resolve o primeiro
  candidato existente: /bin/bash, /usr/bin/bash, /usr/local/bin/bash,
  `$PREFIX/bin/bash` (Termux), caminho fixo do Termux, fallback "bash" via
  PATH. Lixeira XDG do agente é fs puro — funciona no Termux sem nada.
- **v1.9.1** ETag/304 + backoff na skill; **v1.9.0** spinner + caixa output.
- **SKILL.md 3.5.0**: seção Termux (instalação, wake-lock, bateria,
  termux-api, ~/storage/shared), regra 9 (relatório inegociável), regra 11
  com 4 lanes, regra 12 (desinstalação total da skill), limites: 4 lanes.

### Relay / app
- **LANE NOVA: `celular`** — `LaneId` + `LANE_IDS` + `LANE_TOKENS`
  (`PONTE_TOKEN_CELULAR` no .env da sandbox) + `lanesPadrao` no store; erro
  de lane inválida agora dinâmico (`LANE_IDS.join("|")`); painel com aba
  Celular. Commit `06e3d0b` na beta; estável recebe no próximo sync de relay.
- **Bug da defesa de HMR no store** (pegou no ar): a defesa só conferia
  netbook/windows/test — estado em memória criado ANTES da lane nova
  sobrevive ao hot-reload do Next e `markSeen("celular")` dava 500. Fix:
  `if (!s.lanes || LANE_IDS.some((id) => !s.lanes[id])) s.lanes =
  lanesPadrao();` — genérica para lanes futuras.
- **O relay RODA no APP PRINCIPAL** (`next dev -p 3000` da plataforma, rotas
  em `src/app/api/ponte/*` + `src/lib/ponte-store.ts` + painel
  `src/app/page.tsx`) — as cópias em `ponte-beta/relay/` são a fonte do
  repo. Editar SEMPRE nos dois (editar repo, cp para src/). Mudanças no
  store/painel recompilam sozinhas (hot reload); `.env` também é relido
  (Next dev re-carrega) — token novo sem restart.
- Auth: agentes via header `x-ponte-token`; admin via `x-ponte-admin`
  (cmd/result-admin) ou `?admin=` (status/results). O POST /cmd COM header
  Bearer NÃO autoriza.
- Ciclo da lane celular testado de ponta a ponta com curl (cmd → poll →
  result) — ok.

### Beta
- Tag **v0.1.0-beta.10** enviada (commit `06e3d0b`) — agente v1.10.1
  embutido + lane celular; beta.9 (edb3c3e): v1.10.0; beta.8: v1.9.1.

### Confirmação em execução real (usuário, 2026-11-03)
- **LOGO PONTE AGENTE: CONFIRMADA pelo usuário** ("abriu lindamente") em
  execução real na máquina dele. Pendente saber terminal/OS exato (Windows?
  netbook Linux?), mas a arte byte-idêntica apareceu como esperado.
- **Relatório obrigatório: ainda SEM confirmação explícita** do usuário em
  execução real (abertura na tela, fechamento/exclusão do txt quando task
  nova entra). Pedir teste: abrir task, aguardar gap ou Ctrl+C e ver o
  relatório abrir.
- **Lane celular: PRIMEIRA CONEXÃO REAL** — agente no Termux deu lastSeen
  no relay, porém o processo parou de fazer poll ~1 min depois do boot
  (Android congela Termux em background; sem `termux-wake-lock` ou sessão
  em primeiro plano). Ping #123 + 1 comando ficaram pendentes na fila —
  serão consumidos no próximo poll quando o usuário reabrir o Termux.
  Lição: NO CELULAR o agente só vive com tela ligada/sessão aberta ou
  wake-lock; esperar desconexões frequentes e fila acumulando (normal).
- **RADAR DE URL PÚBLICA no relay** (commit `b6edbd1` beta, espelhado no
  app vivo): `src/lib/ponte-host.ts` captura `x-forwarded-host` (não-local)
  em status e poll, guarda o ÚLTIMO visto em globalThis e o status-admin
  devolve `hostPublico: {host, proto, haSegundos}`. Motivo: usuário não
  sabe onde achar a URL do preview; ao ABRIR o painel (ou o celular
  conectar), a URL aparece no status e a IA lê com curl. Fontes que NÃO
  deram a URL: /app/zcode-driver (inacessível), env de processos (política).
  Repo beta tem os 3 arquivos espelhados (ponte-host.ts na raiz do relay).

### Bancada de testes (scripts/ da sandbox)
- `scripts/testa-relatorio.js` — 55 asserts (fatia real do agent.js, exec
  capturado, plataforma comutável, exit interceptado).
- `scripts/testa-logo.js` — 23 asserts (LOGO === referência, decisões de
  fallback com plataforma/release/locale controlados).
- `scripts/testa-e2e-relatorio.py` — 25 asserts PTY real (relay fake em
  Python com fila agendada, xdg-open fake no PATH, gap via env, Ctrl+C,
  terminal de 40 colunas em ASCII). winsize ANTES do boot (openpty+ioctl).
  Rodar ISOLADO de testa-e2e-pty (mesmo relay fake na 3199).
- `scripts/testa-skill-update.js` — 39 asserts; guarda de versão 3.5.0.
- `testa-tela.js` (37), `testa-e2e-pty.py` (19), `testa-e2e-notty.py` (7).
- Teste real GitHub: 200 depois 304 com 0 bytes.
- Teste do BASH do Termux: sandbox só prova a presença da lógica (PREFIX +
  caminho fixo) — o caminho real depende do primeiro boot no celular.

## Aprendizados que valem ouro

- **URL de preview da plataforma expira**: quando a sessão recicla, a URL
  `*.space-z.ai` antiga responde HTTP 410 e a nova só aparece na interface do
  chat. O usuário precisa copiar a URL nova + token e recolar no painel/agente.
- **Release no repo estável**: POST `/releases` com `target_commitish` +
  `tag_name` novo respondeu 422 ("tag_name is not a valid tag"). Receita que
  funciona: criar tag ANOTADA via git (`git tag -a vX.Y.Z <sha>`, push da
  tag) e depois POST `/releases` SEM `target_commitish` (HTTP 201).
- **Token da API do GitHub**: o token do remote do ESTÁVEL falhou na API
  (401 Bad credentials) mesmo com push funcionando (credential helper).
  Para chamadas de API, extrair SEMPRE o token do remote da BETA
  (`git config remote.origin.url` dentro de ponte-beta; 40 hex).
- **raw.githubusercontent suporta ETag/304**: `If-None-Match` com o etag da
  resposta anterior → 304 com zero bytes (validado com curl antes de
  implementar).
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

- **Usuário**: instalar o agente no CELULAR (Termux) — bloco de comandos
  entregue no chat; falta só a URL do preview (só ele vê na interface).
- **Usuário**: baixar a beta.10 ou o agent.js da release v2.7.1 para o
  netbook/Windows.
- **Usuário**: colar a URL nova do preview + token no painel da beta e validar
  com "Testar conexão".
- Quando o celular conectar: validar specs no /status (`lanes.celular`) e o
  primeiro run_command real (ex.: termux-battery-status).
- PAT do GitHub revogado; token vivo no remote da BETA (usar para API).
- Roadmap: abrir relatório no Android com termux-open (adicionar à lista do
  abrirNoNavegador quando TERMUX detectado), janela nativa de setup, lixeira/
  undo no painel, toggle modo deus, notificação no Windows.

## Regras permanentes do projeto

- Zero emojis em código, docs, commits e releases (emoji só no chat).
- PT-BR informal com o usuário (mano/KKKKK/pô).
- Nunca afirmar ação não executada; nunca inventar estado, token ou URL.
- Commits direto na main, mensagem sem emoji, descrevendo causa e fix.
