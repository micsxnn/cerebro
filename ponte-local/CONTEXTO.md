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
- Agente **v1.10.0** (commit `0df1b14`, pushed), SKILL.md **3.4.0**.
- **Release v2.7.0 PUBLICADA**: https://github.com/micsxnn/ponte-local/releases/tag/v2.7.0
  (v2.6.0 saiu antes no mesmo dia — lane por máquina, relatório v1.8.0, fix
  spam, spinner/caixa v1.9.0, skill ETag v1.9.1, regra 12).
- **v1.10.0 — RELATÓRIO OBRIGATÓRIO** (causa raiz do "relatório nunca sai":
  sem task_done o lote ficava aberto para sempre e fecharRelatorioAnterior
  nunca mais rodava):
  - pausa longa (padrão 5 min, env `PONTE_TAREFA_GAP_MS`, min 1 s) + comando
    novo = `garantirTarefaPara()` fecha a tarefa anterior SOZINHO via
    `fecharTarefa(null, true)` — relatório com resumo FACTUAL por tipo de
    operação (`resumoAutomatico` + `rotuloAcao`, rótulos PT-BR por ação);
  - Ctrl+C/SIGTERM com tarefa pendente gera relatório ANTES de sair
    (`desligarComRelatorio`, trava `desligando` contra duplo sinal, exit
    após 1,5 s no Linux / 2,5 s no Windows para o open disparar);
  - cabeçalho do relatório ganhou linha "Fechamento:" (pela IA / automático);
  - relatório anterior fecha na tela e txt é apagado quando tarefa nova
    começa; se o open FALHOU, `relatorioEmTela=false` e o txt NÃO é apagado
    (única cópia — caminho no log);
  - **fix de corrida crítico**: o pkill/Stop-Process que fecha a janela
    anterior matava o xdg-open/notepad do relatório NOVO (mesmo padrão
    "relatorio-ponte") → "Sem app de texto disponível". Fix: contador
    `matancaEditor`; `abrirNovo()` só nasce quando `matancaEditor === 0`;
  - gravação do relatório agora atômica (escreveArquivoAtomico); Windows
    ganhou `notepad.exe` como último fallback de open.
- **v1.10.0 — LOGO PONTE AGENTE no boot**: 7 linhas em blocos █/░ com
  reflexo, byte-a-byte IGUAL à arte do usuário (referência em
  `scripts/logo-referencia.txt`; comparado por script). `terminalSuportaLogo()`:
  win32 TTY + release >= 10 (Consolas) → arte; win32 sem TTY, Win7/8, locale
  não-UTF (LC_ALL/LC_CTYPE/LANG), Linux TTY não-UTF → ASCII `P O N T E A G E
  N T E`; Linux non-TTY → arte (UTF-8 em disco); terminal < 65 colunas
  (LOGO_LARGURA=64) → ASCII. `montarBanner({unicode, largura})` é puro e
  testável.
- **v1.9.1 — auto-update da skill otimizado**: ETag/If-None-Match (304 = zero
  bytes, `notModified:true`), escrita atômica, backoff até 15 min, aviso único
  de falha/recuperação. Release v2.6.0 detalha.
- **v1.9.0 — feedback visual no terminal**: spinner `rodando:` + caixa
  `output`; `ativaVTWindows()` com re-leitura do bit (Win7 sem VT → ASCII).
- **SKILL.md 3.4.0**: regra 9 reescrita (relatório inegociável garantido pelo
  agente), seção do relatório com as garantias novas, banner documentado,
  regra 12 (desinstalação TOTAL da skill antes de atualizar) desde a 3.3.0,
  parágrafo duplicado da lane removido.

### Beta
- Tag **v0.1.0-beta.9** enviada (commit `edb3c3e`) — CI construindo AppImage +
  exe; `appVersion = "0.1.0-beta.9"`; agentes (`agente/` e `embedded/`)
  byte-idênticos ao estável v1.10.0 (validado com cmp).
- beta.8 (2814b8c): agente v1.9.1; beta.7: v1.9.0; beta.6: fix do spam;
  beta.5: mensagens 410 + botão "Testar conexão".

