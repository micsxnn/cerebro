# Ponte Local — RevHunter v48 (guia de operação)

Data: 2026-10-31 · Status: **RELAY NO AR E VALIDADO** · Projeto: patch 999 dias (`com.hunter.net`)

## O que é

Canal de operação remota: a IA (sandbox) comanda um relay Next.js público; o **agente**
instalado no **netbook do usuário (CachyOS/Arch, Pentium N3710)** faz poll a cada 1,5 s
e executa comandos. Só sai tráfego do agente (conexões de saída) — zero firewall/porta.

```
netbook (agent.js)  →poll/result→  relay (sandbox)  ←cmd/resultados←  IA (scripts/ponte.py)
```

## Status da instalação (lado da IA) — FEITO

| Item | Estado |
|---|---|
| Relay Next.js 16.4.3 (`/home/z/my-project/ponte-relay`) | no ar, arquivos 100% idênticos à skill |
| `next.config.ts` | `cacheComponents: false` (compatível com `force-dynamic`) |
| Tokens (agent/admin/test) | gerados em `.env.local` (chmod 600; cópia em `rea-work/ponte/`, NUNCA versionar) |
| URL pública | **validada 200** — `preview-chat-<chat_id>.space-z.ai` (status + download do agente) |
| Teste ponta a ponta | agente de teste na VM (canal `test`): `ponte.py ping` → OK (1 ms) |
| Operador | `scripts/ponte.py` (env em `rea-work/ponte/env.sh`) |
| Reerguer relay | `bash scripts/ponte_up.sh` (o sandbox recicla processos entre mensagens; o agente do netbook reconecta sozinho no próximo poll) |

## Instalação no netbook (lado do usuário) — PENDENTE

CachyOS/Arch — cole no terminal do netbook e deixe aberto:

```bash
sudo pacman -S --needed nodejs curl android-tools
mkdir -p ~/ponte-agent && cd ~/ponte-agent
curl -fso agent.js https://preview-chat-<CHAT_ID>.space-z.ai/api/ponte/download
node agent.js --server https://preview-chat-<CHAT_ID>.space-z.ai --token <AGENT_TOKEN_ENVIADO_NO_CHAT> --auto --save
```

- `--auto` = modo autônomo: a IA executa comandos direto (`run_command`), logados como
  `[AUTO] $ cmd`, com a trava anticatástrofe local ativa (recusa fork bomb, mkfs, dd,
  rm em raiz de sistema etc.). A escalada de permissão é sempre física, no terminal dele.
- Token completo: enviado **só no chat privado** — nunca versionar aqui.
- Próximas vezes: `~/ponte-agent/rodar.sh` (relê `ponte.config.json`).
- Painel visual: a própria URL do relay mostra luz âmbar→verde quando o netbook conecta.

## Operação planejada (pós-conexão) — extração do payload LIAPP

1. Validar: `ponte.py ping` + `ponte.py run_command '{"command":"adb version"}'`
2. Celular no cabo + Depuração USB → aceitar RSA no celular → `adb devices`
3. **Pull à prova de bala** (canal binário cru, sem terminal-app, sem scoped storage):
   `adb exec-out run-as com.hunter.net tar -cf - files > /home/<u>/payload.tar` (exige v8 debuggable instalada)
   - alternativo: `adb exec-out run-as com.hunter.net cat 'files/.59bca860/ز֯٬ڲܮ.jar' > liapp_payload.jar`
4. Trazer à VM: `ponte.py pegar <remoto> <local>` (limite 8 MB — o jar tem ~14,6 MB →
   usar `run_command` + curl up, ou dividir em partes < 8 MB, ou `split` + base64 por parte)
5. Parse do dex real (LauncherActivity/Nowin/BaseActivity/trial) → construir v9

Limites da ponte: corpo 1,5 MB · binário base64 8 MB · `run_command` 30 min · resposta 150k chars.

## Falhas anteriores que a ponte elimina

- aShellYou/Shizuku: `cat` de 14,6 MB pelo stream → "Error: Stream closed." → 0 B (≈10 tentativas)
- Scoped storage: app sem permissão de storage → run-as nega TODO `/sdcard` (Download, media, data)
- ADB exec-out no netbook resolve os dois: binário cru por USB + shell root-de-fato (uid shell).
