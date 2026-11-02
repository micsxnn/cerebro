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
- Agente **v1.9.0** (commit `eb147b1`, pushed), SKILL.md **3.2.0**.
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
  no Win7.
- Bug do spam "Skill atualizada" (v1.8.1): o `versaoDe()` só aceitava o
  marcador `skill-version:` e a comparação com a versão pelada nunca casava —
  regravava e logava a cada 60 s. Fix: aceita versão pelada; igual = silêncio.

### Beta
- Tag **v0.1.0-beta.7** enviada (commit `1ba9f3f`) — CI constrói AppImage +
  exe; `appVersion = "0.1.0-beta.7"`; agentes (`agente/` e `embedded/`)
  byte-idênticos ao estável (validado com cmp).
- beta.6: fix do spam; beta.5: agente loga falha de conexão (mensagens para
  HTTP 410) e botão "Testar conexão" no painel (`/api/test`: 401 = relay no
  ar, 410 = preview expirada).

### Bancada de testes (scripts/ da sandbox)
- `scripts/testa-tela.js` — 37 asserts unitários (spinner VT/ASCII, caixa
  box-drawing/ASCII, truncamento, OSC, %s/%d, larguras, script VT do Windows).
- `scripts/relay-fake-e2e.js` — relay fake HTTP puro na 3199 (`RELAY_OUT_DIR`
  configura a pasta de saída) com 4 comandos prontos.
- `scripts/testa-e2e-pty.py` — agente REAL dentro de PTY real (`pty` da
  stdlib; o `script -qec` do sandbox pendeu) — 19 asserts de bytes crus.
- `scripts/testa-e2e-notty.py` — agente com stdout em arquivo — 7 asserts
  (sem spinner, caixa intacta).

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

- **Usuário**: baixar a beta.7 (agente v1.9.0 com spinner + caixa output) ou
  copiar `agente/agent.js` do estável para `~/ponte-agent/agent.js` e religar
  com `--server URL --token TOKEN --save`.
- **Usuário**: colar a URL nova do preview + token no painel da beta e validar
  com "Testar conexão".
- Release notes da beta.7 no GitHub (patch do corpo via API depois do CI, sem
  emoji) — como foi feito na beta.5.
- PAT do GitHub foi revogado; o token vivo atual está no remote do beta (padrão
  já documentado acima).
- Roadmap beta: janela nativa de setup, lixeira/undo no painel, toggle modo deus,
  notificação no Windows.

## Regras permanentes do projeto

- Zero emojis em código, docs, commits e releases (emoji só no chat).
- PT-BR informal com o usuário (mano/KKKKK/pô).
- Nunca afirmar ação não executada; nunca inventar estado, token ou URL.
- Commits direto na main, mensagem sem emoji, descrevendo causa e fix.