### Bancada de testes (scripts/ da sandbox)
- `scripts/testa-relatorio.js` — NOVO, 55 asserts: fatia o código REAL do
  agent.js (marcadores "relatório da tarefa" → "loop principal") com exec
  capturado, plataforma comutável (Proxy) e exit interceptado; cobre resumo da
  IA/automático/falhas/modos, fecharTarefa (sem lote, gravação, open falho →
  preserva txt), garantirTarefaPara (nova/pausa longa), desligarComRelatorio
  (Ctrl+C gerando antes de sair; duplo sinal ignorado), sobras, caminhos
  Windows (powershell/start). Pegadinha: `new Function` não tem require no
  escopo — passar como parâmetros; desligarComRelatorio com stub de process
  via Proxy para interceptar exit.
- `scripts/testa-logo.js` — NOVO, 23 asserts: LOGO === referência byte-a-byte,
  invariantes (7 linhas, só █/░/espaço, 64 col), montarBanner art/ASCII por
  largura e suporte, decisões do terminalSuportaLogo com plataforma/release/
  locale controlados (slice do código real).
- `scripts/testa-e2e-relatorio.py` — NOVO, 25 asserts PTY real: relay fake em
  Python com fila agendada (sleep entre comandos), xdg-open FAKE no PATH
  registrando aberturas, gap curto via env; cobre boot com logo, fechamento
  automático na pausa, open na tela (abertos.log), task_done com resumo,
  fechar+apagar na tarefa nova, Ctrl+C gerando relatório, terminal de 40
  colunas em ASCII. winsize tem que ser aplicado ANTES do boot (openpty +
  ioctl antes do Popen). Rodar ISOLADO de testa-e2e-pty (mesmo relay fake na
  3199 / pasta /tmp/ponte-e2e — agente remanescente rouba comandos e gera
  10 falhas falsas).
- `scripts/testa-skill-update.js` — 39 asserts (ETag/304, atomic, backoff);
  guarda de versão da SKILL.md atualizada para 3.4.0.
- `scripts/testa-tela.js` (37), `testa-e2e-pty.py` (19), `testa-e2e-notty.py`
  (7) — todos verdes com a v1.10.0.
- Teste real contra o GitHub: 1a chamada baixa (200), 2a chamada 304 com
  0 bytes — confirmado no raw de produção.

## Aprendizados que valem ouro

- **URL de preview da plataforma expira**: quando a sessão recicla, a URL
  `*.space-z.ai` antiga responde HTTP 410 e a nova só aparece na interface do
  chat. O usuário precisa copiar a URL nova + token e recolar no painel/agente.
- **Release no repo estável**: POST `/releases` com `target_commitish` +
  `tag_name` novo respondeu 422 ("tag_name is not a valid tag"). Receita que
  funciona: criar tag ANOTADA via git (`git tag -a vX.Y.Z <sha>`, push da
  tag) e depois POST `/releases` SEM `target_commitish` (HTTP 201).
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

- **Usuário**: baixar a beta.9 (agente v1.10.0 com relatório obrigatório e
  logo) ou copiar `agente/agent.js` do estável (release v2.7.0) para
  `~/ponte-agent/agent.js` e religar com `--server URL --token TOKEN --save`.
- **Usuário**: colar a URL nova do preview + token no painel da beta e validar
  com "Testar conexão".
- Conferir a release da beta.9 quando o CI terminar (assets AppImage + exe).
- PAT do GitHub foi revogado; o token vivo atual está no remote do beta (padrão
  já documentado acima).
- Roadmap beta: janela nativa de setup, lixeira/undo no painel, toggle modo deus,
  notificação no Windows.
- Relatório obrigatório no Windows: lógica validada por testes unitários com
  plataforma comutada (powershell/start/notepad) e revisão linha a linha; não
  há Windows na sandbox — primeira execução real no PC do usuário confirma.
- O relatório de tarefa perdida em QUEDA do agente (sem Ctrl+C, sem gap) não é
  reconstruído do ponte-log.jsonl — limite conhecido aceito por agora.

## Regras permanentes do projeto

- Zero emojis em código, docs, commits e releases (emoji só no chat).
- PT-BR informal com o usuário (mano/KKKKK/pô).
- Nunca afirmar ação não executada; nunca inventar estado, token ou URL.
- Commits direto na main, mensagem sem emoji, descrevendo causa e fix.
