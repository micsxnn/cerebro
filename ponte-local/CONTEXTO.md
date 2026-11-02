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
- Agente **v1.9.1** (commit `f6cfb28`, pushed), SKILL.md **3.3.0**.
- **Release v2.6.0 PUBLICADA** (tag no `f6cfb28`, release id `431958032`):
  https://github.com/micsxnn/ponte-local/releases/tag/v2.6.0 — cobre tudo
  desde a v2.5.2 (agente v1.5.2): relay 1.3.1 lane por máquina, relatório da
  tarefa (v1.8.0), fix do spam (v1.8.1), spinner + caixa output (v1.9.0) e
  otimizações do auto-update (v1.9.1). Notas PT-BR sem emoji.
- **v1.9.1 — auto-update da skill otimizado**: checagem manda ETag da resposta
  anterior (If-None-Match); raw do GitHub responde 304 com ZERO bytes quando
  nada mudou (campo `notModified:true` no `skill_update`, sem reescrita nem
  log). Escrita ATÔMICA do SKILL.md (`.tmp-<pid>` + rename, fallback direto
  se o rename for barrado). Loop trocou setInterval por agenda com backoff
  progressivo em falhas (60 s dobra até teto de 15 min) e aviso ÚNICO de
  falha e de recuperação (fim de spam na rede fora). `pode304` exige etag
  conhecido E arquivo local existente (304 contra arquivo apagado mentiria).
- **v1.9.0 — feedback visual no terminal**: spinner `rodando:` em toda ação
  (braille no Linux, ASCII `|/-\` no Windows) e caixa `output` com
  stdout/stderr/código ao fim de cada run_command. Módulo de tela no agent.js:
  detecção TTY/VT, `spinnerInicio/Fim`, `caixaOutput`, hook no `log()` (limpa
  e redesenha a linha do spinner) e no `processCommand` (spinner para ações de
  arquivo; run_command cuida do próprio, depois do s/N).
- **Windows sem dependências**: `ativaVTWindows()` liga
  ENABLE_VIRTUAL_TERMINAL_PROCESSING via PowerShell + P/Invoke
  (`-EncodedCommand` base64 UTF-16LE, zero dor de quoting) e RE-LÊ o bit antes
  de aceitar (Win7/8 rejeita o flag — sem a re-leitura o agente imprimiria
  lixo). Sem VT: `\r` + padding e caixa ASCII. Sem TTY (redirecionado/app):
  spinner desligado, caixa sai igual.
- `log()` agora escreve via `process.stdout.write` direto — `console.log`
  tratava `%d`/`%s` do output do usuário como formato.
- Bugs pegos nos testes: canto `┐` faltava no mapa de glifos (topo da caixa
  fechava com `┘`), nota "mais N linhas" saía fora da caixa, VT falso-positivo
  no Win7; no teste do auto-update, o fake de servidor só recalculava o etag
  no 200 e respondia 304 mesmo com conteúdo novo (falso-negativo em cascata).
- Bug do spam "Skill atualizada" (v1.8.1): o `versaoDe()` só aceitava o
  marcador `skill-version:` e a comparação com a versão pelada nunca casava —
  regravava e logava a cada 60 s. Fix: aceita versão pelada; igual = silêncio.
- **SKILL.md 3.3.0 — regra 12**: instalar versão nova da skill exige
  DESINSTALAR TOTALMENTE a anterior (pasta inteira, SKILL.md e auxiliares) e
  instalar a nova do zero — nunca sobrescrever por cima (mistura de
  instruções é pior que versão velha inteira); conferência final: só existem
  os arquivos da versão nova e o `skill-version` confere. Reforçada na seção
  "Skill auto-atualizada". Fix adicional: parágrafo da lane por máquina
  estava DUPLICADO no topo — removido.

### Beta
- Tag **v0.1.0-beta.8** enviada (commit `2814b8c`) — CI construindo AppImage +
  exe no momento da checagem (mesma esteira da beta.7, que concluiu com
  sucesso); `appVersion = "0.1.0-beta.8"`; agentes (`agente/` e `embedded/`)
  byte-idênticos ao estável v1.9.1 (validado com cmp).
- beta.7: agente v1.9.0 (spinner + caixa); beta.6: fix do spam; beta.5:
  agente loga falha de conexão (mensagens para HTTP 410) e botão "Testar
  conexão" no painel (`/api/test`: 401 = relay no ar, 410 = preview expirada).

### Bancada de testes (scripts/ da sandbox)
- `scripts/testa-skill-update.js` — NOVO, 39 asserts: fatia o código REAL do
  agent.js entre "function versaoDe" e "function salvarGodMode", roda contra
  servidor HTTP fake com etag recalculado do conteúdo (304/200/500/conexão
  que cai/forçar-200) e valida boot, 304 sem log nem reescrita, atualização
  com seta no log + audit, downgrade ignorado, sem marcador, re-download após
  apagar arquivo, backoff (único aviso de falha, teto, recuperação única) e
  guarda de coerência da regra 12 na SKILL.md. Pegadinha: `new Function` não
  tem `require` no escopo — passar require/globalThis como parâmetros.
- `scripts/testa-tela.js` — 37 asserts unitários (spinner VT/ASCII, caixa
  box-drawing/ASCII, truncamento, OSC, %s/%d, larguras, script VT do Windows).
- `scripts/relay-fake-e2e.js` — relay fake HTTP puro na 3199 (`RELAY_OUT_DIR`
  configura a pasta de saída) com 4 comandos prontos.
- `scripts/testa-e2e-pty.py` — agente REAL dentro de PTY real (`pty` da
  stdlib; o `script -qec` do sandbox pendeu) — 19 asserts de bytes crus.
- `scripts/testa-e2e-notty.py` — agente com stdout em arquivo — 7 asserts
  (sem spinner, caixa intacta).
- Teste real contra o GitHub: 1a chamada baixa (200), 2a chamada 304 com
  0 bytes — confirmado no raw de produção antes do push.

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

- **Usuário**: baixar a beta.8 (agente v1.9.1 com skill otimizada) ou copiar
  `agente/agent.js` do estável (release v2.6.0) para `~/ponte-agent/agent.js`
  e religar com `--server URL --token TOKEN --save`.
- **Usuário**: colar a URL nova do preview + token no painel da beta e validar
  com "Testar conexão".
- Conferir a release da beta.8 quando o CI terminar (assets AppImage + exe).
- PAT do GitHub foi revogado; o token vivo atual está no remote do beta (padrão
  já documentado acima).
- Roadmap beta: janela nativa de setup, lixeira/undo no painel, toggle modo deus,
  notificação no Windows.

## Regras permanentes do projeto

- Zero emojis em código, docs, commits e releases (emoji só no chat).
- PT-BR informal com o usuário (mano/KKKKK/pô).
- Nunca afirmar ação não executada; nunca inventar estado, token ou URL.
- Commits direto na main, mensagem sem emoji, descrevendo causa e fix.
